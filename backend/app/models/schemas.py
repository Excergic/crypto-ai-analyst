from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class CryptoData(BaseModel):
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: Optional[int] = 0  # Can be null in free tier
    market_cap_rank: Optional[int] = 0
    total_volume: Optional[int] = 0
    
    # These might not be available in free tier
    price_change_percentage_24h: Optional[float] = None
    price_change_percentage_7d: Optional[float] = None
    price_change_percentage_30d: Optional[float] = None
    
    # Additional safety fields
    image: Optional[str] = None  # Coin image URL
    last_updated: Optional[str] = None  # When data was last updated

class AnalysisState(BaseModel):
    crypto_data: List[CryptoData] = []
    analysis_results: Dict[str, Any] = {}
    report_path: Optional[str] = None
    insights: List[str] = []
    timestamp: datetime = datetime.now()
    
    # Track data quality for free tier
    data_source: str = "free_tier"
    has_price_changes: bool = False

class AnalysisRequest(BaseModel):
    num_coins: int = 10  # Keep conservative for free tier
    vs_currency: str = "usd"

class AnalysisResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    warnings: List[str] = []  # For free tier limitations
