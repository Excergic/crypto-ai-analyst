
import logging
from typing import Dict, Any, List
import statistics
from datetime import datetime

logger = logging.getLogger(__name__)

class AnalysisAgent:
    def __init__(self):
        self.name = "AnalysisAgent"
        
    def analyze_crypto_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform basic crypto market analysis"""
        try:
            logger.info("📊 AnalysisAgent: Starting analysis...")
            
            crypto_data = state.get("crypto_data", [])
            if not crypto_data:
                raise Exception("No crypto data to analyze")
            
            analysis_results = {}
            
            # 1. Market Overview
            analysis_results["market_overview"] = self._analyze_market_overview(crypto_data)
            
            # 2. Price Analysis (if data available)
            if state.get("has_price_changes", False):
                analysis_results["price_trends"] = self._analyze_price_trends(crypto_data)
            else:   
                analysis_results["price_trends"] = {"note": "Price change data not available"}
            
            # 3. Volume Analysis
            analysis_results["volume_analysis"] = self._analyze_volume(crypto_data)
            
            # 4. Top Performers
            analysis_results["top_performers"] = self._find_top_performers(crypto_data)
            
            # Update state
            state["analysis_results"] = analysis_results
            state["analysis_status"] = "completed"
            state["analysis_timestamp"] = datetime.now().isoformat()
            
            logger.info("✅ AnalysisAgent: Analysis completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"❌ AnalysisAgent error: {e}")
            state["analysis_status"] = "failed"
            state["analysis_error"] = str(e)
            return state
    
    def _analyze_market_overview(self, crypto_data: List[Dict]) -> Dict[str, Any]:
        """Calculate basic market statistics"""
        prices = [float(coin["current_price"]) for coin in crypto_data if coin["current_price"]]
        market_caps = [int(coin["market_cap"]) for coin in crypto_data if coin["market_cap"]]
        
        return {
            "total_cryptos_analyzed": len(crypto_data),
            "total_market_cap": sum(market_caps),
            "average_price": statistics.mean(prices) if prices else 0,
            "median_price": statistics.median(prices) if prices else 0,
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0
            }
        }
    
    def _analyze_price_trends(self, crypto_data: List[Dict]) -> Dict[str, Any]:
        """Analyze price change trends"""
        changes_24h = [
            float(coin["price_change_percentage_24h"]) 
            for coin in crypto_data 
            if coin.get("price_change_percentage_24h") is not None
        ]
        
        if not changes_24h:
            return {"note": "No price change data available"}
        
        positive_changes = [c for c in changes_24h if c > 0]
        negative_changes = [c for c in changes_24h if c < 0]
        
        return {
            "average_24h_change": statistics.mean(changes_24h),
            "positive_movers": len(positive_changes),
            "negative_movers": len(negative_changes),
            "strongest_gain": max(changes_24h),
            "biggest_loss": min(changes_24h)
        }
    
    def _analyze_volume(self, crypto_data: List[Dict]) -> Dict[str, Any]:
        """Analyze trading volume"""
        volumes = [int(coin["total_volume"]) for coin in crypto_data if coin["total_volume"]]
        
        if not volumes:
            return {"note": "Volume data not available"}
        
        return {
            "total_volume": sum(volumes),
            "average_volume": statistics.mean(volumes),
            "highest_volume_crypto": max(crypto_data, key=lambda x: x.get("total_volume", 0))["name"]
        }
    
    def _find_top_performers(self, crypto_data: List[Dict]) -> Dict[str, Any]:
        """Find top performing cryptocurrencies"""
        # Sort by market cap
        by_market_cap = sorted(crypto_data, key=lambda x: x.get("market_cap", 0), reverse=True)[:5]
        
        # Sort by 24h change if available
        by_change = []
        if any(coin.get("price_change_percentage_24h") for coin in crypto_data):
            by_change = sorted(
                [coin for coin in crypto_data if coin.get("price_change_percentage_24h")],
                key=lambda x: x["price_change_percentage_24h"],
                reverse=True
            )[:5]
        
        return {
            "top_by_market_cap": [{"name": coin["name"], "market_cap": coin["market_cap"]} for coin in by_market_cap],
            "top_by_24h_change": [
                {"name": coin["name"], "change": coin["price_change_percentage_24h"]} 
                for coin in by_change
            ] if by_change else []
        }

# Create agent instance
analysis_agent = AnalysisAgent()
