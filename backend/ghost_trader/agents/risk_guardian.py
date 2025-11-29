"""
Risk Guardian Agent - Monitors and manages trading risks
"""
from datetime import datetime, timedelta
import json

class RiskGuardian:
    def __init__(self):
        self.max_daily_loss = 0.05  # 5% max daily loss
        self.max_position_risk = 0.03  # 3% max risk per position
        self.volatility_threshold = 0.25  # 25% volatility threshold
        
    def assess_position_risk(self, symbol, entry_price, current_price, position_size, portfolio_value):
        """Assess risk for a specific position"""
        position_value = position_size * current_price
        position_percent = position_value / portfolio_value
        
        # Calculate unrealized P&L
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Risk assessment
        risk_factors = []
        risk_level = "LOW"
        
        # Position size risk
        if position_percent > 0.20:
            risk_factors.append("Position size exceeds 20% of portfolio")
            risk_level = "HIGH"
        elif position_percent > 0.15:
            risk_factors.append("Position size above recommended 15%")
            risk_level = "MEDIUM"
        
        # Drawdown risk
        if pnl_percent < -10:
            risk_factors.append(f"Position down {abs(pnl_percent):.1f}%")
            risk_level = "HIGH"
        elif pnl_percent < -5:
            risk_factors.append(f"Position down {abs(pnl_percent):.1f}%")
            if risk_level == "LOW":
                risk_level = "MEDIUM"
        
        return {
            "symbol": symbol,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "position_percent": round(position_percent * 100, 2),
            "pnl_percent": round(pnl_percent, 2),
            "recommendations": self._generate_risk_recommendations(risk_level, risk_factors),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_risk_recommendations(self, risk_level, risk_factors):
        """Generate risk management recommendations"""
        recommendations = []
        
        if risk_level == "HIGH":
            recommendations.append("Consider reducing position size immediately")
            recommendations.append("Set tight stop-loss orders")
            recommendations.append("Monitor position closely")
        elif risk_level == "MEDIUM":
            recommendations.append("Review position sizing")
            recommendations.append("Consider setting stop-loss orders")
            recommendations.append("Monitor for further deterioration")
        else:
            recommendations.append("Maintain current risk management")
            recommendations.append("Continue monitoring position")
        
        return recommendations
    
    def check_portfolio_risk_limits(self, positions, daily_pnl=0):
        """Check if portfolio exceeds risk limits"""
        alerts = []
        
        # Daily loss limit check
        if daily_pnl < -self.max_daily_loss:
            alerts.append({
                "type": "DAILY_LOSS_LIMIT",
                "severity": "CRITICAL",
                "message": f"Daily loss of {abs(daily_pnl)*100:.1f}% exceeds {self.max_daily_loss*100}% limit",
                "action": "STOP_TRADING"
            })
        
        # Position concentration check
        if positions:
            total_value = sum(pos.get("current_value", 0) for pos in positions)
            for pos in positions:
                position_percent = pos.get("current_value", 0) / total_value
                if position_percent > 0.25:
                    alerts.append({
                        "type": "CONCENTRATION_RISK",
                        "severity": "HIGH",
                        "message": f"{pos['symbol']} represents {position_percent*100:.1f}% of portfolio",
                        "action": "REDUCE_POSITION"
                    })
        
        return alerts
    
    def calculate_var(self, positions, confidence_level=0.95, time_horizon=1):
        """Calculate Value at Risk (simplified)"""
        if not positions:
            return 0
        
        # Simplified VaR calculation
        # In production, use historical price data and proper statistical methods
        total_value = sum(pos.get("current_value", 0) for pos in positions)
        
        # Assume average volatility of 2% daily for Indian stocks
        daily_volatility = 0.02
        
        # VaR calculation (simplified)
        z_score = 1.645 if confidence_level == 0.95 else 2.33  # 95% or 99%
        var = total_value * daily_volatility * z_score * (time_horizon ** 0.5)
        
        return round(var, 2)
    
    def generate_risk_report(self, positions, portfolio_metrics):
        """Generate comprehensive risk report"""
        total_value = portfolio_metrics.get("total_value", 0)
        total_pnl_percent = portfolio_metrics.get("total_pnl_percent", 0)
        
        # Overall risk assessment
        if total_pnl_percent < -10:
            overall_risk = "HIGH"
        elif total_pnl_percent < -5:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"
        
        # Risk metrics
        var_95 = self.calculate_var(positions, 0.95)
        var_99 = self.calculate_var(positions, 0.99)
        
        # Risk factors
        risk_factors = []
        if len(positions) < 3:
            risk_factors.append("Low diversification - less than 3 positions")
        if total_pnl_percent < -5:
            risk_factors.append(f"Portfolio down {abs(total_pnl_percent):.1f}%")
        
        return {
            "overall_risk": overall_risk,
            "var_95": var_95,
            "var_99": var_99,
            "risk_factors": risk_factors,
            "portfolio_beta": 1.0,  # Placeholder - calculate actual beta
            "sharpe_ratio": 0.0,    # Placeholder - calculate actual Sharpe ratio
            "max_drawdown": abs(min(0, total_pnl_percent)),
            "recommendations": self._generate_portfolio_risk_recommendations(overall_risk, risk_factors),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_portfolio_risk_recommendations(self, risk_level, risk_factors):
        """Generate portfolio-level risk recommendations"""
        recommendations = []
        
        if risk_level == "HIGH":
            recommendations.append("Consider reducing overall exposure")
            recommendations.append("Implement strict stop-loss discipline")
            recommendations.append("Review and rebalance portfolio immediately")
        elif risk_level == "MEDIUM":
            recommendations.append("Monitor positions closely")
            recommendations.append("Consider hedging strategies")
            recommendations.append("Review position sizing")
        else:
            recommendations.append("Maintain current risk management approach")
            recommendations.append("Continue regular portfolio monitoring")
        
        return recommendations