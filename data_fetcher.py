# data_fetcher.py
import yfinance as yf
import requests
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import re
from difflib import SequenceMatcher
import streamlit as st
import time

@st.cache_data(ttl=300, show_spinner=False)
def fetch_symbol_data(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Standalone function to fetch data with caching and retries.
    Returns: dictionary with 'info', 'history', 'financials', 'balance_sheet', 'cashflow', 'major_holders'
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            ticker = yf.Ticker(symbol)
            
            # 1. Fetch Basic Info
            info = ticker.info
            
            # 2. Fetch History (1y)
            hist = ticker.history(period="1y")
            
            if hist.empty and not info:
                # If both fail, likely invalid symbol or network issue
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return None
            
            # 3. Fetch Financials (safely)
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow
            major_holders = ticker.major_holders
            
            return {
                'info': info,
                'history': hist,
                'financials': financials,
                'balance_sheet': balance_sheet,
                'cashflow': cashflow,
                'major_holders': major_holders
            }
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            print(f"Failed to fetch data for {symbol} after {max_retries} retries: {e}")
            return None
    return None

@st.cache_data(ttl=60, show_spinner=False)
def fetch_market_indices() -> List[Dict[str, Any]]:
    """Fetch live data for major market indices (Standalone Cached)"""
    indices = [
        {'symbol': '^NSEI', 'name': 'NIFTY 50', 'currency': '₹'},
        {'symbol': '^BSESN', 'name': 'SENSEX', 'currency': '₹'},
        {'symbol': '^IXIC', 'name': 'NASDAQ', 'currency': '$'},
        {'symbol': '^GSPC', 'name': 'S&P 500', 'currency': '$'},
        {'symbol': 'GC=F', 'name': 'GOLD', 'currency': '$'},
        {'symbol': 'BTC-USD', 'name': 'BITCOIN', 'currency': '$'},
    ]
    
    results = []
    for index in indices:
        try:
            ticker = yf.Ticker(index['symbol'])
            hist = ticker.history(period="2d")
            
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                change = ((current - prev) / prev) * 100
                
                results.append({
                    'name': index['name'],
                    'price': current,
                    'change': change,
                    'currency': index['currency']
                })
        except Exception as e:
            print(f"Error fetching index {index['name']}: {e}")
            
    return results

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
            # === OPTIMIZATION: Use Cached Fetcher with Retry ===
            data_bundle = fetch_symbol_data(symbol)
            
            if not data_bundle:
                return None
                
            info = data_bundle['info']
            hist = data_bundle['history']
            
            # Get current price
            current_price = hist['Close'].iloc[-1] if not hist.empty else info.get('currentPrice', 0)
            
            # Get financial data (pass the pre-fetched dfs)
            financials = self._process_financial_data(data_bundle)
            
            # Determine market and currency symbol
            market = self.get_market_from_symbol(symbol)
            currency_code = info.get('currency', 'USD')
            currency_symbol = self.get_currency_symbol(currency_code, market)
            
            # Fetch Promoter/Insider Holding with Fallback calculation
            promoter_holding = (info.get('heldPercentInsiders', 0) or 0) * 100
            
            # Fallback for Indian stocks or when info is missing
            if promoter_holding == 0:
                try:
                    mh = data_bundle.get('major_holders')
                    if mh is not None and not mh.empty:
                        # Parsing logic
                        val = mh.iloc[0, 0]
                        
                        # Clean and convert
                        if isinstance(val, (int, float)):
                            promoter_holding = float(val) * 100 
                        elif isinstance(val, str):
                            val_str = val.replace('%', '').strip()
                            promoter_holding = float(val_str)
                        
                        # Validate reasonable range
                        if promoter_holding < 1 and promoter_holding > 0:
                           pass
                except Exception as e:
                    pass

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
                
                # Promoter/Insider Holding
                # Yahoo Finance uses 'heldPercentInsiders' for promoter/insider holding (0.72 = 72%)
                'promoter_holding': promoter_holding,
                'promoter_pledging': 0,  # Yahoo Finance rarely provides pledging data in standard info
                
                # Financial statement data
                **financials,
                
                # Growth metrics: Prefer 5-year CAGR from financials, fallback to YoY info
                'revenue_growth': financials.get('revenue_growth') if financials.get('revenue_growth_years', 0) >= 2 else (info.get('revenueGrowth', 0) or 0) * 100,
                'earnings_growth': financials.get('earnings_growth') if financials.get('earnings_growth_years', 0) >= 2 else (info.get('earningsGrowth', 0) or info.get('earningsQuarterlyGrowth', 0) or 0) * 100,
                'revenue_growth_years': financials.get('revenue_growth_years') if financials.get('revenue_growth_years', 0) >= 2 else (1 if info.get('revenueGrowth') else 0),
                'earnings_growth_years': financials.get('earnings_growth_years') if financials.get('earnings_growth_years', 0) >= 2 else (1 if info.get('earningsGrowth') or info.get('earningsQuarterlyGrowth') else 0),
                
                # Calculated fields
                'change_percent': self._calculate_change_percent(current_price, info.get('previousClose', current_price)),
                'history': hist  # Expose full history for charts
            }
            
            return stock_data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    def get_market_indices(self) -> List[Dict[str, Any]]:
        """Fetch live data for major market indices (Delegates to cached function)"""
        return fetch_market_indices()
    
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
    
    def _process_financial_data(self, data_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial statement data from pre-fetched bundle with historical growth calculations"""
        
        financial_data = {}
        
        try:
            # Get financials from bundle
            financials = data_bundle.get('financials', pd.DataFrame())
            balance_sheet = data_bundle.get('balance_sheet', pd.DataFrame())
            cash_flow = data_bundle.get('cashflow', pd.DataFrame())
            
            if not financials.empty:
                # Income statement items (most recent year)
                latest_col = financials.columns[0]
                financial_data.update({
                    'total_revenue': financials.loc['Total Revenue', latest_col] if 'Total Revenue' in financials.index else 0,
                    'operating_income': financials.loc['Operating Income', latest_col] if 'Operating Income' in financials.index else 0,
                    'net_income': financials.loc['Net Income', latest_col] if 'Net Income' in financials.index else 0,
                    'ebitda': financials.loc['EBITDA', latest_col] if 'EBITDA' in financials.index else 0,
                })
                
                # Calculate real historical growth rates (CAGR over available years)
                num_years = min(len(financials.columns), 5)  # Use up to 5 years
                if num_years >= 2:
                    # Revenue Growth CAGR
                    if 'Total Revenue' in financials.index:
                        latest_revenue = financials.loc['Total Revenue', financials.columns[0]]
                        oldest_revenue = financials.loc['Total Revenue', financials.columns[num_years - 1]]
                        if oldest_revenue and oldest_revenue > 0 and latest_revenue and latest_revenue > 0:
                            # CAGR = (End Value / Start Value)^(1/n) - 1
                            revenue_cagr = ((latest_revenue / oldest_revenue) ** (1 / (num_years - 1)) - 1) * 100
                            financial_data['revenue_growth'] = round(revenue_cagr, 2)
                            financial_data['revenue_growth_years'] = num_years - 1
                        else:
                            financial_data['revenue_growth'] = 0
                            financial_data['revenue_growth_years'] = 0
                    
                    # Net Income (Profit) Growth CAGR
                    if 'Net Income' in financials.index:
                        latest_income = financials.loc['Net Income', financials.columns[0]]
                        oldest_income = financials.loc['Net Income', financials.columns[num_years - 1]]
                        
                        # Store history for consistency check (new)
                        income_history = []
                        for i in range(num_years):
                            val = financials.loc['Net Income', financials.columns[i]]
                            income_history.append(val)
                        financial_data['net_income_history'] = income_history
                        
                        if oldest_income and oldest_income > 0 and latest_income and latest_income > 0:
                            profit_cagr = ((latest_income / oldest_income) ** (1 / (num_years - 1)) - 1) * 100
                            financial_data['earnings_growth'] = round(profit_cagr, 2)
                            financial_data['earnings_growth_years'] = num_years - 1
                        else:
                            # Handle negative income scenarios
                            financial_data['earnings_growth'] = 0
                            financial_data['earnings_growth_years'] = 0
                else:
                    financial_data['revenue_growth'] = 8.0  # Default fallback
                    financial_data['earnings_growth'] = 10.0  # Default fallback
                    financial_data['revenue_growth_years'] = 0
                    financial_data['earnings_growth_years'] = 0
            
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
            
            # Add raw dataframes for advanced analysis (Piotroski, Altman Z, etc.)
            financial_data['raw_financials'] = financials
            financial_data['raw_balance_sheet'] = balance_sheet
            financial_data['raw_cash_flow'] = cash_flow
        
        except Exception as e:
            print(f"Error getting financial data: {str(e)}")
        
        # Fill missing values with defaults
        defaults = {
            'total_revenue': 0, 'operating_income': 0, 'net_income': 0, 'ebitda': 0,
            'total_assets': 0, 'total_debt': 0, 'total_stockholder_equity': 0,
            'total_current_assets': 0, 'total_current_liabilities': 0,
            'operating_cash_flow': 0, 'free_cash_flow': 0, 'capital_expenditures': 0,
            'revenue_growth': 8.0, 'earnings_growth': 10.0,
            'revenue_growth_years': 0, 'earnings_growth_years': 0
        }
        for key, default_val in defaults.items():
            if key not in financial_data:
                financial_data[key] = default_val
        
        return financial_data
    
    def _calculate_change_percent(self, current: float, previous: float) -> float:
        """Calculate percentage change"""
        if previous and previous != 0:
            return ((current - previous) / previous) * 100
        return 0
    
    def _calculate_growth_rate(self, current_value: float, metric_type: str) -> float:
        """Calculate growth rate based on reasonable estimates (no randomness)"""
        # Use deterministic conservative estimates based on market averages
        # This ensures consistent results for the same stock
        
        if current_value <= 0:
            return 0.0
        
        if metric_type == 'revenue':
            # Conservative revenue growth estimate (S&P 500 average is ~5-7%)
            return 8.0  # 8% revenue growth assumption
        elif metric_type == 'earnings':
            # Conservative earnings growth estimate (historical average ~10%)
            return 10.0  # 10% earnings growth assumption
        
        return 5.0  # Default conservative growth rate
    
    
    def _search_yahoo_api(self, query: str) -> List[Dict[str, str]]:
        """Search using Yahoo Finance API"""
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        suggestions = []
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            data = response.json()
            
            if 'quotes' in data:
                for quote in data['quotes']:
                    # Only include stocks and ETFs
                    if quote.get('quoteType') in ['EQUITY', 'ETF', 'MUTUALFUND']:
                        symbol = quote.get('symbol')
                        shortname = quote.get('shortname') or quote.get('longname') or symbol
                        exch = quote.get('exchange', '')
                        
                        # Add to suggestions
                        suggestions.append({
                            'name': shortname,
                            'symbol': symbol,
                            'score': 0.9 if query.lower() in shortname.lower() or query.lower() in symbol.lower() else 0.7,
                            'exchange': exch
                        })
        except Exception as e:
            print(f"Yahoo API Search Error: {e}")
            
        return suggestions

    def search_stocks(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """Search for stocks using Yahoo API and local fuzzy matching"""
        
        # 1. Get API Suggestions
        api_results = self._search_yahoo_api(query)
        
        # 2. Get Local Fuzzy Suggestions
        local_suggestions = []
        normalized_query = self._normalize_query(query)
        
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
                
            if similarity > 0.4:  # Threshold
                local_suggestions.append({
                    'name': name.title(),
                    'symbol': symbol,
                    'score': similarity,
                    'exchange': 'NSE' if '.NS' in symbol else 'BSE'
                })
        
        # 3. Combine and Deduplicate
        # Create a dict by symbol to deduplicate, preferring higher score or API result
        combined = {}
        
        # Add local first
        for item in local_suggestions:
            combined[item['symbol']] = item
            
        # Add/Update with API results (API usually more accurate for broad queries)
        for item in api_results:
            sym = item['symbol']
            # If we have a local match for this symbol, average the scores or take max?
            # Let's trust API existence but maybe keep our local human-readable name if we prefer it?
            # For now, just overwrite or add
            if sym in combined:
                # If existing score is very high (exact match), keep it?
                # Actually, simply taking the max score is good standard
                 if item['score'] > combined[sym]['score']:
                     combined[sym] = item
            else:
                combined[sym] = item
        
        # Convert back to list
        final_list = list(combined.values())
        
        # Sort by score
        final_list.sort(key=lambda x: x['score'], reverse=True)
        
        return final_list[:limit]
    
    def get_stock_with_suggestions(self, query: str) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, str]]]:
        """Get stock data and also return similar stocks if not found"""
        # Try to get the exact stock
        stock_data = self.get_stock_data(query)
        
        # If found, return with empty suggestions
        if stock_data:
            return stock_data, []
            
        # If not found, run the robust search
        suggestions = self.search_stocks(query, limit=8)
        
        # Check if the top suggestion is a very strong match (e.g., exact symbol match from API)
        # If so, we could potentially auto-select it, but it's safer to show suggestions
        # unless query matches symbol exactly
        
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