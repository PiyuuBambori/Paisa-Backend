"""
Ghost Trader Service
Main service class that handles all Ghost Trader functionality
"""

from flask import jsonify
import google.generativeai as genai
import os
from datetime import datetime, timedelta
import json
import random
from dotenv import load_dotenv

# Import Ghost Trader agents
from .agents.news_analyzer import NewsAnalyzer
from .agents.portfolio_manager import PortfolioManager
from .agents.risk_guardian import RiskGuardian
from .agents.trading_agent import TradingAgent

load_dotenv()

class GhostTraderService:
    def __init__(self):
        # Initialize AI model
        api_key = os.getenv('GEMINI_API_KEY', 'API KEY HERE')
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Initialize agents
        self.news_analyzer = NewsAnalyzer(api_key)
        self.portfolio_manager = PortfolioManager()
        self.risk_guardian = RiskGuardian()
        self.trading_agent = TradingAgent(api_key)
        
        # System prompt for stock recommendations
        self.system_prompt = """
        You are Ghost Trader, an elite stock recommendation AI for Indian markets (NSE & BSE). 
        You analyze market trends, technical indicators, sector performance, and economic factors to recommend 
        the best performing stocks. You operate with machine precision and provide data-driven recommendations.
        
        Your role is to:
        1. Identify high-potential stocks based on current market trends
        2. Analyze sector rotation and momentum
        3. Consider fundamental and technical factors
        4. Provide clear BUY recommendations with reasoning
        5. Assign confidence scores based on analysis depth
        
        Always be analytical, precise, and focused on performance potential.
        Never use hype or emotion. Base recommendations on solid market analysis.
        """
    
    def get_recommendations(self):
        """Get top stock recommendations"""
        try:
            recommendations = self._get_ai_recommendations()
            
            return jsonify({
                "recommendations": recommendations,
                "total_count": len(recommendations),
                "timestamp": datetime.now().isoformat(),
                "market_status": "OPEN" if 9 <= datetime.now().hour < 16 else "CLOSED"
            })
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return jsonify({"error": "Failed to get recommendations"}), 500
    
    def get_market_overview(self):
        """Get market overview and trends"""
        try:
            recommendations = self._get_ai_recommendations()
            
            # Analyze sectors from recommendations
            sectors = {}
            for rec in recommendations:
                sector = rec.get("sector", "Others")
                if sector not in sectors:
                    sectors[sector] = {"count": 0, "avg_confidence": 0}
                sectors[sector]["count"] += 1
                sectors[sector]["avg_confidence"] += rec.get("confidence", 75)
            
            # Calculate average confidence per sector
            for sector in sectors:
                sectors[sector]["avg_confidence"] = round(sectors[sector]["avg_confidence"] / sectors[sector]["count"])
            
            overview = {
                "total_recommendations": len(recommendations),
                "avg_confidence": round(sum(r.get("confidence", 75) for r in recommendations) / len(recommendations)) if recommendations else 0,
                "top_sectors": dict(sorted(sectors.items(), key=lambda x: x[1]["count"], reverse=True)[:5]),
                "market_trend": "BULLISH" if len(recommendations) > 6 else "NEUTRAL",
                "timestamp": datetime.now().isoformat()
            }
            
            return jsonify(overview)
        except Exception as e:
            print(f"Error getting market overview: {e}")
            return jsonify({"error": "Failed to get market overview"}), 500
    
    def get_signals(self):
        """Get recent trading signals"""
        try:
            # Generate recent signals based on recommendations
            recommendations = self._get_ai_recommendations()
            
            signals = []
            for i, rec in enumerate(recommendations[:3]):  # Top 3 as recent signals
                signal = {
                    "id": str(i + 1),
                    "symbol": rec["symbol"],
                    "signal": rec["recommendation"],
                    "confidence": rec["confidence"],
                    "reason": rec["reason"],
                    "timestamp": datetime.now().isoformat(),
                    "target_price": rec.get("target_price", 0),
                    "stop_loss": rec.get("target_price", 0) * 0.9 if rec.get("target_price") else 0,
                    "timeframe": "1-2 weeks"
                }
                signals.append(signal)
            
            return jsonify(signals)
        except Exception as e:
            print(f"Error getting signals: {e}")
            return jsonify({"error": "Failed to get signals"}), 500
    
    def get_portfolio(self):
        """Get portfolio analysis"""
        try:
            # Use portfolio manager to generate portfolio data
            portfolio_data = self.portfolio_manager.calculate_portfolio_metrics([
                {
                    "symbol": "RELIANCE",
                    "investment": 121000,
                    "current_value": 122837.50,
                    "pnl": 1837.50
                },
                {
                    "symbol": "TCS",
                    "investment": 95500,
                    "current_value": 94730,
                    "pnl": -770
                },
                {
                    "symbol": "HDFC BANK",
                    "investment": 129000,
                    "current_value": 125917.50,
                    "pnl": -3082.50
                }
            ])
            
            portfolio = {
                "positions": [
                    {
                        "symbol": "RELIANCE",
                        "quantity": 50,
                        "avg_price": 2420.00,
                        "current_price": 2456.75,
                        "pnl": 1837.50,
                        "pnl_percent": 1.52
                    },
                    {
                        "symbol": "TCS",
                        "quantity": 25,
                        "avg_price": 3820.00,
                        "current_price": 3789.20,
                        "pnl": -770.00,
                        "pnl_percent": -0.81
                    },
                    {
                        "symbol": "HDFC BANK",
                        "quantity": 75,
                        "avg_price": 1720.00,
                        "current_price": 1678.90,
                        "pnl": -3082.50,
                        "pnl_percent": -2.39
                    }
                ],
                **portfolio_data
            }
            
            return jsonify(portfolio)
        except Exception as e:
            print(f"Error getting portfolio: {e}")
            return jsonify({"error": "Failed to get portfolio"}), 500
    
    def health_check(self):
        """Health check endpoint"""
        return jsonify({
            "status": "Ghost Trader operational",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "agents": {
                "news_analyzer": "active",
                "portfolio_manager": "active", 
                "risk_guardian": "active"
            }
        })
    
    def _get_ai_recommendations(self):
        """Get AI-powered stock recommendations"""
        prompt = f"""
        {self.system_prompt}
        
        Based on current Indian market trends, sector performance, and technical analysis, 
        recommend the TOP 8 stocks from NSE/BSE that have the highest potential for good returns.
        
        Consider:
        - Current market momentum and trends
        - Sector rotation patterns
        - Technical breakouts and support levels
        - Fundamental strength
        - Recent news and developments
        
        Provide recommendations in this exact format for each stock:
        
        Stock: [SYMBOL]
        Sector: [Sector Name]
        Recommendation: BUY
        Target: [Price Target]
        Confidence: [70-95]%
        Reason: [2-3 lines explaining why this stock will perform well]
        
        Focus on stocks with strong momentum and growth potential.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_recommendations(response.text)
        except Exception as e:
            print(f"AI recommendation error: {e}")
            return self._generate_fallback_recommendations()
    
    def _parse_recommendations(self, response_text):
        """Parse AI recommendations into structured data"""
        recommendations = []
        lines = response_text.strip().split('\n')
        
        current_stock = {}
        for line in lines:
            line = line.strip()
            if line.startswith("Stock:"):
                if current_stock:
                    recommendations.append(current_stock)
                current_stock = {
                    "symbol": line.replace("Stock:", "").strip(),
                    "sector": "",
                    "recommendation": "BUY",
                    "target_price": 0,
                    "confidence": 75,
                    "reason": "",
                    "timestamp": datetime.now().isoformat()
                }
            elif line.startswith("Sector:"):
                current_stock["sector"] = line.replace("Sector:", "").strip()
            elif line.startswith("Target:"):
                try:
                    target_str = line.replace("Target:", "").replace("₹", "").replace(",", "").strip()
                    current_stock["target_price"] = float(target_str)
                except:
                    current_stock["target_price"] = 0
            elif line.startswith("Confidence:"):
                try:
                    conf_str = line.replace("Confidence:", "").replace("%", "").strip()
                    current_stock["confidence"] = int(conf_str)
                except:
                    current_stock["confidence"] = 75
            elif line.startswith("Reason:"):
                current_stock["reason"] = line.replace("Reason:", "").strip()
        
        if current_stock:
            recommendations.append(current_stock)
        
        return recommendations[:8]  # Return top 8 recommendations
    
    def _generate_fallback_recommendations(self):
        """Generate fallback recommendations when AI fails"""
        fallback_stocks = [
            {
                "symbol": "RELIANCE",
                "sector": "Oil & Gas",
                "recommendation": "BUY",
                "target_price": 2650,
                "confidence": 82,
                "reason": "Strong fundamentals with diversified business model. Retail and digital expansion driving growth.",
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "TCS",
                "sector": "IT Services",
                "recommendation": "BUY", 
                "target_price": 4200,
                "confidence": 85,
                "reason": "Leading IT services company with strong client base. Digital transformation trends favorable.",
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "HDFC BANK",
                "sector": "Banking",
                "recommendation": "BUY",
                "target_price": 1850,
                "confidence": 80,
                "reason": "Largest private bank with consistent growth. Strong asset quality and digital banking initiatives.",
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "INFY",
                "sector": "IT Services", 
                "recommendation": "BUY",
                "target_price": 1650,
                "confidence": 78,
                "reason": "Strong order book and margin expansion. Cloud and digital services driving revenue growth.",
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "ICICI BANK",
                "sector": "Banking",
                "recommendation": "BUY",
                "target_price": 1350,
                "confidence": 79,
                "reason": "Improved asset quality and strong retail franchise. Digital banking leadership position.",
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "BHARTIARTL",
                "sector": "Telecom",
                "recommendation": "BUY",
                "target_price": 1200,
                "confidence": 76,
                "reason": "5G rollout and ARPU improvement potential. Market leadership in telecom sector.",
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "ITC",
                "sector": "FMCG",
                "recommendation": "BUY",
                "target_price": 520,
                "confidence": 74,
                "reason": "Diversified FMCG portfolio with strong brands. ESG initiatives and premiumization strategy.",
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "HCLTECH",
                "sector": "IT Services",
                "recommendation": "BUY",
                "target_price": 1850,
                "confidence": 77,
                "reason": "Strong engineering services and product portfolio. Mode 2 and Mode 3 services gaining traction.",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        return fallback_stocks
    
    def buy_stock(self, symbol, quantity, price):
        """Execute buy order for a stock"""
        try:
            # Execute buy order through trading agent
            order = self.trading_agent.execute_buy_order(symbol, quantity, price)
            
            # In real implementation, save to database
            # For now, return order confirmation
            return jsonify({
                "status": "success",
                "message": f"Successfully bought {quantity} shares of {symbol}",
                "order": order
            })
        except Exception as e:
            print(f"Error buying stock: {e}")
            return jsonify({"error": "Failed to execute buy order"}), 500
    
    def get_trading_decisions(self):
        """Get AI trading decisions for current portfolio"""
        try:
            # Simulate current portfolio positions
            portfolio_positions = [
                {
                    "symbol": "RELIANCE",
                    "entry_price": 2420,
                    "current_price": 2456 + random.randint(-50, 50),
                    "quantity": 50,
                    "days_held": 15,
                    "pnl_percent": ((2456 - 2420) / 2420) * 100,
                    "market_trend": "BULLISH",
                    "sector_performance": "POSITIVE",
                    "volume_trend": "HIGH"
                },
                {
                    "symbol": "TCS",
                    "entry_price": 3820,
                    "current_price": 3789 + random.randint(-100, 100),
                    "quantity": 25,
                    "days_held": 32,
                    "pnl_percent": ((3789 - 3820) / 3820) * 100,
                    "market_trend": "NEUTRAL",
                    "sector_performance": "STABLE",
                    "volume_trend": "NORMAL"
                },
                {
                    "symbol": "HDFC BANK",
                    "entry_price": 1720,
                    "current_price": 1678 + random.randint(-30, 30),
                    "quantity": 75,
                    "days_held": 8,
                    "pnl_percent": ((1678 - 1720) / 1720) * 100,
                    "market_trend": "BULLISH",
                    "sector_performance": "RECOVERING",
                    "volume_trend": "HIGH"
                }
            ]
            
            # Get AI decisions for all positions
            decisions = self.trading_agent.get_portfolio_decisions(portfolio_positions)
            
            return jsonify({
                "decisions": decisions,
                "total_positions": len(decisions),
                "timestamp": datetime.now().isoformat(),
                "next_analysis": (datetime.now() + timedelta(hours=1)).isoformat()
            })
        except Exception as e:
            print(f"Error getting trading decisions: {e}")
            return jsonify({"error": "Failed to get trading decisions"}), 500
    
    def execute_ai_trades(self):
        """Execute AI-recommended trades automatically"""
        try:
            # Simulate getting trading decisions directly
            portfolio_positions = [
                {
                    "symbol": "RELIANCE",
                    "entry_price": 2420,
                    "current_price": 2456 + random.randint(-50, 50),
                    "quantity": 50,
                    "days_held": 15,
                    "pnl_percent": ((2456 - 2420) / 2420) * 100,
                    "market_trend": "BULLISH",
                    "sector_performance": "POSITIVE",
                    "volume_trend": "HIGH"
                },
                {
                    "symbol": "TCS",
                    "entry_price": 3820,
                    "current_price": 3789 + random.randint(-100, 100),
                    "quantity": 25,
                    "days_held": 32,
                    "pnl_percent": ((3789 - 3820) / 3820) * 100,
                    "market_trend": "NEUTRAL",
                    "sector_performance": "STABLE",
                    "volume_trend": "NORMAL"
                }
            ]
            
            # Get AI decisions for all positions
            decisions = self.trading_agent.get_portfolio_decisions(portfolio_positions)
            
            executed_trades = []
            
            for decision in decisions:
                if decision["decision"] == "SELL" and decision["confidence"] >= 80:
                    # Execute sell order
                    sell_order = self.trading_agent.execute_sell_order(
                        decision["symbol"], 
                        50,  # Simulate quantity
                        decision["current_price"]
                    )
                    executed_trades.append(sell_order)
            
            return jsonify({
                "status": "success",
                "executed_trades": executed_trades,
                "total_trades": len(executed_trades),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error executing AI trades: {e}")
            return jsonify({"error": "Failed to execute AI trades"}), 500