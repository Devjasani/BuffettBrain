import pandas as pd
import numpy as np
from typing import Dict, List, Any
import yfinance as yf
from datetime import datetime, timedelta

class StockAnalyzer:
    def __init__(self):
        self.buffett_criteria = self._initialize_buffett_criteria()
    
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
                'criteria': 'Market Price 20-30% below Intrinsic Value',
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
                'criteria': 'Revenue and Profit Growth Aligned',
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
            },
            {
                'name': 'Promoter Holding & Pledging',
                'key': 'promoter_holding',
                'criteria': 'High holding, no/low pledging',
                'holding_threshold': 50,
                'pledging_threshold': 5
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
        
        return {
            'total_score': total_score,
            'metrics': metrics_results,
            'recommendation': recommendation,
            'analysis_timestamp': pd.Timestamp.now()
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
        
        # Intrinsic value estimation (using Graham's formula)
        metrics['intrinsic_value'] = self._calculate_graham_intrinsic_value(stock_data)
        
        # Growth alignment (simplified)
        revenue_growth = stock_data.get('revenue_growth', 0) or 0
        profit_growth = stock_data.get('earnings_growth', 0) or 0
        if revenue_growth > 0 and profit_growth > 0:
            metrics['growth_alignment'] = min(revenue_growth, profit_growth) / max(revenue_growth, profit_growth)
        else:
            metrics['growth_alignment'] = 0
        
        # Earnings consistency (simplified volatility measure)
        metrics['earnings_consistency'] = 0.7  # Placeholder - would need historical data
        
        # Free cash flow trend (simplified)
        free_cash_flow = stock_data.get('free_cash_flow', 0) or 0
        metrics['free_cash_flow'] = free_cash_flow > 0
        
        # Dividend history (simplified)
        dividend_yield = stock_data.get('dividend_yield', 0) or 0
        metrics['dividend_history'] = dividend_yield > 0
        
        # Promoter holding (placeholder - would need specific Indian market data)
        metrics['promoter_holding'] = 60  # Placeholder percentage
        metrics['promoter_pledging'] = 2   # Placeholder percentage
        
        return metrics
    
    def _calculate_graham_intrinsic_value(self, stock_data: Dict[str, Any]) -> float:
        """
        Calculate intrinsic value using Benjamin Graham's formula:
        
        Original Formula: Intrinsic Value = EPS × (8.5 + 2g)
        Revised Formula: Intrinsic Value = EPS × (8.5 + 2g) × (4.4 / Y)
        
        Where:
        - EPS = Earnings per share (TTM)
        - 8.5 = P/E ratio for a no-growth company
        - g = expected annual earnings growth rate (as %, use 7.5% if not available)
        - 4.4 = historical average yield of AAA corporate bonds
        - Y = current yield of AAA corporate bonds (use 4.0% as default)
        """
        
        try:
            # Get required parameters
            eps = stock_data.get('eps', 0) or 0
            current_price = stock_data.get('current_price', 0) or 0
            
            # If EPS is not available or unreasonable, estimate from P/E ratio
            if eps <= 0:
                pe_ratio = stock_data.get('pe_ratio', 0) or 0
                if pe_ratio > 0 and current_price > 0:
                    eps = current_price / pe_ratio
                else:
                    # If still no EPS, use conservative estimate
                    eps = current_price * 0.05  # Assume 5% earnings yield
            
            # Ensure EPS is reasonable
            if eps <= 0:
                return current_price * 0.8  # Fallback: 20% below current price
            
            # Get growth rate (use earnings growth if available, otherwise conservative estimate)
            growth_rate = stock_data.get('earnings_growth', 7.5) or 7.5
            # Ensure growth rate is reasonable (not too high)
            growth_rate = min(growth_rate, 25.0)  # Cap at 25% maximum
            
            # Current AAA corporate bond yield (conservative estimate)
            current_bond_yield = 4.0  # 4.0% as default
            
            # Calculate using Graham's REVISED formula
            # Intrinsic Value = EPS × (8.5 + 2g) × (4.4 / Y)
            intrinsic_value = eps * (8.5 + (2 * growth_rate)) * (4.4 / current_bond_yield)
            
            # Apply sanity checks
            if intrinsic_value <= 0:
                return current_price * 0.8
                
            # Ensure intrinsic value is not extremely different from current price
            # (not more than 10x or less than 0.1x current price)
            price_ratio = intrinsic_value / current_price if current_price > 0 else 1
            if price_ratio > 10:
                intrinsic_value = current_price * 10
            elif price_ratio < 0.1:
                intrinsic_value = current_price * 0.1
                
            return round(intrinsic_value, 2)
            
        except Exception as e:
            print(f"Error in Graham intrinsic value calculation: {e}")
            # Fallback to simpler method
            current_price = stock_data.get('current_price', 0) or 0
            return current_price * 0.8  # Conservative fallback
    
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
            if isinstance(value, bool):
                passed = value
                status = "good" if passed else "poor"
                value = "Yes" if value else "No"
        
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
            if current_price > 0 and intrinsic_value > 0:
                # CORRECTED MARGIN OF SAFETY FORMULA
                margin_of_safety = (1 - (current_price / intrinsic_value)) * 100
                if margin_of_safety >= criterion['discount_threshold']:
                    passed = True
                    status = "good"
                elif margin_of_safety > 0:
                    status = "caution"
                value = f"{margin_of_safety:.1f}%"
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
            if isinstance(value, (int, float)):
                if value > criterion['alignment_threshold']:
                    passed = True
                    status = "good"
                elif value > 0.5:
                    status = "caution"
                value = f"{value:.2f}"
        
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
        
        elif key == 'promoter_holding':
            holding = stock_data.get('promoter_holding', 0)
            pledging = stock_data.get('promoter_pledging', 0)
            if holding > criterion['holding_threshold'] and pledging < criterion['pledging_threshold']:
                passed = True
                status = "good"
            elif holding > 30:
                status = "caution"
            value = f"{holding:.1f}% holding, {pledging:.1f}% pledged"
        
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
            'target_price': buy_price_max
        }
    
    def get_technical_indicators(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate REAL technical indicators using historical data"""
        
        symbol = stock_data.get('symbol', '')
        current_price = stock_data.get('current_price', 0)
        
        if not symbol:
            return self._get_fallback_indicators(current_price)
        
        try:
            # Fetch historical data using yfinance
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period="1y")
            
            if hist_data.empty:
                return self._get_fallback_indicators(current_price)
            
            # Calculate SMA 50 and SMA 200
            hist_data['SMA_50'] = hist_data['Close'].rolling(window=50).mean()
            hist_data['SMA_200'] = hist_data['Close'].rolling(window=200).mean()
            
            # Calculate RSI
            hist_data = self._calculate_rsi(hist_data)
            
            # Get latest values
            latest_data = hist_data.iloc[-1]
            sma_50 = latest_data.get('SMA_50', current_price)
            sma_200 = latest_data.get('SMA_200', current_price)
            rsi = latest_data.get('RSI', 50)
            
            # Determine trend
            if current_price > sma_50 and current_price > sma_200:
                trend = "Strong Uptrend 📈"
            elif current_price > sma_50:
                trend = "Moderate Uptrend 📊"
            elif current_price > sma_200:
                trend = "Weak Uptrend ↗️"
            else:
                trend = "Downtrend 📉"
            
            return {
                'rsi': round(rsi, 2),
                'sma_50': round(sma_50, 2),
                'sma_200': round(sma_200, 2),
                'trend': trend,
                'price_vs_sma50': round(((current_price - sma_50) / sma_50 * 100), 2),
                'price_vs_sma200': round(((current_price - sma_200) / sma_200 * 100), 2)
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
    
    def _get_fallback_indicators(self, current_price: float) -> Dict[str, Any]:
        """Fallback technical indicators when historical data is not available"""
        return {
            'rsi': 50.0,
            'sma_50': current_price,
            'sma_200': current_price * 0.95,
            'trend': "Data Not Available",
            'price_vs_sma50': 0.0,
            'price_vs_sma200': 5.0
        }
    
    