"""
Portfolio Manager Agent - Manages portfolio allocation and risk
"""
from datetime import datetime
import json

class PortfolioManager:
    def __init__(self):
        self.max_position_size = 0.15  # 15% max per position
        self.max_sector_allocation = 0.30  # 30% max per sector
        self.cash_reserve = 0.10  # 10% cash reserve
    
    def calculate_position_size(self, portfolio_value, confidence, risk_level="MEDIUM"):
        """Calculate optimal position size based on confidence and risk"""
        base_allocation = {
            "LOW": 0.05,    # 5%
            "MEDIUM": 0.10, # 10%
            "HIGH": 0.15    # 15%
        }
        
        base_size = base_allocation.get(risk_level, 0.10)
        
        # Adjust based on confidence
        confidence_multiplier = confidence / 100
        position_size = base_size * confidence_multiplier
        
        # Cap at maximum position size
        position_size = min(position_size, self.max_position_size)
        
        return round(position_size * portfolio_value, 2)
    
    def analyze_portfolio_risk(self, positions):
        """Analyze portfolio risk and diversification"""
        if not positions:
            return {
                "risk_level": "LOW",
                "diversification_score": 100,
                "recommendations": ["Start building positions"]
            }
        
        total_value = sum(pos["current_value"] for pos in positions)
        
        # Calculate concentration risk
        max_position_percent = max(pos["current_value"] / total_value for pos in positions) * 100
        
        # Determine risk level
        if max_position_percent > 25:
            risk_level = "HIGH"
        elif max_position_percent > 15:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Calculate diversification score
        num_positions = len(positions)
        diversification_score = min(100, num_positions * 20)  # 20 points per position, max 100
        
        # Generate recommendations
        recommendations = []
        if max_position_percent > 20:
            recommendations.append("Reduce concentration in largest position")
        if num_positions < 5:
            recommendations.append("Consider adding more positions for diversification")
        if diversification_score < 60:
            recommendations.append("Increase portfolio diversification across sectors")
    
        return {
            "risk_level": risk_level,
            "diversification_score": diversification_score,
            "max_position_percent": round(max_position_percent, 2),
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_rebalancing_suggestions(self, positions, target_allocations=None):
        """Generate portfolio rebalancing suggestions"""
        if not positions:
            return []
    
        suggestions = []
        total_value = sum(pos["current_value"] for pos in positions)
    
        for position in positions:
            current_percent = (position["current_value"] / total_value) * 100
    
            # Check for overweight positions
            if current_percent > 20:
                suggestions.append({
                    "symbol": position["symbol"],
                    "action": "REDUCE",
                    "reason": f"Overweight at {current_percent:.1f}%, consider reducing to <20%",
                    "priority": "HIGH"
                })
    
            # Check for underperforming positions
            if position.get("pnl_percent", 0) < -10:
                suggestions.append({
                    "symbol": position["symbol"],
                    "action": "REVIEW",
                    "reason": f"Underperforming at {position.get('pnl_percent', 0):.1f}%",
                    "priority": "MEDIUM"
                })
    
        return suggestions
    
    def calculate_portfolio_metrics(self, positions):
        """Calculate key portfolio metrics"""
        if not positions:
            return {
                "total_value": 0,
                "total_pnl": 0,
                "total_pnl_percent": 0,
                "winning_positions": 0,
                "losing_positions": 0
            }
        
        total_investment = sum(pos.get("investment", 0) for pos in positions)
        total_value = sum(pos.get("current_value", 0) for pos in positions)
        total_pnl = total_value - total_investment
        total_pnl_percent = (total_pnl / total_investment * 100) if total_investment > 0 else 0
        
        winning_positions = len([pos for pos in positions if pos.get("pnl", 0) > 0])
        losing_positions = len([pos for pos in positions if pos.get("pnl", 0) < 0])
        
        return {
            "total_investment": round(total_investment, 2),
            "total_value": round(total_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_percent": round(total_pnl_percent, 2),
            "winning_positions": winning_positions,
            "losing_positions": losing_positions,
            "win_rate": round((winning_positions / len(positions)) * 100, 1) if positions else 0
        }