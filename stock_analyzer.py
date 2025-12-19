import pandas as pd
import numpy as np
from typing import Dict, List, Any
import yfinance as yf
from datetime import datetime, timedelta
from modules.fundamental_indicators import FundamentalIndicators

class StockAnalyzer:
    def __init__(self):
        self.buffett_criteria = self._initialize_buffett_criteria()
        self.fundamental_indicators = FundamentalIndicators()
    
    def _initialize_buffett_criteria(self):
        """Initialize the 16-point Buffett criteria"""
        return [
            {
                'name': 'Return on Equity (ROE)',
                'key': 'roe',
                'criteria': '> 15% = Good, < 10% = Avoid',
                'good_threshold': 15,
                'bad_threshold': 10
            },
            {
                'name': 'Debt-to-Equity Ratio',
                'key': 'debt_to_equity',
                'criteria': '< 0.5 = Excellent, 0.5-1 = Okay, > 1 = Avoid',
                'excellent_threshold': 0.5,
                'avoid_threshold': 1.0
            },
            {
                'name': 'Current Ratio',
                'key': 'current_ratio',
                'criteria': '> 1.5 = Healthy, < 1 = Risky',
                'good_threshold': 1.5,
                'bad_threshold': 1.0
            },
            {
                'name': 'Book Value Per Share',
                'key': 'book_value_check',
                'criteria': 'Stock Price < Book Value',
                'comparison': 'price_vs_book'
            },
            {
                'name': 'Price-to-Earnings (P/E) Ratio',
                'key': 'pe_ratio',
                'criteria': '10-15 = Fair, 15-25 = Okay, > 25 = Expensive',
                'fair_min': 10,
                'fair_max': 15,
                'okay_max': 25
            },
            {
                'name': 'Price-to-Book (P/B) Ratio',
                'key': 'pb_ratio',
                'criteria': '< 1.5 = Undervalued',
                'good_threshold': 1.5
            },
            {
                'name': 'Intrinsic Value vs Market Price',
                'key': 'intrinsic_value_check',
                'criteria': 'MoS ≥ 20% (IV=Intrinsic Value via DCF, MoS=Margin of Safety)',
                'discount_threshold': 20
            },
            {
                'name': 'Operating Profit Margin (OPM)',
                'key': 'operating_margin',
                'criteria': '> 15% and stable',
                'good_threshold': 15
            },
            {
                'name': 'Revenue vs Profit Growth',
                'key': 'growth_alignment',
                'criteria': 'Both positive (5-year CAGR or YoY)',
                'alignment_threshold': 0.8
            },
            {
                'name': 'Return on Capital Employed (ROCE)',
                'key': 'roce',
                'criteria': '> 15%',
                'good_threshold': 15
            },
            {
                'name': 'PEG Ratio',
                'key': 'peg_ratio',
                'criteria': '< 1.0',
                'good_threshold': 1.0
            },
            {
                'name': 'Earnings Growth',
                'key': 'earnings_growth',
                'criteria': '> 8-10% CAGR',
                'good_threshold': 8
            },
            {
                'name': 'Consistent Earnings',
                'key': 'earnings_consistency',
                'criteria': 'Net Income stable over 5-10 years',
                'volatility_threshold': 0.3
            },
            {
                'name': 'Free Cash Flow',
                'key': 'free_cash_flow',
                'criteria': 'Positive & growing over 5 years',
                'growth_threshold': 0
            },
            {
                'name': 'Dividend History',
                'key': 'dividend_history',
                'criteria': 'Dividend paid last 5 years (bonus)',
                'years_threshold': 3
            }
        ]
    
    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complete Buffett analysis on a stock"""
        
        # Calculate derived metrics
        derived_metrics = self._calculate_derived_metrics(stock_data)
        stock_data.update(derived_metrics)
        
        # Evaluate each criterion
        metrics_results = []
        total_score = 0
        
        for criterion in self.buffett_criteria:
            result = self._evaluate_criterion(stock_data, criterion)
            metrics_results.append(result)
            if result['passed']:
                total_score += 1
        
        # Generate buy recommendation
        recommendation = self._generate_recommendation(stock_data, total_score)
        
        # --- Advanced Fundamentals (Piotroski, Graham, Altman Z) ---
        raw_fin = stock_data.get('raw_financials', pd.DataFrame())
        raw_bs = stock_data.get('raw_balance_sheet', pd.DataFrame())
        raw_cf = stock_data.get('raw_cash_flow', pd.DataFrame())
        
        piotroski = self.fundamental_indicators.get_piotroski_f_score(raw_fin, raw_bs, raw_cf)
        
        # ROIC
        roic_val = self.fundamental_indicators.get_roic(raw_fin, raw_bs)
        
        market_cap = stock_data.get('market_cap', 0) or 0
        altman_z = self.fundamental_indicators.get_altman_z_score(raw_fin, raw_bs, market_cap)
        
        return {
            'total_score': total_score,
            'metrics': metrics_results,
            'recommendation': recommendation,
            'analysis_timestamp': pd.Timestamp.now(),
            'advanced_metrics': {
                'piotroski': piotroski,
                'roic': roic_val,
                'altman_z': altman_z
            }
        }
    
    def _calculate_derived_metrics(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived financial metrics"""
        metrics = {}
        
        # Basic financial ratios
        total_debt = stock_data.get('total_debt', 0) or 0
        total_equity = stock_data.get('total_stockholder_equity', 1) or 1
        
        metrics['debt_to_equity'] = total_debt / total_equity if total_equity > 0 else float('inf')
        
        current_assets = stock_data.get('total_current_assets', 0) or 0
        current_liabilities = stock_data.get('total_current_liabilities', 1) or 1
        metrics['current_ratio'] = current_assets / current_liabilities if current_liabilities > 0 else 0
        
        # ROE calculation
        net_income = stock_data.get('net_income', 0) or 0
        metrics['roe'] = (net_income / total_equity * 100) if total_equity > 0 else 0
        
        # Operating margin
        operating_income = stock_data.get('operating_income', 0) or 0
        total_revenue = stock_data.get('total_revenue', 1) or 1
        metrics['operating_margin'] = (operating_income / total_revenue * 100) if total_revenue > 0 else 0
        
        # ROCE calculation
        total_capital = total_equity + total_debt
        metrics['roce'] = (operating_income / total_capital * 100) if total_capital > 0 else 0
        
        # PEG ratio calculation
        pe_ratio = stock_data.get('pe_ratio', 0) or 0
        earnings_growth = stock_data.get('earnings_growth', 1) or 1
        metrics['peg_ratio'] = pe_ratio / earnings_growth if earnings_growth > 0 else float('inf')
        
        # Book value check
        book_value = stock_data.get('book_value', 0) or 0
        current_price = stock_data.get('current_price', 0) or 0
        metrics['book_value_check'] = current_price < book_value
        
        # Intrinsic value estimation (using Buffett's DCF method)
        metrics['intrinsic_value'] = self._calculate_buffett_dcf_intrinsic_value(stock_data)
        
        # Growth alignment (simplified)
        revenue_growth = stock_data.get('revenue_growth', 0) or 0
        profit_growth = stock_data.get('earnings_growth', 0) or 0
        if revenue_growth > 0 and profit_growth > 0:
            metrics['growth_alignment'] = min(revenue_growth, profit_growth) / max(revenue_growth, profit_growth)
        else:
            metrics['growth_alignment'] = 0
        
        # Earnings consistency (calculated in _evaluate_criterion from net_income_history)
        metrics['earnings_consistency'] = None
        
        # Free cash flow trend (simplified)
        free_cash_flow = stock_data.get('free_cash_flow', 0) or 0
        metrics['free_cash_flow'] = free_cash_flow > 0
        
        # Dividend history (simplified)
        dividend_yield = stock_data.get('dividend_yield', 0) or 0
        metrics['dividend_history'] = dividend_yield > 0
        
        # Promoter holding (placeholder - would need specific Indian market data)
        metrics['promoter_holding'] = stock_data.get('promoter_holding', 0)
        metrics['promoter_pledging'] = 0   # Still placeholder as yfinance doesn't provide this easily
        
        return metrics
    
    def _calculate_buffett_dcf_intrinsic_value(self, stock_data: Dict[str, Any]) -> float:
        """
        Calculate intrinsic value using Buffett's Discounted Cash Flow (DCF) method:
        
        Formula: Intrinsic Value = Σ(FCF_t / (1+r)^t) + Terminal Value / (1+r)^n
        
        Where:
        - FCF_t = Free Cash Flow in year t
        - r = Discount rate (10-year Treasury yield + risk premium)
        - n = Projection period (typically 10 years)
        - Terminal Value = FCF_n × (1 + g) / (r - g), where g = perpetual growth rate
        
        Divide by shares outstanding for per-share intrinsic value.
        """
        
        try:
            # Get required parameters
            current_price = stock_data.get('current_price', 0) or 0
            free_cash_flow = stock_data.get('free_cash_flow', 0) or 0
            shares_outstanding = stock_data.get('shares_outstanding', 0) or 0
            
            # If no FCF data, estimate from net income (FCF ≈ Net Income × 0.8 typically)
            if free_cash_flow <= 0:
                net_income = stock_data.get('net_income', 0) or 0
                if net_income > 0:
                    free_cash_flow = net_income * 0.8
                else:
                    # Estimate from EPS if available
                    eps = stock_data.get('eps', 0) or 0
                    if eps > 0 and shares_outstanding > 0:
                        free_cash_flow = eps * shares_outstanding * 0.8
                    elif current_price > 0:
                        # Last resort: assume 5% FCF yield
                        free_cash_flow = current_price * shares_outstanding * 0.05 if shares_outstanding > 0 else current_price * 0.05
            
            if free_cash_flow <= 0 or shares_outstanding <= 0:
                # Fallback to simpler EPS-based calculation
                return self._estimate_intrinsic_value_simple(stock_data)
            
            # DCF Parameters
            projection_years = 10  # Standard 10-year projection
            
            # Discount rate: 10-year Treasury (~4.5%) + Equity Risk Premium (~5%) = ~9.5%
            # Use 10% as a conservative round number (Buffett typically uses 10-12%)
            discount_rate = 0.10
            
            # Growth rate for FCF projection (use earnings growth, capped at 15%)
            earnings_growth = stock_data.get('earnings_growth', 10) or 10
            fcf_growth_rate = min(earnings_growth / 100, 0.15)  # Cap at 15%
            
            # Terminal growth rate (perpetual growth, typically 2-3% = GDP growth)
            terminal_growth_rate = 0.025  # 2.5%
            
            # Calculate projected FCF for each year and discount to present value
            total_present_value = 0
            projected_fcf = free_cash_flow
            
            for year in range(1, projection_years + 1):
                # Project FCF with declining growth rate
                # Growth rate declines linearly to terminal growth rate
                year_growth = fcf_growth_rate - (fcf_growth_rate - terminal_growth_rate) * (year / projection_years)
                projected_fcf = projected_fcf * (1 + year_growth)
                
                # Discount to present value
                discount_factor = (1 + discount_rate) ** year
                present_value = projected_fcf / discount_factor
                total_present_value += present_value
            
            # Calculate Terminal Value (Gordon Growth Model)
            # Terminal Value = FCF_n × (1 + g) / (r - g)
            terminal_fcf = projected_fcf * (1 + terminal_growth_rate)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
            
            # Discount terminal value to present
            terminal_pv = terminal_value / ((1 + discount_rate) ** projection_years)
            
            # Total intrinsic value = PV of projected FCFs + PV of Terminal Value
            total_intrinsic_value = total_present_value + terminal_pv
            
            # Per-share intrinsic value
            intrinsic_value_per_share = total_intrinsic_value / shares_outstanding
            
            # Apply sanity checks
            if intrinsic_value_per_share <= 0:
                return current_price * 0.8
            
            # Ensure intrinsic value is within reasonable bounds (0.2x to 5x current price)
            price_ratio = intrinsic_value_per_share / current_price if current_price > 0 else 1
            if price_ratio > 5:
                intrinsic_value_per_share = current_price * 5
            elif price_ratio < 0.2:
                intrinsic_value_per_share = current_price * 0.2
            
            return round(intrinsic_value_per_share, 2)
            
        except Exception as e:
            print(f"Error in Buffett DCF intrinsic value calculation: {e}")
            # Fallback to simpler method
            return self._estimate_intrinsic_value_simple(stock_data)
    
    def _estimate_intrinsic_value_simple(self, stock_data: Dict[str, Any]) -> float:
        """Simple intrinsic value as fallback"""
        current_price = stock_data.get('current_price', 0) or 0
        eps = stock_data.get('eps', 0) or 0
        
        if eps > 0:
            # Use conservative P/E multiple
            return eps * 12  # 12x earnings as conservative estimate
        else:
            return current_price * 0.8  # 20% discount as fallback
    
    def _evaluate_criterion(self, stock_data: Dict[str, Any], criterion: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single Buffett criterion"""
        
        key = criterion['key']
        name = criterion['name']
        criteria_text = criterion['criteria']
        
        # Get the value for this criterion
        if key in stock_data:
            value = stock_data[key]
        else:
            value = "N/A"
        
        # Evaluate based on criterion type
        passed = False
        status = "poor"
        
        if key == 'roe':
            if isinstance(value, (int, float)):
                if value > criterion['good_threshold']:
                    passed = True
                    status = "good"
                elif value > criterion['bad_threshold']:
                    status = "caution"
                value = f"{value:.2f}%"
        
        elif key == 'debt_to_equity':
            if isinstance(value, (int, float)):
                if value < criterion['excellent_threshold']:
                    passed = True
                    status = "good"
                elif value <= criterion['avoid_threshold']:
                    status = "caution"
                value = f"{value:.2f}"
        
        elif key == 'current_ratio':
            if isinstance(value, (int, float)):
                if value > criterion['good_threshold']:
                    passed = True
                    status = "good"
                elif value >= criterion['bad_threshold']:
                    status = "caution"
                value = f"{value:.2f}"
        
        elif key == 'book_value_check':
            book_value = stock_data.get('book_value', 0) or 0
            current_price = stock_data.get('current_price', 0) or 0
            currency = stock_data.get('currency', 'INR')
            # Map common currencies to symbols
            currency_symbols = {'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥'}
            curr_symbol = currency_symbols.get(currency, currency + ' ')
            if book_value > 0:
                passed = current_price < book_value
                status = "good" if passed else "poor"
                # Display actual book value vs current price
                value = f"{curr_symbol}{book_value:,.2f} (Price: {curr_symbol}{current_price:,.2f})"
            else:
                passed = False
                status = "poor"
                value = "N/A"
        
        elif key == 'pe_ratio':
            pe_value = stock_data.get('pe_ratio', 0)
            if isinstance(pe_value, (int, float)) and pe_value > 0:
                if criterion['fair_min'] <= pe_value <= criterion['fair_max']:
                    passed = True
                    status = "good"
                elif pe_value <= criterion['okay_max']:
                    status = "caution"
                value = f"{pe_value:.2f}"
            else:
                value = "N/A"
        
        elif key == 'pb_ratio':
            pb_value = stock_data.get('pb_ratio', 0)
            if isinstance(pb_value, (int, float)) and pb_value > 0:
                if pb_value < criterion['good_threshold']:
                    passed = True
                    status = "good"
                else:
                    status = "caution" if pb_value < 2.0 else "poor"
                value = f"{pb_value:.2f}"
            else:
                value = "N/A"
        
        elif key == 'intrinsic_value_check':
            current_price = stock_data.get('current_price', 0)
            intrinsic_value = stock_data.get('intrinsic_value', 0)
            currency = stock_data.get('currency', 'INR')
            currency_symbols = {'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥'}
            curr_symbol = currency_symbols.get(currency, currency + ' ')
            
            if current_price > 0 and intrinsic_value > 0:
                # Margin of Safety = (Intrinsic Value - Market Price) / Intrinsic Value × 100
                # Positive = undervalued (stock trading below intrinsic value)
                # Negative = overvalued (stock trading above intrinsic value)
                margin_of_safety = (1 - (current_price / intrinsic_value)) * 100
                
                if margin_of_safety >= criterion['discount_threshold']:
                    passed = True
                    status = "good"
                elif margin_of_safety > 0:
                    status = "caution"
                
                # Clear display: show intrinsic value and margin of safety with explanation
                if margin_of_safety >= 0:
                    value = f"IV: {curr_symbol}{intrinsic_value:,.2f} | MoS: {margin_of_safety:.1f}% (Undervalued)"
                else:
                    value = f"IV: {curr_symbol}{intrinsic_value:,.2f} | MoS: {margin_of_safety:.1f}% (Overvalued)"
            else:
                value = "N/A"
        
        elif key in ['operating_margin', 'roce']:
            if isinstance(value, (int, float)):
                if value > criterion['good_threshold']:
                    passed = True
                    status = "good"
                elif value > criterion['good_threshold'] * 0.7:
                    status = "caution"
                value = f"{value:.2f}%"
        
        elif key == 'growth_alignment':
            revenue_growth = stock_data.get('revenue_growth', 0) or 0
            profit_growth = stock_data.get('earnings_growth', 0) or 0
            years = stock_data.get('revenue_growth_years', 0) or stock_data.get('earnings_growth_years', 0)
            
            # Pass if both are positive (Growth is happening)
            if revenue_growth > 0 and profit_growth > 0:
                passed = True
                status = "good"
                
                # Check alignment for "Excellent" vs "Good" status (optional refinement)
                # If one is growing much faster than the other (e.g. > 2x difference), mark as caution but still PASS
                alignment_ratio = min(revenue_growth, profit_growth) / max(revenue_growth, profit_growth)
                if alignment_ratio < 0.5:
                    status = "caution"  # Still passed, but caution flag
            
            # Format display with actual growth percentages
            rev_sign = "+" if revenue_growth >= 0 else ""
            profit_sign = "+" if profit_growth >= 0 else ""
            
            # Check if we have real data
            if years > 1:
                # Multi-year CAGR
                period_text = f" ({years}Y CAGR)"
            elif years == 1:
                # One year data
                period_text = " (YoY)"
            else:
                period_text = " (Est)"

            if years > 0 or revenue_growth != 0 or profit_growth != 0:
                value = f"Rev: {rev_sign}{revenue_growth:.1f}% | Profit: {profit_sign}{profit_growth:.1f}%{period_text}"
            else:
                # No data available
                value = "N/A (Data not available)"
                status = "caution"
        
        elif key == 'earnings_consistency':
            income_history = stock_data.get('net_income_history', [])
            currency = stock_data.get('currency', 'INR')
            currency_symbols = {'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥'}
            curr_symbol = currency_symbols.get(currency, currency)
            
            if income_history and len(income_history) >= 2:
                # History is usually latest first, reverse to show chronological trend
                trend_values = income_history[::-1]
                
                # Check 1: Are all years positive? (No losses)
                all_positive = all(val > 0 for val in trend_values)
                
                # Check 2: Stability/Growth (Simple check: Latest > Oldest or generally increasing)
                # For "Consistency", main criteria is usually predictability and no losses.
                # User asked: "if net income stable, if not failed"
                if all_positive:
                    passed = True
                    status = "good"
                    
                    # Optional: Check if volatile (Standard Deviation / Mean > 0.5?)
                    # For now, just passing on no losses is a good baseline for "Consistency"
                else:
                    status = "poor"  # Failed if losses exist
                
                # Format for display: Show simplified numbers (e.g. 1.2B, 500Cr)
                formatted_trend = []
                for val in trend_values:
                    # Auto-scale
                    abs_val = abs(val)
                    if abs_val >= 1e9: # Billion
                        v_str = f"{val/1e9:.1f}B"
                    elif abs_val >= 1e7: # Crore (India specific preference often mixed, but stick to B/M or Cr/L based on currency?)
                        # Use Cr for INR, M for others?
                        if currency == 'INR':
                            v_str = f"{val/1e7:.0f}Cr"
                        else:
                            v_str = f"{val/1e6:.1f}M"
                    elif abs_val >= 1e6: # Million
                        v_str = f"{val/1e6:.1f}M"
                    else:
                        v_str = f"{val/1e3:.0f}K"
                    formatted_trend.append(v_str)
                
                # Show last 3-5 years trend
                trend_str = " → ".join(formatted_trend[-5:])
                value = f"{trend_str} ({'Consistent' if all_positive else 'Volatile'})"
            else:
                value = "N/A (Insufficient Data)"
        
        elif key == 'peg_ratio':
            if isinstance(value, (int, float)) and value != float('inf'):
                if value < criterion['good_threshold']:
                    passed = True
                    status = "good"
                elif value < 1.5:
                    status = "caution"
                value = f"{value:.2f}"
            else:
                value = "N/A"
        
        elif key == 'earnings_growth':
            earnings_growth = stock_data.get('earnings_growth', 0)
            if isinstance(earnings_growth, (int, float)):
                if earnings_growth > criterion['good_threshold']:
                    passed = True
                    status = "good"
                elif earnings_growth > 0:
                    status = "caution"
                value = f"{earnings_growth:.2f}%"
            else:
                value = "N/A"
        
        elif key == 'earnings_consistency':
            # This would require historical analysis
            if isinstance(value, (int, float)):
                if value > 0.6:  # Simplified threshold
                    passed = True
                    status = "good"
                elif value > 0.4:
                    status = "caution"
                value = f"{value:.2f}"
            else:
                value = "N/A"
        
        elif key == 'free_cash_flow':
            if isinstance(value, bool):
                passed = value
                status = "good" if passed else "poor"
                value = "Positive" if value else "Negative"
        
        
        elif key == 'dividend_history':
            if isinstance(value, bool):
                passed = value
                status = "good" if passed else "caution"  # Not mandatory
                value = "Yes" if value else "No"
        
        return {
            'name': name,
            'value': value,
            'status': status,
            'passed': passed,
            'criteria': criteria_text
        }
    
    def _generate_recommendation(self, stock_data: Dict[str, Any], total_score: int) -> Dict[str, Any]:
        """Generate buy/hold/avoid recommendation with CORRECT margin of safety"""
        
        current_price = stock_data.get('current_price', 0)
        intrinsic_value = stock_data.get('intrinsic_value', current_price)
        
        # CORRECTED MARGIN OF SAFETY CALCULATION
        if current_price > 0 and intrinsic_value > 0:
            margin_of_safety = (1 - (current_price / intrinsic_value)) * 100
        else:
            margin_of_safety = 0
        
        # Determine recommendation based on score and valuation
        if total_score >= 12 and margin_of_safety >= 20:
            status = "Buy"
            buy_price_max = current_price * 1.05  # 5% above current
            buy_price_min = current_price * 0.95  # 5% below current
        elif total_score >= 10 and margin_of_safety >= 10:
            status = "Buy"
            buy_price_max = current_price
            buy_price_min = current_price * 0.9
        elif total_score >= 8 or margin_of_safety >= 0:
            status = "Hold"
            target_price = intrinsic_value * 0.8  # 20% discount to intrinsic
            buy_price_max = target_price
            buy_price_min = target_price * 0.9
        else:
            status = "Avoid"
            target_price = intrinsic_value * 0.7  # 30% discount to intrinsic
            buy_price_max = target_price
            buy_price_min = target_price * 0.9
        
        return {
            'status': status,
            'current_price': current_price,
            'intrinsic_value': intrinsic_value,
            'margin_of_safety': margin_of_safety,
            'buy_price_min': buy_price_min,
            'buy_price_max': buy_price_max,
            'target_price': buy_price_max,
            'currency_symbol': stock_data.get('currency_symbol', '₹')
        }


    
    
    def get_technical_indicators(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate REAL technical indicators using historical data"""
        
        symbol = stock_data.get('symbol', '')
        current_price = stock_data.get('current_price', 0)
        
        if not symbol:
            return self._get_fallback_indicators(current_price)
        
        try:
            # Fetch historical data using yfinance (Reuse from stock_data if available to save calls)
            if 'history' in stock_data and stock_data['history'] is not None and not stock_data['history'].empty:
                hist_data = stock_data['history'].copy()
            else:
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period="1y")
            
            if hist_data.empty:
                return self._get_fallback_indicators(current_price)
            
            # --- 1. Moving Averages ---
            hist_data['SMA_50'] = hist_data['Close'].rolling(window=50).mean()
            hist_data['SMA_200'] = hist_data['Close'].rolling(window=200).mean()
            
            # --- 2. RSI ---
            hist_data = self._calculate_rsi(hist_data)
            
            # --- 3. MACD ---
            hist_data = self._calculate_macd(hist_data)
            
            # --- 4. Bollinger Bands ---
            hist_data = self._calculate_bollinger_bands(hist_data)
            
            # --- 5. Stochastic Oscillator ---
            hist_data = self._calculate_stochastic(hist_data)
            
            # --- 6. EMAs (Fast Trend) ---
            hist_data['EMA_9'] = hist_data['Close'].ewm(span=9, adjust=False).mean()
            hist_data['EMA_21'] = hist_data['Close'].ewm(span=21, adjust=False).mean()
            
            # Extract Latest Values
            latest = hist_data.iloc[-1]
            prev = hist_data.iloc[-2] if len(hist_data) > 1 else latest
            
            sma_50 = latest.get('SMA_50', current_price)
            sma_200 = latest.get('SMA_200', current_price)
            rsi = latest.get('RSI', 50)
            macd_line = latest.get('MACD_Line', 0)
            signal_line = latest.get('Signal_Line', 0)
            stoch_k = latest.get('Stoch_K', 50)
            stoch_d = latest.get('Stoch_D', 50)
            ema_9 = latest.get('EMA_9', current_price)
            ema_21 = latest.get('EMA_21', current_price)
            
            # --- Calculate Technical Score (0-100) ---
            tech_score = 0
            signals = []
            
            # 1. Long Term Trend (Max 20 pts)
            if current_price > sma_200:
                tech_score += 15
                signals.append("Price > SMA200 (Long Term Bullish)")
            if current_price > sma_50:
                tech_score += 5
            
            # 2. Fast Trend (EMA Crossover) (Max 20 pts)
            if ema_9 > ema_21:
                tech_score += 20
                signals.append("EMA 9 > EMA 21 (Short Term Bullish)")
            else:
                signals.append("EMA 9 < EMA 21 (Short Term Bearish)")

            # 3. RSI (Max 15 pts)
            if 40 <= rsi <= 70:
                tech_score += 15
            elif rsi > 70:
                tech_score += 5
                signals.append("RSI Overbought (>70)")
            elif rsi < 30:
                tech_score += 10
                signals.append("RSI Oversold (<30) - Potential Bounce")
                
            # 4. MACD (Max 15 pts)
            if macd_line > signal_line:
                tech_score += 15
                signals.append("MACD Bullish Crossover")
            
            # 5. Stochastic (Max 15 pts)
            if stoch_k < 20 and stoch_k > stoch_d:
                tech_score += 15
                signals.append("Stochastic Oversold Cross (Buy)")
            elif stoch_k > 80 and stoch_k < stoch_d:
                 pass # Bearish signal
            elif stoch_k > stoch_d:
                tech_score += 10
            
            # 6. Bollinger (Max 15 pts)
            bb_upper = latest.get('BB_Upper', current_price * 1.1)
            bb_lower = latest.get('BB_Lower', current_price * 0.9)
            
            if current_price > bb_lower and current_price < bb_upper:
                tech_score += 15
            elif current_price >= bb_upper:
                 tech_score += 10
                 signals.append("Price hitting Upper BB (Momentum)")
            elif current_price <= bb_lower:
                 tech_score += 5
                 signals.append("Price at Lower BB (Support)")

            # Determine Verdict
            if tech_score >= 80:
                verdict = "Strong Bullish"
                action = "BUY"
            elif tech_score >= 60:
                verdict = "Bullish"
                action = "ACCUMULATE"
            elif tech_score >= 40:
                verdict = "Neutral"
                action = "HOLD"
            else:
                verdict = "Bearish"
                action = "AVOID"

            return {
                'rsi': round(rsi, 2),
                'sma_50': round(sma_50, 2),
                'sma_200': round(sma_200, 2),
                'macd': round(macd_line, 2),
                'macd_signal': round(signal_line, 2),
                'stoch_k': round(stoch_k, 2),
                'stoch_d': round(stoch_d, 2),
                'ema_9': round(ema_9, 2),
                'ema_21': round(ema_21, 2),
                'bb_upper': round(bb_upper, 2),
                'bb_lower': round(bb_lower, 2),
                'technical_score': tech_score,
                'verdict': verdict,
                'action': action,
                'signals': signals,
                'trend': verdict 
            }
            
        except Exception as e:
            print(f"Error calculating technical indicators for {symbol}: {e}")
            return self._get_fallback_indicators(current_price)
    
    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        data['RSI'] = rsi
        return data

    def _calculate_stochastic(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Stochastic Oscillator"""
        low_min = data['Low'].rolling(window=period).min()
        high_max = data['High'].rolling(window=period).max()
        
        # Fast %K
        data['Stoch_K'] = 100 * ((data['Close'] - low_min) / (high_max - low_min))
        # Slow %D (3-period SMA of %K)
        data['Stoch_D'] = data['Stoch_K'].rolling(window=3).mean()
        return data

    def _calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD (12, 26, 9)"""
        exp12 = data['Close'].ewm(span=12, adjust=False).mean()
        exp26 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD_Line'] = exp12 - exp26
        data['Signal_Line'] = data['MACD_Line'].ewm(span=9, adjust=False).mean()
        return data

    def _calculate_bollinger_bands(self, data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        sma = data['Close'].rolling(window=window).mean()
        std = data['Close'].rolling(window=window).std()
        data['BB_Upper'] = sma + (std * 2)
        data['BB_Lower'] = sma - (std * 2)
        return data
    
    def _get_fallback_indicators(self, current_price: float) -> Dict[str, Any]:
        """Fallback technical indicators when historical data is not available"""
        return {
            'rsi': 50.0,
            'sma_50': current_price,
            'sma_200': current_price * 0.95,
            'macd': 0, 'macd_signal': 0,
            'stoch_k': 50, 'stoch_d': 50,
            'ema_9': current_price, 'ema_21': current_price,
            'bb_upper': current_price * 1.05,
            'bb_lower': current_price * 0.95,
            'technical_score': 50,
            'verdict': "Data Not Available",
            'action': "HOLD",
            'signals': ["Insufficient Data"],
            'trend': "Data Not Available"
        }
    
    