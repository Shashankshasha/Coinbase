from decision_engine.rules import TradingRules
from typing import Dict, List

class DecisionValidator:
    """
    Validates trading decisions against all safety rules.
    """
    
    def __init__(self):
        self.rules = TradingRules()
    
    def validate_trade(
        self,
        action: str,
        product_id: str,
        confidence: float,
        trade_amount: float,
        available_balance: float
    ) -> Dict:
        """
        Validate a trading decision against all rules.
        
        Returns:
            {
                "approved": bool,
                "checks": [{"rule": str, "passed": bool, "reason": str}],
                "summary": str
            }
        """
        checks = []
        
        # 1. Check confidence threshold
        passed, reason = self.rules.check_confidence_threshold(confidence)
        checks.append({"rule": "Confidence Threshold", "passed": passed, "reason": reason})
        
        # 2. Check cooldown period
        passed, reason = self.rules.check_cooldown()
        checks.append({"rule": "Cooldown Period", "passed": passed, "reason": reason})
        
        # 3. Check position limit (for BUY only)
        if action == "BUY":
            passed, reason = self.rules.check_position_limit(product_id)
            checks.append({"rule": "Position Limit", "passed": passed, "reason": reason})
        
        # 4. Check balance (for BUY only)
        if action == "BUY":
            passed, reason = self.rules.check_balance(available_balance, trade_amount)
            checks.append({"rule": "Balance Check", "passed": passed, "reason": reason})
        
        # 5. Check trade amount
        passed, reason = self.rules.check_trade_amount(trade_amount)
        checks.append({"rule": "Trade Amount", "passed": passed, "reason": reason})
        
        # 6. Check trading mode
        passed, reason = self.rules.check_trading_mode(action)
        checks.append({"rule": "Trading Mode", "passed": passed, "reason": reason})
        
        # Determine if approved
        all_passed = all(check["passed"] for check in checks)
        
        # Create summary
        if all_passed:
            summary = f"✅ Trade APPROVED: {action} {product_id} for £{trade_amount:.2f}"
        else:
            failed = [c for c in checks if not c["passed"]]
            reasons = ", ".join([c["reason"] for c in failed])
            summary = f"❌ Trade REJECTED: {reasons}"
        
        return {
            "approved": all_passed,
            "checks": checks,
            "summary": summary
        }
    
    def record_execution(self, product_id: str, action: str, amount: float, price: float):
        """
        Record a successful trade execution.
        """
        self.rules.record_trade(product_id, action, amount, price)
    
    def get_current_position(self, product_id: str) -> dict:
        """
        Get current open position.
        """
        return self.rules.get_position(product_id)
    
    def format_validation_report(self, validation: Dict) -> str:
        """
        Format validation results into readable report.
        """
        report = f"\n{'='*60}\n"
        report += f"DECISION VALIDATION REPORT\n"
        report += f"{'='*60}\n\n"
        
        for check in validation["checks"]:
            status = "✅" if check["passed"] else "❌"
            report += f"{status} {check['rule']}: {check['reason']}\n"
        
        report += f"\n{validation['summary']}\n"
        report += f"{'='*60}\n"
        
        return report