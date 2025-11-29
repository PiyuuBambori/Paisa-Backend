"""
Trading Agent - Autonomous AI agent that executes buy/hold/sell decisions
"""
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import random

class TradingAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.system_prompt = """
        You are an autonomous Trading Agent for Ghost Trader. You make BUY/HOLD/SELL decisions 
        based on real-time market analysis, technical indicators, and risk management.
        
        Your responsibilities:
        1. Analyze current market conditions for held stocks
        2. Make HOLD or SELL decisions for existing positions
        3. Provide clear reasoning for each decision
        4. Consider risk management and profit targets
        5. Monitor stop-loss levels and market trends
        
        Always be disciplined, analytical, and focused on protecting capital while maximizing returns.
        """
    
    def analyze_position(self, stock_data):
        """Analyze a position and decide whether to HOLD or SELL"""
        prompt = f"""
        {self.system_prompt}
        
        Analyze this stock position and make a trading decision:
        
        Stock: {stock_data['symbol']}
        Entry Price: ₹{stock_data['entry_price']}
        Current Price: ₹{stock_data['current_price']}
        Quantity: {stock_data['quantity']}
        Days Held: {stock_data['days_held']}
        Current P&L: {stock_data['pnl_percent']:.2f}%
        
        Market Context:
        - Overall market trend: {stock_data.get('market_trend', 'NEUTRAL')}
        - Sector performance: {stock_data.get('sector_performance', 'NEUTRAL')}
        - Volume trend: {stock_data.get('volume_trend', 'NORMAL')}
        
        Provide your decision in this exact format:
        Decision: [HOLD/SELL]
        Confidence: [70-95]%
        Reason: [2-3 lines explaining your decision]
        Target: [If HOLD, mention target price or exit strategy]
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_trading_decision(response.text, stock_data)
        except Exception as e:
            return self._generate_fallback_decision(stock_data)
    
    def _parse_trading_decision(self, response_text, stock_data):
        """Parse AI trading decision"""
        lines = response_text.strip().split('\n')
        
        decision = "HOLD"
        confidence = 75
        reason = "Maintaining position based on current analysis."
        target = ""
        
        for line in lines:
            if "Decision:" in line:
                if "SELL" in line.upper():
                    decision = "SELL"
                else:
                    decision = "HOLD"
            elif "Confidence:" in line:
                try:
                    confidence = int(line.replace("Confidence:", "").replace("%", "").strip())
                except:
                    confidence = 75
            elif "Reason:" in line:
                reason = line.replace("Reason:", "").strip()
            elif "Target:" in line:
                target = line.replace("Target:", "").strip()
        
        return {
            "symbol": stock_data["symbol"],
            "decision": decision,
            "confidence": confidence,
            "reason": reason,
            "target": target,
            "current_price": stock_data["current_price"],
            "pnl_percent": stock_data["pnl_percent"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_fallback_decision(self, stock_data):
        """Generate fallback decision when AI fails"""
        pnl = stock_data["pnl_percent"]
        days_held = stock_data["days_held"]
        
        # Simple rule-based fallback
        if pnl > 15:  # Take profit at 15%
            decision = "SELL"
            reason = "Taking profit at 15% gain. Good risk-reward achieved."
            confidence = 80
        elif pnl < -8:  # Stop loss at -8%
            decision = "SELL"
            reason = "Stop loss triggered. Limiting downside risk."
            confidence = 85
        elif days_held > 90 and pnl > 5:  # Long-term profit taking
            decision = "SELL"
            reason = "Long-term position showing profit. Time to book gains."
            confidence = 75
        else:
            decision = "HOLD"
            reason = "Position within acceptable range. Continuing to monitor."
            confidence = 70
        
        return {
            "symbol": stock_data["symbol"],
            "decision": decision,
            "confidence": confidence,
            "reason": reason,
            "target": "Monitor for 15% gain or -8% stop loss",
            "current_price": stock_data["current_price"],
            "pnl_percent": stock_data["pnl_percent"],
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_buy_order(self, symbol, quantity, price):
        """Simulate buy order execution"""
        # In real implementation, this would connect to broker API
        order = {
            "order_id": f"BUY_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "symbol": symbol,
            "action": "BUY",
            "quantity": quantity,
            "price": price,
            "total_amount": quantity * price,
            "status": "EXECUTED",
            "timestamp": datetime.now().isoformat(),
            "fees": quantity * price * 0.001  # 0.1% fees
        }
        return order
    
    def execute_sell_order(self, symbol, quantity, price):
        """Simulate sell order execution"""
        # In real implementation, this would connect to broker API
        order = {
            "order_id": f"SELL_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "symbol": symbol,
            "action": "SELL",
            "quantity": quantity,
            "price": price,
            "total_amount": quantity * price,
            "status": "EXECUTED",
            "timestamp": datetime.now().isoformat(),
            "fees": quantity * price * 0.001  # 0.1% fees
        }
        return order
    
    def get_portfolio_decisions(self, portfolio_positions):
        """Analyze entire portfolio and make decisions for all positions"""
        decisions = []
        
        for position in portfolio_positions:
            decision = self.analyze_position(position)
            decisions.append(decision)
        
        return decisions