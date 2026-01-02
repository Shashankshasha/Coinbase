"""
INTEGRATION: Enhanced Entry System → Beast Mode Bot
This file shows how to integrate the multi-factor scoring into your existing bot
"""

from enhanced_entry_system import MLEnhancedEntrySystem as EnhancedEntrySystem


class SmartAPIManagerEnhanced:
    """
    ENHANCED VERSION with Multi-Factor Scoring Algorithm
    
    Changes from original:
    - Replaced simple pre-filter with 100-point scoring system
    - Added multi-timeframe trend analysis
    - Added support/resistance detection
    - Added market regime detection
    - More accurate confidence scoring
    """
    
    def __init__(self):
        # Keep all original attributes
        self.last_claude_call_time = None
        self.cached_confidence = None
        self.cache_duration_seconds = 300
        self.calls_saved_today = 0
        self.calls_made_today = 0
        
        # NEW: Enhanced entry system
        self.enhanced_entry = EnhancedEntrySystem()
        
        # DIP BUYING SETTINGS (keep from original)
        self.ENABLE_DIP_BUYING = True
        self.DIP_THRESHOLD_PCT = 5.0
        self.DIP_MAX_DROP_PCT = 10.0
        self.DIP_RSI_MAX = 30
        self.DIP_VOLUME_MIN = 1.5
        
        from data_layer.coinbase_client import CoinbaseClient
        self.cb_client = CoinbaseClient()
    
    def should_call_claude_for_entry(self, snapshot: dict, product_id: str = None) -> tuple[bool, str]:
        """
        ENHANCED Pre-filter using Multi-Factor Scoring
        
        Returns (should_call, reason)
        """
        # ================================================================
        # STRATEGY 1: ENHANCED SAFE ENTRY (New Multi-Factor Scoring)
        # ================================================================
        
        print(f"\n🔍 Running Enhanced Entry Analysis...")
        
        analysis = self.enhanced_entry.analyze_entry_opportunity(snapshot, product_id)
        
        # Print detailed breakdown (optional - comment out if too verbose)
        self._print_compact_analysis(analysis)
        
        # Decision based on score
        if analysis['should_enter']:
            return True, f"✅ {analysis['reason']} (Score: {analysis['score']}/100)"
        
        # ================================================================
        # STRATEGY 2: DIP BUYING (Keep original logic as backup)
        # ================================================================
        
        if product_id and self.ENABLE_DIP_BUYING:
            is_dip, dip_reason, drop_pct = self.check_for_dip(snapshot, product_id)
            
            if is_dip:
                return True, f"💰 {dip_reason} - BUY THE DIP!"
        
        # ================================================================
        # NO ENTRY - SKIP CLAUDE CALL
        # ================================================================
        
        self.calls_saved_today += 1
        return False, f"❌ {analysis['reason']}"
    
    def _print_compact_analysis(self, analysis: dict):
        """
        Print compact version of analysis (less verbose than full version)
        """
        print(f"   Score: {analysis['score']}/100 ({analysis['quality']})")
        
        # Show top 2 and bottom 2 factors
        breakdown = analysis['breakdown']
        sorted_factors = sorted(
            breakdown.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        print(f"   Top factors:")
        for factor, data in sorted_factors[:2]:
            pct = (data['score'] / data['max']) * 100
            emoji = "✅" if pct >= 70 else "⚠️" if pct >= 50 else "❌"
            print(f"      {emoji} {factor.replace('_', ' ').title()}: {data['score']}/{data['max']} ({pct:.0f}%)")
        
        if len(sorted_factors) > 2:
            print(f"   Weakest factors:")
            for factor, data in sorted_factors[-2:]:
                pct = (data['score'] / data['max']) * 100
                emoji = "✅" if pct >= 70 else "⚠️" if pct >= 50 else "❌"
                print(f"      {emoji} {factor.replace('_', ' ').title()}: {data['score']}/{data['max']} ({pct:.0f}%)")
    
    def check_for_dip(self, snapshot: dict, product_id: str) -> tuple[bool, str, float]:
        """
        Keep original dip buying logic (unchanged)
        """
        if not self.ENABLE_DIP_BUYING:
            return False, "Dip buying disabled", 0.0
        
        try:
            historical_candles = self.cb_client.get_candles(product_id, "ONE_HOUR", 24)
            
            if not historical_candles or len(historical_candles) < 24:
                return False, "Not enough historical data", 0.0
            
            current_price = snapshot.get('current_price', 0)
            indicators = snapshot.get('indicators', {})
            
            recent_prices = [c['close'] for c in historical_candles[-24:]]
            avg_price = sum(recent_prices) / len(recent_prices)
            
            drop_pct = ((avg_price - current_price) / avg_price) * 100
            
            rsi = indicators.get('rsi', 50)
            volume_ratio = indicators.get('volume_ratio', 0)
            
            is_big_enough_drop = drop_pct >= self.DIP_THRESHOLD_PCT
            is_not_crash = drop_pct < self.DIP_MAX_DROP_PCT
            is_oversold = rsi < self.DIP_RSI_MAX
            is_high_volume = volume_ratio >= self.DIP_VOLUME_MIN
            
            if is_big_enough_drop and is_not_crash and is_oversold and is_high_volume:
                return True, f"DIP DETECTED: {drop_pct:.1f}% drop, RSI {rsi:.0f}, Vol {volume_ratio:.1f}x", drop_pct
            
            if drop_pct >= self.DIP_MAX_DROP_PCT:
                return False, f"Drop too extreme ({drop_pct:.1f}%) - might be crash", drop_pct
            elif drop_pct < self.DIP_THRESHOLD_PCT:
                return False, f"Drop too small ({drop_pct:.1f}% < {self.DIP_THRESHOLD_PCT}%)", drop_pct
            elif rsi >= self.DIP_RSI_MAX:
                return False, f"Not oversold (RSI {rsi:.0f} >= {self.DIP_RSI_MAX})", drop_pct
            elif volume_ratio < self.DIP_VOLUME_MIN:
                return False, f"Volume too low ({volume_ratio:.1f}x < {self.DIP_VOLUME_MIN}x)", drop_pct
            
            return False, "No dip conditions met", drop_pct
            
        except Exception as e:
            print(f"   ⚠️  Error checking dip: {e}")
            return False, "Error getting historical data", 0.0
    
    # Keep all other original methods unchanged
    def record_claude_call(self, confidence: float):
        """Record a Claude API call"""
        from datetime import datetime
        self.last_claude_call_time = datetime.now()
        self.cached_confidence = confidence
        self.calls_made_today += 1
    
    def reset_daily_stats(self):
        """Reset call counters at midnight"""
        from datetime import datetime
        today = datetime.now().date()
        if not hasattr(self, 'last_reset'):
            self.last_reset = today
            return
        
        if today != self.last_reset:
            print(f"\n📊 API Stats (previous day):")
            print(f"   Calls made: {self.calls_made_today}")
            print(f"   Calls saved: {self.calls_saved_today}")
            if self.calls_made_today > 0:
                total = self.calls_made_today + self.calls_saved_today
                efficiency = (self.calls_saved_today / total) * 100
                print(f"   Efficiency: {efficiency:.1f}% reduction")
            
            self.calls_saved_today = 0
            self.calls_made_today = 0
            self.last_reset = today
    
    def check_exit_without_claude(self, current_price: float, entry_data: dict, 
                                  trailing_info: dict = None) -> dict:
        """
        Keep original exit logic (unchanged)
        """
        target_price = entry_data.get('target_price')
        stop_loss_price = entry_data.get('stop_loss_price')
        entry_price = entry_data.get('entry_price')
        
        crypto_amount = entry_data.get('crypto_amount', 0)
        current_value = crypto_amount * current_price
        exit_fee = current_value * 0.012
        exit_revenue = current_value - exit_fee
        entry_cost = entry_data.get('entry_cost', 0)
        current_pnl = exit_revenue - entry_cost
        
        if current_price <= stop_loss_price:
            return {
                'should_exit': True,
                'reason': f'STOP LOSS HIT: £{current_pnl:.2f}',
                'exit_type': 'STOP_LOSS',
                'use_claude': True
            }
        
        if current_price >= target_price:
            if trailing_info and trailing_info.get('active'):
                trailing_stop_price = trailing_info.get('trailing_stop_price')
                
                if current_price <= trailing_stop_price:
                    return {
                        'should_exit': True,
                        'reason': f'TRAILING STOP: £{current_pnl:.2f} profit',
                        'exit_type': 'TRAILING_STOP',
                        'use_claude': True
                    }
                else:
                    return {
                        'should_exit': False,
                        'reason': f'Trailing active, riding trend (£{current_pnl:.2f})',
                        'exit_type': 'HOLDING',
                        'use_claude': False
                    }
            else:
                return {
                    'should_exit': True,
                    'reason': f'TARGET HIT: £{current_pnl:.2f} profit',
                    'exit_type': 'TARGET_HIT',
                    'use_claude': True
                }
        
        return {
            'should_exit': False,
            'reason': f'Holding (P&L: £{current_pnl:.2f})',
            'exit_type': 'HOLDING',
            'use_claude': False
        }