import numpy as np

def calculate_reverse_dcf(current_price, free_cash_flow, shares_outstanding, discount_rate=0.10, terminal_growth_rate=0.025, projection_years=10):
    """
    Reverse DCF: Calculate the implied growth rate required to justify the current stock price.
    
    Formula: Find 'g' such that DCF(g) = Current Price
    """
    if current_price <= 0 or free_cash_flow <= 0 or shares_outstanding <= 0:
        return None
        
    fcf_per_share = free_cash_flow / shares_outstanding
    
    # Binary search for the growth rate
    low = -0.50  # -50% growth
    high = 1.00  # 100% growth
    tolerance = 0.01 # 1 cent
    
    for _ in range(100): # Max iterations
        mid = (low + high) / 2
        implied_value = _calculate_dcf_value(fcf_per_share, mid, discount_rate, terminal_growth_rate, projection_years)
        
        if abs(implied_value - current_price) < tolerance:
            return mid * 100 # Return as percentage
        
        if implied_value < current_price:
            low = mid
        else:
            high = mid
            
    return mid * 100

def _calculate_dcf_value(fcf, growth_rate, discount_rate, terminal_growth_rate, years):
    total_pv = 0
    current_fcf = fcf
    
    # Projection phase
    for i in range(1, years + 1):
        current_fcf = current_fcf * (1 + growth_rate)
        pv = current_fcf / ((1 + discount_rate) ** i)
        total_pv += pv
        
    # Terminal value
    terminal_fcf = current_fcf * (1 + terminal_growth_rate)
    terminal_val = terminal_fcf / (discount_rate - terminal_growth_rate)
    terminal_pv = terminal_val / ((1 + discount_rate) ** years)
    
    return total_pv + terminal_pv
