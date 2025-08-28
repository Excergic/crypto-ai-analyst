import os
import requests
import logging
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class CryptoService:
    def __init__(self):
        self.base_url = os.getenv("COINGECKO_API_URL", "https://api.coingecko.com/api/v3")
        self.session = requests.Session()
        
        # Free tier conservative rate limiting
        self.rate_limit_delay = 2.5  # 2.5 seconds = ~24 calls/min (safe for 30/min limit)
        self.last_request_time = 0

    def _respect_rate_limit(self):
        """Conservative rate limiting for free tier"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            logger.info(f"⏳ Rate limiting: waiting {sleep_time:.1f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def fetch_top_cryptos(self, vs_currency: str = "usd", per_page: int = 10, page: int = 1) -> List[Dict[str, Any]]:
        """Fetch top cryptocurrencies - FREE TIER COMPATIBLE"""
        try:
            self._respect_rate_limit()
            
            url = f"{self.base_url}/coins/markets"
            
            # Minimal parameters for free tier reliability
            params = {
                'vs_currency': vs_currency,
                'order': 'market_cap_desc',
                'per_page': min(per_page, 50),  # Conservative limit
                'page': page,
                'sparkline': False,
                # DON'T request price_change_percentage in free tier
                # 'price_change_percentage': '24h,7d,30d'  # May not work in free tier
            }
            
            logger.info(f"🔍 Fetching {per_page} cryptos (Free Tier)")
            
            response = self.session.get(url, params=params, timeout=30)
            
            # Handle rate limiting aggressively
            if response.status_code == 429:
                logger.warning("⚠️ Rate limit hit! Waiting 2 minutes...")
                time.sleep(120)  # Wait 2 minutes
                response = self.session.get(url, params=params, timeout=30)
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✅ Fetched {len(data)} cryptos successfully")
            return data
            
        except requests.RequestException as e:
            logger.error(f"❌ Error fetching crypto data: {e}")
            raise Exception(f"API Error: {str(e)}")

    def fetch_simple_prices_with_change(self, coin_ids: List[str]) -> Dict[str, Any]:
        """Alternative method to get price changes (FREE TIER)"""
        try:
            self._respect_rate_limit()
            
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': ','.join(coin_ids[:50]),  # Limit for stability
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',  # This usually works in free tier
                'include_24hr_vol': 'true'
            }
            
            logger.info(f"📊 Fetching price changes for {len(coin_ids)} coins")
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"❌ Error fetching price changes: {e}")
            return {}  # Return empty dict instead of crashing

    def get_basic_crypto_data(self, num_coins: int = 10) -> List[Dict[str, Any]]:
        """Get crypto data with fallback for price changes"""
        try:
            # Step 1: Get basic market data
            market_data = self.fetch_top_cryptos(per_page=num_coins)
            
            # Step 2: Try to get price changes separately if not included
            coin_ids = [coin['id'] for coin in market_data[:10]]  # Limit to prevent API overuse
            
            try:
                price_changes = self.fetch_simple_prices_with_change(coin_ids)
                
                # Merge price change data
                for coin in market_data:
                    coin_id = coin['id']
                    if coin_id in price_changes:
                        price_data = price_changes[coin_id]
                        
                        # Add 24h change if available
                        if 'usd_24h_change' in price_data:
                            coin['price_change_percentage_24h'] = price_data['usd_24h_change']
                        
                        # Add volume if available
                        if 'usd_24h_vol' in price_data:
                            coin['total_volume'] = price_data['usd_24h_vol']
                            
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch price changes: {e}")
                # Continue without price changes
                
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Error in get_basic_crypto_data: {e}")
            raise

# Create singleton instance
crypto_service = CryptoService()
