
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, Any, List
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class VisualizationAgent:
    def __init__(self):
        self.name = "VisualizationAgent"
        
    def generate_charts(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization charts from crypto data"""
        try:
            logger.info("📊 VisualizationAgent: Generating charts...")
            
            crypto_data = state.get("validated_crypto_data", [])
            analysis_results = state.get("analysis_results", {})
            
            if not crypto_data:
                raise Exception("No crypto data available for visualization")
            
            # Convert to DataFrame
            df = pd.DataFrame(crypto_data)
            
            # Create charts directory
            os.makedirs("reports/charts", exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            chart_paths = []
            
            # 1. Market Cap Distribution (Bar Chart)
            plt.figure(figsize=(12, 6))
            top_10 = df.nlargest(10, 'market_cap')
            plt.bar(range(len(top_10)), top_10['market_cap'], color='skyblue')
            plt.xticks(range(len(top_10)), top_10['name'], rotation=45, ha='right')
            plt.title('Top 10 Cryptocurrencies by Market Cap')
            plt.ylabel('Market Cap (USD)')
            plt.tight_layout()
            
            chart_path = f"reports/charts/market_cap_distribution_{timestamp}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            chart_paths.append(chart_path)
            plt.close()
            
            # 2. Price Change Distribution (if available)
            if state.get("has_price_changes"):
                price_changes = df[df['price_change_percentage_24h'].notna()]
                if not price_changes.empty:
                    plt.figure(figsize=(10, 6))
                    colors = ['green' if x > 0 else 'red' for x in price_changes['price_change_percentage_24h']]
                    plt.bar(range(len(price_changes)), price_changes['price_change_percentage_24h'], color=colors, alpha=0.7)
                    plt.xticks(range(len(price_changes)), price_changes['symbol'], rotation=45)
                    plt.title('24h Price Changes')
                    plt.ylabel('Price Change (%)')
                    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
                    plt.tight_layout()
                    
                    chart_path = f"reports/charts/price_changes_{timestamp}.png"
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                    chart_paths.append(chart_path)
                    plt.close()
            
            # 3. Market Overview Pie Chart
            market_overview = analysis_results.get("market_overview", {})
            if market_overview:
                plt.figure(figsize=(8, 8))
                # Create pie chart of top 5 by market cap
                top_5 = df.nlargest(5, 'market_cap')
                others_market_cap = df.iloc[5:]['market_cap'].sum()
                
                sizes = list(top_5['market_cap']) + [others_market_cap] if others_market_cap > 0 else list(top_5['market_cap'])
                labels = list(top_5['name']) + ['Others'] if others_market_cap > 0 else list(top_5['name'])
                
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                plt.title('Market Cap Distribution')
                plt.axis('equal')
                
                chart_path = f"reports/charts/market_distribution_{timestamp}.png"
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                chart_paths.append(chart_path)
                plt.close()
            
            # Update state
            state["chart_paths"] = chart_paths
            state["visualization_status"] = "completed"
            
            logger.info(f"✅ Generated {len(chart_paths)} charts")
            return state
            
        except Exception as e:
            logger.error(f"❌ VisualizationAgent error: {e}")
            state["visualization_status"] = "failed"
            state["visualization_error"] = str(e)
            return state

# Create agent instance
visualization_agent = VisualizationAgent()
