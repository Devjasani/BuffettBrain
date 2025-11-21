import streamlit as st
from typing import Union

def format_currency(amount: Union[int, float], currency: str = "₹", is_large: bool = False) -> str:
    """Format currency with appropriate scaling for large numbers"""
    
    if amount == 0:
        return f"{currency}0"
    
    if is_large:
        if amount >= 1e12:  # Trillion
            return f"{currency}{amount/1e12:.2f}T"
        elif amount >= 1e9:  # Billion
            return f"{currency}{amount/1e9:.2f}B"
        elif amount >= 1e7:  # Crore
            return f"{currency}{amount/1e7:.2f}Cr"
        elif amount >= 1e5:  # Lakh
            return f"{currency}{amount/1e5:.2f}L"
        elif amount >= 1e3:  # Thousand
            return f"{currency}{amount/1e3:.2f}K"
    
    return f"{currency}{amount:,.2f}"

def format_percentage(value: Union[int, float], decimal_places: int = 2) -> str:
    """Format percentage values"""
    if value == 0:
        return "0%"
    return f"{value:.{decimal_places}f}%"

def get_status_emoji(status: str) -> str:
    """Get emoji based on status"""
    status_map = {
        'good': '✅',
        'caution': '⚠️',
        'poor': '❌'
    }
    return status_map.get(status.lower(), '❓')

def get_recommendation_color(recommendation: str) -> str:
    """Get color code for recommendation"""
    color_map = {
        'buy': '#28a745',    # Green
        'hold': '#ffc107',   # Yellow
        'avoid': '#dc3545'   # Red
    }
    return color_map.get(recommendation.lower(), '#6c757d')

def calculate_score_grade(score: int, total: int = 16) -> tuple:
    """Calculate grade and color based on score"""
    percentage = (score / total) * 100
    
    if percentage >= 75:
        return "Excellent", "#28a745"
    elif percentage >= 60:
        return "Good", "#17a2b8"
    elif percentage >= 40:
        return "Average", "#ffc107"
    else:
        return "Poor", "#dc3545"

def display_metric_tooltip(metric_name: str) -> str:
    """Get tooltip text for metrics"""
    tooltips = {
        'Return on Equity (ROE)': 'Measures how efficiently a company uses shareholders equity to generate profit. Higher is better.',
        'Debt-to-Equity Ratio': 'Compares total debt to shareholder equity. Lower ratios indicate less financial risk.',
        'Current Ratio': 'Measures ability to pay short-term obligations. Above 1.5 indicates healthy liquidity.',
        'Book Value Per Share': 'Company\'s equity divided by shares outstanding. Buying below book value can indicate undervaluation.',
        'Price-to-Earnings (P/E) Ratio': 'Price per share divided by earnings per share. Lower ratios may indicate undervaluation.',
        'Price-to-Book (P/B) Ratio': 'Market price per share divided by book value per share. Below 1.5 suggests undervaluation.',
        'Intrinsic Value vs Market Price': 'Comparison of calculated fair value to current market price. Discount indicates potential bargain.',
        'Operating Profit Margin (OPM)': 'Operating income as percentage of revenue. Higher margins indicate efficient operations.',
        'Revenue vs Profit Growth': 'Alignment between revenue and profit growth rates. Should grow together sustainably.',
        'Return on Capital Employed (ROCE)': 'Efficiency of capital usage. Higher ROCE indicates better management of capital.',
        'PEG Ratio': 'P/E ratio divided by earnings growth rate. Below 1.0 may indicate undervaluation relative to growth.',
        'Earnings Growth': 'Annual growth rate of company earnings. Consistent growth above 8-10% is considered good.',
        'Consistent Earnings': 'Stability of earnings over time. Less volatility indicates more predictable business.',
        'Free Cash Flow': 'Cash generated after capital expenditures. Positive and growing FCF is crucial for value investing.',
        'Dividend History': 'Track record of dividend payments. Consistent dividends indicate financial stability.',
        'Promoter Holding & Pledging': 'Percentage owned by founders/promoters and how much is pledged. High holding with low pledging is preferred.'
    }
    
    return tooltips.get(metric_name, 'No description available')

def format_financial_statement_item(value: Union[int, float], item_type: str = 'currency') -> str:
    """Format financial statement items appropriately"""
    
    if value == 0 or value is None:
        return "N/A"
    
    if item_type == 'currency':
        return format_currency(value, is_large=True)
    elif item_type == 'percentage':
        return format_percentage(value)
    elif item_type == 'ratio':
        return f"{value:.2f}"
    else:
        return str(value)

def get_buffett_quote() -> str:
    """Get a random Warren Buffett quote for inspiration"""
    quotes = [
        "Price is what you pay. Value is what you get.",
        "Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1.",
        "It's far better to buy a wonderful company at a fair price than a fair company at a wonderful price.",
        "The stock market is designed to transfer money from the active to the patient.",
        "Risk comes from not knowing what you're doing.",
        "Someone's sitting in the shade today because someone planted a tree a long time ago.",
        "The most important investment you can make is in yourself.",
        "Our favorite holding period is forever.",
        "Buy a stock the way you would buy a house. Understand and like it such that you'd be content to own it in the absence of any market.",
        "Time is the friend of the wonderful company, the enemy of the mediocre."
    ]
    
    import random
    return random.choice(quotes)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_stock_data(symbol: str):
    """Cache wrapper for stock data to reduce API calls"""
    # This would be used with the actual data fetching function
    pass

def validate_stock_input(input_text: str) -> bool:
    """Validate stock input format"""
    if not input_text or len(input_text.strip()) < 2:
        return False
    
    # Check for valid characters (alphanumeric, dots, hyphens)
    import re
    pattern = r'^[a-zA-Z0-9\.\-\s]+$'
    return bool(re.match(pattern, input_text.strip()))

def create_comparison_chart_data(comparison_data: list) -> dict:
    """Prepare data for comparison charts"""
    
    chart_data = {
        'stocks': [],
        'scores': [],
        'prices': [],
        'market_caps': [],
        'pe_ratios': []
    }
    
    for data in comparison_data:
        stock_data = data['stock_data']
        analysis = data['analysis']
        
        chart_data['stocks'].append(stock_data.get('symbol', 'N/A'))
        chart_data['scores'].append(analysis['total_score'])
        chart_data['prices'].append(stock_data.get('current_price', 0))
        chart_data['market_caps'].append(stock_data.get('market_cap', 0))
        chart_data['pe_ratios'].append(stock_data.get('pe_ratio', 0))
    
    return chart_data
