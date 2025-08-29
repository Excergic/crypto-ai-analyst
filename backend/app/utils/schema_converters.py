from typing import List, Dict, Any
import logging
from datetime import datetime
from ..models.schemas import CryptoData, AnalysisRequest, AnalysisResponse
from ..agents.langgraph_workflow import CryptoAnalysisState

logger = logging.getLogger(__name__)

class SchemaConverter:
    @staticmethod
    def request_to_langgraph_state(request: AnalysisRequest) -> CryptoAnalysisState:
        """Convert API request to LangGraph initial state"""
        return {
            "num_coins": request.num_coins,
            "vs_currency": request.vs_currency,
            "raw_crypto_data": [],
            "validated_crypto_data": [],
            "analysis_results": {},
            "workflow_status": "starting",
            "data_collection_status": "pending",
            "analysis_status": "pending",
            "has_price_changes": False,
            "warnings": [],
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def langgraph_state_to_response(state: CryptoAnalysisState) -> AnalysisResponse:
        """Convert LangGraph final state to API response"""
        status = "success" if state.get("workflow_status") == "completed" else "error"
        
        return AnalysisResponse(
            status=status,
            message=f"LangGraph workflow processed {len(state.get('validated_crypto_data', []))} cryptocurrencies",
            data={
                "analysis_results": state.get("analysis_results", {}),
                "crypto_count": len(state.get("validated_crypto_data", [])),
                "has_price_changes": state.get("has_price_changes", False),
                "workflow_status": state.get("workflow_status", "unknown")
            },
            warnings=state.get("warnings", [])
        )
    
    @staticmethod
    def validate_raw_crypto_data(raw_data: List[Dict[str, Any]]) -> tuple[List[Dict], List[str]]:
        """Validate raw crypto data using Pydantic models"""
        validated_data = []
        validation_errors = []
        
        for item in raw_data:
            try:
                crypto_item = CryptoData(**item)
                validated_data.append(crypto_item.dict())
            except Exception as e:
                validation_errors.append(f"Validation error for {item.get('id', 'unknown')}: {str(e)}")
                continue
                
        return validated_data, validation_errors
