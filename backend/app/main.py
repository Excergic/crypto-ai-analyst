from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from fastapi.responses import FileResponse

from .agents.langgraph_workflow import crypto_workflow
from .models.schemas import AnalysisRequest, AnalysisResponse
from .utils.schema_converters import SchemaConverter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto AI Analyst - LangGraph Architecture",
    description="Multi-agent crypto analysis with proper schema separation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Crypto AI Analyst with LangGraph! 🚀",
        "architecture": "dual_schema_approach",
        "features": ["pydantic_validation", "langgraph_workflow", "schema_conversion"]
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def run_analysis(request: AnalysisRequest):
    """Run complete crypto analysis using clean architecture"""
    try:
        logger.info(f"🚀 Starting analysis for {request.num_coins} coins...")
        
        # Convert API request to LangGraph state
        initial_state = SchemaConverter.request_to_langgraph_state(request)
        
        # Execute LangGraph workflow
        final_state = await crypto_workflow.ainvoke(initial_state)
        
        # Convert back to API response
        response = SchemaConverter.langgraph_state_to_response(final_state)
        
        logger.info("✅ Analysis completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/download/report/{filename}")
async def download_report(filename: str):
    """Download generated Excel report"""
    file_path = f"reports/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/download/chart/{filename}")
async def download_chart(filename: str):
    """Download generated chart"""
    file_path = f"reports/charts/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            media_type="image/png",
            filename=filename
        )
    else:
        raise HTTPException(status_code=404, detail="Chart not found")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "architecture": "clean_separation",
        "schemas": {
            "pydantic": "API validation",
            "typeddict": "LangGraph workflow"
        }
    }
