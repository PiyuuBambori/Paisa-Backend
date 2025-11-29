"""
News Analyzer Agent - Processes market news and sentiment
"""
import google.generativeai as genai
from datetime import datetime
import requests
import json

class NewsAnalyzer:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.system_prompt = """
        You are News Analyzer, a specialized AI agent that processes financial news and market sentiment 
        for the Indian stock market. You work with Ghost Trader to provide news-based insights.
        
        Analyze news sentiment and impact on stock prices. Be objective and factual.
        Rate sentiment as: POSITIVE, NEGATIVE, or NEUTRAL
        Rate impact as: HIGH, MEDIUM, or LOW
        """
    
    def analyze_news_sentiment(self, symbol, news_text):
        """Analyze news sentiment for a specific stock"""
        prompt = f"""
        {self.system_prompt}
        
        Analyze this news for {symbol}:
        "{news_text}"
        
        Provide analysis in this format:
        Sentiment: [POSITIVE/NEGATIVE/NEUTRAL]
        Impact: [HIGH/MEDIUM/LOW]
        Summary: [Brief impact summary in 1 line]
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_news_analysis(response.text, symbol)
        except Exception as e:
            return {
                "symbol": symbol,
                "sentiment": "NEUTRAL",
                "impact": "LOW",
                "summary": "News analysis unavailable",
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_news_analysis(self, response_text, symbol):
        """Parse news analysis response"""
        lines = response_text.strip().split('\n')
        
        sentiment = "NEUTRAL"
        impact = "LOW"
        summary = "News analysis processed"
        
        for line in lines:
            if "Sentiment:" in line:
                sentiment = line.replace("Sentiment:", "").strip()
            elif "Impact:" in line:
                impact = line.replace("Impact:", "").strip()
            elif "Summary:" in line:
                summary = line.replace("Summary:", "").strip()
        
        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "impact": impact,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_market_news(self, symbols=None):
        """Fetch latest market news (placeholder - integrate with news API)"""
        # Placeholder news data - replace with real news API
        mock_news = [
            {
                "headline": "RELIANCE announces major expansion in renewable energy",
                "symbol": "RELIANCE",
                "timestamp": datetime.now().isoformat(),
                "source": "Economic Times"
            },
            {
                "headline": "TCS reports strong Q3 earnings, beats estimates",
                "symbol": "TCS",
                "timestamp": datetime.now().isoformat(),
                "source": "Business Standard"
            }
        ]
        
        return mock_news