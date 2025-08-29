from langgraph.graph import StateGraph, END, START
from langgraph.graph.state import CompiledStateGraph
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# LangGraph state schema (TypedDict for performance)
class CryptoAnalysisState(TypedDict):
    # Input parameters
    num_coins: int
    vs_currency: str
    
    # Data storage
    raw_crypto_data: List[Dict[str, Any]]
    validated_crypto_data: List[Dict[str, Any]]
    
    # Analysis results
    analysis_results: Dict[str, Any]
    
    # Workflow tracking
    workflow_status: str
    data_collection_status: str
    analysis_status: str
    has_price_changes: bool
    
    # Error handling
    warnings: List[str]
    errors: List[str]
    timestamp: str

def data_collection_node(state: CryptoAnalysisState) -> CryptoAnalysisState:
    """LangGraph node for data collection with Pydantic validation"""
    logger.info("🔍 LangGraph: Data collection node starting...")
    
    try:
        from ..services.crypto_service import crypto_service
        from ..utils.schema_converters import SchemaConverter
        
        # Fetch raw data
        raw_data = crypto_service.get_basic_crypto_data(state["num_coins"])
        
        # Validate using Pydantic models
        validated_data, validation_errors = SchemaConverter.validate_raw_crypto_data(raw_data)
        
        # Update state
        state.update({
            "raw_crypto_data": raw_data,
            "validated_crypto_data": validated_data,
            "data_collection_status": "completed",
            "has_price_changes": any(
                crypto.get("price_change_percentage_24h") is not None 
                for crypto in validated_data
            ),
            "timestamp": datetime.now().isoformat()
        })
        
        # Add warnings for validation errors
        if validation_errors:
            state["warnings"].extend(validation_errors)
        
        if not validated_data:
            state["data_collection_status"] = "failed"
            state["errors"].append("No valid crypto data after validation")
        
        logger.info(f"✅ Data collection completed: {len(validated_data)} cryptos validated")
        return state
        
    except Exception as e:
        logger.error(f"❌ Data collection failed: {e}")
        state.update({
            "data_collection_status": "failed",
            "errors": [str(e)],
            "timestamp": datetime.now().isoformat()
        })
        return state

def analysis_node(state: CryptoAnalysisState) -> CryptoAnalysisState:
    """LangGraph node for analysis"""
    logger.info("📊 LangGraph: Analysis node starting...")
    
    try:
        crypto_data = state["validated_crypto_data"]
        
        if not crypto_data:
            raise Exception("No validated crypto data available for analysis")
        
        # Perform analysis
        analysis_results = {
            "market_overview": {
                "total_cryptos_analyzed": len(crypto_data),
                "total_market_cap": sum(crypto.get("market_cap", 0) for crypto in crypto_data),
                "average_price": sum(crypto.get("current_price", 0) for crypto in crypto_data) / len(crypto_data)
            },
            "top_performers": {
                "by_market_cap": sorted(crypto_data, key=lambda x: x.get("market_cap", 0), reverse=True)[:5]
            }
        }
        
        # Add price analysis if available
        if state["has_price_changes"]:
            price_changes = [
                crypto.get("price_change_percentage_24h", 0) 
                for crypto in crypto_data 
                if crypto.get("price_change_percentage_24h") is not None
            ]
            
            if price_changes:
                analysis_results["price_trends"] = {
                    "average_24h_change": sum(price_changes) / len(price_changes),
                    "positive_movers": len([c for c in price_changes if c > 0]),
                    "negative_movers": len([c for c in price_changes if c < 0])
                }
        
        # Update state
        state.update({
            "analysis_results": analysis_results,
            "analysis_status": "completed",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info("✅ Analysis completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        state.update({
            "analysis_status": "failed",
            "errors": [str(e)],
            "timestamp": datetime.now().isoformat()
        })
        return state

def error_handling_node(state: CryptoAnalysisState) -> CryptoAnalysisState:
    """Handle errors gracefully"""
    logger.warning("⚠️ LangGraph: Error handling node activated")
    
    state.update({
        "workflow_status": "completed_with_errors",
        "timestamp": datetime.now().isoformat()
    })
    
    if not state.get("warnings"):
        state["warnings"] = []
    state["warnings"].append("Workflow completed with errors - check logs")
    
    return state

# Conditional routing functions
def should_continue_to_analysis(state: CryptoAnalysisState) -> str:
    """Route based on data collection success"""
    if state.get("data_collection_status") == "completed":
        return "analysis"
    else:
        return "error_handler"

def check_workflow_completion(state: CryptoAnalysisState) -> str:
    """Route based on analysis success"""
    if state.get("analysis_status") == "completed":
        # Mark workflow as completed
        state["workflow_status"] = "completed"
        return END
    else:
        return "error_handler"

def create_crypto_analysis_workflow() -> CompiledStateGraph:
    """Create and compile the LangGraph workflow"""
    
    workflow = StateGraph(CryptoAnalysisState)
    
    # Add nodes
    workflow.add_node("data_collection", data_collection_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("error_handler", error_handling_node)
    
    # Add edges
    workflow.add_edge(START, "data_collection")
    
    workflow.add_conditional_edges(
        "data_collection",
        should_continue_to_analysis,
        {
            "analysis": "analysis",
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_conditional_edges(
        "analysis",
        check_workflow_completion,
        {
            END: END,
            "error_handler": "error_handler"
        }
    )
    
    workflow.add_edge("error_handler", END)
    
    compiled_workflow = workflow.compile()
    logger.info("🚀 LangGraph workflow compiled successfully")
    
    return compiled_workflow

# Create the workflow instance
crypto_workflow = create_crypto_analysis_workflow()
