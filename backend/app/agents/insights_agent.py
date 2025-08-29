
import logging
from typing import Dict, Any, List
import openai
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class AIInsightsAgent:
    def __init__(self):
        self.name = "AIInsightsAgent"
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def generate_insights(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights from analysis results"""
        try:
            logger.info("🤖 AIInsightsAgent: Generating insights...")
            
            analysis_results = state.get("analysis_results", {})
            crypto_data = state.get("validated_crypto_data", [])
            
            # Create market summary for AI
            market_summary = self._create_market_summary(analysis_results, crypto_data, state)
            
            # Generate insights using GPT
            prompt = self._create_insights_prompt(market_summary)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional cryptocurrency market analyst. Provide clear, actionable insights based on the data provided."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_insights = response.choices[0].message.content
            
            # Parse insights into structured format
            insights = self._structure_insights(ai_insights)
            
            # Update state
            state["ai_insights"] = insights
            state["insights_status"] = "completed"
            
            logger.info("✅ AI insights generated successfully")
            return state
            
        except Exception as e:
            logger.error(f"❌ AIInsightsAgent error: {e}")
            state["insights_status"] = "failed" 
            state["insights_error"] = str(e)
            
            # Fallback to basic insights
            state["ai_insights"] = self._generate_fallback_insights(state)
            return state
    
    def _create_market_summary(self, analysis_results: Dict, crypto_data: List, state: Dict) -> str:
        """Create a summary of market data for AI processing"""
        market_overview = analysis_results.get("market_overview", {})
        price_trends = analysis_results.get("price_trends", {})
        
        summary = f"""
        Market Analysis Summary:
        - Total cryptocurrencies analyzed: {market_overview.get('total_cryptos_analyzed', 0)}
        - Total market cap: ${market_overview.get('total_market_cap', 0):,.2f}
        - Average price: ${market_overview.get('average_price', 0):,.2f}
        """
        
        if price_trends:
            summary += f"""
        - Average 24h change: {price_trends.get('average_24h_change', 0):.2f}%
        - Positive movers: {price_trends.get('positive_movers', 0)}
        - Negative movers: {price_trends.get('negative_movers', 0)}
        """
        
        # Add top performers
        top_performers = analysis_results.get("top_performers", {}).get("by_market_cap", [])[:3]
        if top_performers:
            summary += "\nTop performers by market cap:\n"
            for coin in top_performers:
                summary += f"- {coin.get('name')}: ${coin.get('market_cap', 0):,.0f}\n"
        
        return summary
    
    def _create_insights_prompt(self, market_summary: str) -> str:
        """Create prompt for AI insights generation"""
        return f"""
        Based on this cryptocurrency market data:

        {market_summary}

        Please provide 3-4 key insights about:
        1. Overall market sentiment
        2. Notable trends or patterns
        3. Investment considerations
        4. Market risks or opportunities

        Keep insights professional, concise, and actionable for investors.
        """
    
    def _structure_insights(self, ai_insights: str) -> List[str]:
        """Structure AI insights into a list"""
        # Split by numbered points or bullet points
        insights = []
        lines = ai_insights.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                # Remove numbering/bullets and add to insights
                clean_line = line.lstrip('0123456789.•- ').strip()
                if clean_line:
                    insights.append(clean_line)
        
        return insights[:4]  # Limit to 4 insights
    
    def _generate_fallback_insights(self, state: Dict) -> List[str]:
        """Generate basic insights if AI fails"""
        analysis_results = state.get("analysis_results", {})
        market_overview = analysis_results.get("market_overview", {})
        price_trends = analysis_results.get("price_trends", {})
        
        insights = [
            f"Market analysis covers {market_overview.get('total_cryptos_analyzed', 0)} cryptocurrencies with total market cap of ${market_overview.get('total_market_cap', 0):,.0f}",
            f"Average cryptocurrency price in this dataset is ${market_overview.get('average_price', 0):,.2f}"
        ]
        
        if price_trends:
            avg_change = price_trends.get('average_24h_change', 0)
            if avg_change > 0:
                insights.append(f"Market shows positive momentum with average 24h change of +{avg_change:.2f}%")
            else:
                insights.append(f"Market shows bearish sentiment with average 24h change of {avg_change:.2f}%")
        
        return insights

# Create agent instance
ai_insights_agent = AIInsightsAgent()
