from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class CryptoData(BaseModel):
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: int
    market_cap_rank: int
    total_volume: int
    price_change_percentage_24h: Optional[float]
    price_change_percentage_7d: Optional[float]
    price_change_percentage_30d: Optional[float]

class AnalysisState(BaseModel):
    crypto_data: List[CryptoData] = []
    analysis_results: Dict[str, Any] = {}
    report_path: Optional[str] = None
    insights: List[str] = []
    timestamp: datetime = datetime.now()

class AnalysisRequest(BaseModel):
    num_coins: int = 10
    vs_currency: str = "usd"

class AnalysisResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
