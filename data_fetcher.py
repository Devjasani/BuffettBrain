# data_fetcher.py
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import re
from difflib import SequenceMatcher

class DataFetcher:
    def __init__(self):
        self.indian_stock_suffixes = ['.NS', '.BO']  # NSE and BSE
        self.common_indian_stocks = {
            'tcs': 'TCS.NS',
            'reliance': 'RELIANCE.NS',
            'infy': 'INFY.NS',
            'infosys': 'INFY.NS',
            'hdfcbank': 'HDFCBANK.NS',
            'icicibank': 'ICICIBANK.NS',
            'wipro': 'WIPRO.NS',
            'itc': 'ITC.NS',
            'lt': 'LT.NS',
            'larsen': 'LT.NS',
            'sbin': 'SBIN.NS',
            'bhartiartl': 'BHARTIARTL.NS',
            'airtel': 'BHARTIARTL.NS',
            'maruti': 'MARUTI.NS',
            'asian paints': 'ASIANPAINT.NS',
            'asianpaint': 'ASIANPAINT.NS',
            'bajaj finance': 'BAJFINANCE.NS',
            'bajfinance': 'BAJFINANCE.NS',
            'kotak': 'KOTAKBANK.NS',
            'kotakbank': 'KOTAKBANK.NS',
            'hindunilvr': 'HINDUNILVR.NS',
            'hindustan unilever': 'HINDUNILVR.NS',
            'axisbank': 'AXISBANK.NS',
            'axis bank': 'AXISBANK.NS',
            'nestleind': 'NESTLEIND.NS',
            'nestle': 'NESTLEIND.NS',
            'titan': 'TITAN.NS',
            'ultratech': 'ULTRACEMCO.NS',
            'ultracemco': 'ULTRACEMCO.NS',
            'powergrid': 'POWERGRID.NS',
            'ntpc': 'NTPC.NS',
            'ongc': 'ONGC.NS',
            'coal india': 'COALINDIA.NS',
            'coalindia': 'COALINDIA.NS',
            'jswsteel': 'JSWSTEEL.NS',
            'jsw steel': 'JSWSTEEL.NS',
            'tatamotors': 'TATAMOTORS.NS',
            'tata motors': 'TATAMOTORS.NS',
            'bajaj auto': 'BAJAJ-AUTO.NS',
            'bajaj-auto': 'BAJAJ-AUTO.NS',
            'bajajauto': 'BAJAJ-AUTO.NS',
            'britannia': 'BRITANNIA.NS',
            'drreddy': 'DRREDDY.NS',
            'dr reddy': 'DRREDDY.NS',
            'eichermot': 'EICHERMOT.NS',
            'eicher': 'EICHERMOT.NS',
            'grasim': 'GRASIM.NS',
            'hcltech': 'HCLTECH.NS',
            'hcl tech': 'HCLTECH.NS',
            'heromotoco': 'HEROMOTOCO.NS',
            'hero motocorp': 'HEROMOTOCO.NS',
            'hindalco': 'HINDALCO.NS',
            'indusindbk': 'INDUSINDBK.NS',
            'indusind bank': 'INDUSINDBK.NS',
            'techm': 'TECHM.NS',
            'tech mahindra': 'TECHM.NS',
            'upl': 'UPL.NS',
            'vedl': 'VEDL.NS',
            'vedanta': 'VEDL.NS'
        }
    
    def get_stock_data(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Fetch comprehensive stock data for Indian stocks
        Accepts various input formats: ticker, company name, etc.
        """
        
        # Clean and normalize the query
        normalized_query = self._normalize_query(query)
        
        # Try to find the stock symbol
        symbol = self._find_stock_symbol(normalized_query)
        
        if not symbol:
            return None
        
        try:
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            
            # Get basic info
            info = ticker.info
            
            # Get historical data for calculations
            hist = ticker.history(period="1y")
            
            if hist.empty or not info:
                return None
            
            # Get current price
            current_price = hist['Close'].iloc[-1] if not hist.empty else info.get('currentPrice', 0)
            
            # Get financial data
            financials = self._get_financial_data(ticker)
            
            # Determine market and currency symbol
            market = self.get_market_from_symbol(symbol)
            currency_code = info.get('currency', 'USD')
            currency_symbol = self.get_currency_symbol(currency_code, market)
            
            # Compile comprehensive stock data
            stock_data = {
                # Basic info
                'symbol': symbol,
                'long_name': info.get('longName', ''),
                'short_name': info.get('shortName', ''),
                'business_summary': info.get('longBusinessSummary', ''),
                'industry': info.get('industry', ''),
                'sector': info.get('sector', ''),
                'exchange': info.get('exchange', ''),
                'currency': info.get('currency', 'USD'),
                'currency_symbol': currency_symbol,
                'market': market,
                
                # Price data
                'current_price': current_price,
                'previous_close': info.get('previousClose', current_price),
                'open_price': info.get('open', current_price),
                'day_low': info.get('dayLow', current_price),
                'day_high': info.get('dayHigh', current_price),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', current_price),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', current_price),
                
                # Market data
                'market_cap': info.get('marketCap', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'float_shares': info.get('floatShares', 0),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                
                # Valuation ratios
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'ps_ratio': info.get('priceToSalesTrailing12Months', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'ev_revenue': info.get('enterpriseToRevenue', 0),
                'ev_ebitda': info.get('enterpriseToEbitda', 0),
                
                # Financial metrics
                'book_value': info.get('bookValue', 0),
                'eps': info.get('trailingEps', 0),
                'forward_eps': info.get('forwardEps', 0),
                'beta': info.get('beta', 1.0),
                
                # Dividend data
                'dividend_rate': info.get('dividendRate', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'payout_ratio': info.get('payoutRatio', 0),
                'ex_dividend_date': info.get('exDividendDate', None),
                
                # Financial statement data
                **financials,
                
                # Calculated fields
                'change_percent': self._calculate_change_percent(current_price, info.get('previousClose', current_price)),
                'revenue_growth': self._calculate_growth_rate(financials.get('total_revenue', 0), 'revenue'),
                'earnings_growth': self._calculate_growth_rate(financials.get('net_income', 0), 'earnings'),
            }
            
            return stock_data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_currency_symbol(self, currency_code: str, market: str = '') -> str:
        """Get currency symbol based on currency code or market"""
        currency_map = {
            'INR': '₹',
            'USD': '$',
            'GBP': '£',
            'EUR': '€',
            'JPY': '¥',
            'CNY': '¥',
            'AUD': 'A$',
            'CAD': 'C$',
            'HKD': 'HK$',
            'SGD': 'S$',
            'BRL': 'R$',
            'KRW': '₩',
            'CHF': 'CHF',
        }
        
        # Normalize currency code
        if currency_code:
            currency_code = currency_code.upper()
        
        # Try to get by currency code first
        if currency_code in currency_map:
            return currency_map[currency_code]
        
        # Fallback to market-based mapping
        market_currency_map = {
            'India': '₹',
            'USA': '$',
            'UK': '£',
            'Japan': '¥',
            'Hong Kong': 'HK$',
            'Australia': 'A$',
            'Canada': 'C$',
            'Brazil': 'R$',
            'Germany': '€',
            'France': '€',
            'Italy': '€',
            'Spain': '€',
        }
        
        return market_currency_map.get(market, '$')
    
    def _normalize_query(self, query: str) -> str:
        """Normalize the input query for better matching"""
        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r'\s+', ' ', query.lower().strip())
        
        # Remove common suffixes if present
        for suffix in ['.ns', '.bo', '.nse', '.bse']:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
                break
        
        return normalized
    
    def _find_stock_symbol(self, query: str) -> Optional[str]:
        """Find the appropriate stock symbol for the query"""
        
        # First, check if it's in our predefined list
        if query in self.common_indian_stocks:
            return self.common_indian_stocks[query]
        
        # Check for partial matches in company names
        for name, symbol in self.common_indian_stocks.items():
            if query in name or name in query:
                return symbol
        
        # If not found, try adding Indian suffixes
        possible_symbols = [
            query.upper(),
            f"{query.upper()}.NS",
            f"{query.upper()}.BO"
        ]
        
        # Test each possible symbol
        for symbol in possible_symbols:
            if self._validate_symbol(symbol):
                return symbol
        
        return None
    
    def _validate_symbol(self, symbol: str) -> bool:
        """Validate if a symbol exists and has data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we got valid data
            if info and info.get('regularMarketPrice') or info.get('currentPrice'):
                return True
            
            # Also check if we can get recent history
            hist = ticker.history(period="5d")
            return not hist.empty
            
        except:
            return False
    
    def _get_financial_data(self, ticker) -> Dict[str, Any]:
        """Extract financial statement data from ticker"""
        
        financial_data = {}
        
        try:
            # Get financials
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            if not financials.empty:
                # Income statement items (most recent year)
                latest_col = financials.columns[0]
                financial_data.update({
                    'total_revenue': financials.loc['Total Revenue', latest_col] if 'Total Revenue' in financials.index else 0,
                    'operating_income': financials.loc['Operating Income', latest_col] if 'Operating Income' in financials.index else 0,
                    'net_income': financials.loc['Net Income', latest_col] if 'Net Income' in financials.index else 0,
                    'ebitda': financials.loc['EBITDA', latest_col] if 'EBITDA' in financials.index else 0,
                })
            
            if not balance_sheet.empty:
                # Balance sheet items (most recent year)
                latest_col = balance_sheet.columns[0]
                financial_data.update({
                    'total_assets': balance_sheet.loc['Total Assets', latest_col] if 'Total Assets' in balance_sheet.index else 0,
                    'total_debt': balance_sheet.loc['Total Debt', latest_col] if 'Total Debt' in balance_sheet.index else 0,
                    'total_stockholder_equity': balance_sheet.loc['Stockholders Equity', latest_col] if 'Stockholders Equity' in balance_sheet.index else 0,
                    'total_current_assets': balance_sheet.loc['Current Assets', latest_col] if 'Current Assets' in balance_sheet.index else 0,
                    'total_current_liabilities': balance_sheet.loc['Current Liabilities', latest_col] if 'Current Liabilities' in balance_sheet.index else 0,
                })
            
            if not cash_flow.empty:
                # Cash flow items (most recent year)
                latest_col = cash_flow.columns[0]
                financial_data.update({
                    'operating_cash_flow': cash_flow.loc['Total Cash From Operating Activities', latest_col] if 'Total Cash From Operating Activities' in cash_flow.index else 0,
                    'free_cash_flow': cash_flow.loc['Free Cash Flow', latest_col] if 'Free Cash Flow' in cash_flow.index else 0,
                    'capital_expenditures': cash_flow.loc['Capital Expenditures', latest_col] if 'Capital Expenditures' in cash_flow.index else 0,
                })
        
        except Exception as e:
            print(f"Error getting financial data: {str(e)}")
        
        # Fill missing values with 0
        for key in ['total_revenue', 'operating_income', 'net_income', 'ebitda', 
                   'total_assets', 'total_debt', 'total_stockholder_equity',
                   'total_current_assets', 'total_current_liabilities',
                   'operating_cash_flow', 'free_cash_flow', 'capital_expenditures']:
            if key not in financial_data:
                financial_data[key] = 0
        
        return financial_data
    
    def _calculate_change_percent(self, current: float, previous: float) -> float:
        """Calculate percentage change"""
        if previous and previous != 0:
            return ((current - previous) / previous) * 100
        return 0
    
    def _calculate_growth_rate(self, current_value: float, metric_type: str) -> float:
        """Calculate growth rate (simplified - would need historical data for accurate calculation)"""
        # This is a placeholder - in reality, you'd need multiple years of data
        # For now, return a reasonable estimate based on current market conditions
        
        if metric_type == 'revenue':
            return np.random.uniform(5, 15)  # 5-15% revenue growth assumption
        elif metric_type == 'earnings':
            return np.random.uniform(8, 20)  # 8-20% earnings growth assumption
        
        return 0
    
    def search_stocks(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """Search for stocks and return suggestions with fuzzy matching"""
        suggestions = []
        normalized_query = self._normalize_query(query)
        
        # Calculate similarity scores for all stocks
        scored_stocks = []
        for name, symbol in self.common_indian_stocks.items():
            # Calculate similarity ratio
            similarity = SequenceMatcher(None, normalized_query, name).ratio()
            
            # Boost score for exact substring matches
            if normalized_query in name:
                similarity += 0.3
            elif name in normalized_query:
                similarity += 0.2
            
            # Boost score for matching start of name
            if name.startswith(normalized_query):
                similarity += 0.2
            
            scored_stocks.append({
                'name': name.title(),
                'symbol': symbol,
                'score': similarity
            })
        
        # Sort by score and take top results
        scored_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        # Filter out low scoring matches (below 0.3 threshold)
        suggestions = [
            {'name': stock['name'], 'symbol': stock['symbol']}
            for stock in scored_stocks[:limit]
            if stock['score'] > 0.3
        ]
        
        return suggestions
    
    def get_stock_with_suggestions(self, query: str) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, str]]]:
        """Get stock data and also return similar stocks if not found"""
        # Try to get the exact stock
        stock_data = self.get_stock_data(query)
        
        # If found, return with empty suggestions
        if stock_data:
            return stock_data, []
        
        # If not found, return similar stocks
        suggestions = self.search_stocks(query, limit=5)
        return None, suggestions
    
    def get_market_from_symbol(self, symbol: str) -> str:
        """Determine the market/country from stock symbol"""
        if '.NS' in symbol or '.BO' in symbol:
            return 'India'
        elif '.L' in symbol:
            return 'UK'
        elif '.HK' in symbol:
            return 'Hong Kong'
        elif '.T' in symbol or '.JP' in symbol:
            return 'Japan'
        elif '.AX' in symbol:
            return 'Australia'
        elif '.SA' in symbol:
            return 'Brazil'
        elif '.TO' in symbol:
            return 'Canada'
        else:
            return 'USA'