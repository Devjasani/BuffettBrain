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

def calculate_score_grade(score: int, total: int = 15) -> tuple:
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


def validate_stock_input(input_text: str) -> bool:
    """Validate stock input format"""
    if not input_text or len(input_text.strip()) < 2:
        return False
    
    # Check for valid characters (alphanumeric, dots, hyphens)
    import re
    pattern = r'^[a-zA-Z0-9\.\-\s]+$'
    return bool(re.match(pattern, input_text.strip()))


