import pandas as pd
import numpy as np

class FundamentalIndicators:
    """
    Calculates advanced fundamental metrics:
    1. Piotroski F-Score (0-9) - Financial Health
    2. Graham Number - Fair Value
    3. Altman Z-Score - Bankruptcy Risk
    """
    
    def get_piotroski_f_score(self, financials: pd.DataFrame, balance_sheet: pd.DataFrame, cash_flow: pd.DataFrame) -> dict:
        """
        Calculates Piotroski F-Score (0-9).
        Returns a dictionary with the score and the breakdown of passes.
        """
        score = 0
        details = {}
        
        try:
            if financials.empty or balance_sheet.empty or cash_flow.empty:
                return {'score': 0, 'details': {}}

            # Get latest two years columns, explicitly SORTED by date descending (Newest First)
            cols = sorted(financials.columns, reverse=True)
            if len(cols) < 2:
                return {'score': 0, 'details': {}}
            
            t = cols[0]   # Current Year
            t_1 = cols[1] # Previous Year
            
            # Helper for safe extraction
            def get_val(df, row, col):
                if row in df.index:
                    val = df.loc[row, col]
                    return 0 if pd.isna(val) else val
                return 0
            
            # --- PROFITABILITY (4 points) ---
            
            # 1. ROA > 0
            net_income = get_val(financials, 'Net Income', t)
            total_assets = get_val(balance_sheet, 'Total Assets', t) or 1 # Avoid div by zero
            total_assets_prev = get_val(balance_sheet, 'Total Assets', t_1) or total_assets
            avg_assets = (total_assets + total_assets_prev) / 2
            roa = net_income / avg_assets if avg_assets else 0
            
            if roa > 0:
                score += 1
                details['Positive ROA'] = True
            else:
                details['Positive ROA'] = False
                
            # 2. Operating Cash Flow > 0
            # 2. Operating Cash Flow > 0
            ocf = get_val(cash_flow, 'Total Cash From Operating Activities', t)
            if ocf > 0:
                score += 1
                details['Positive OCF'] = True
            else:
                details['Positive OCF'] = False
                
            # 3. ROA Increasing (Current ROA > Prev ROA)
            # 3. ROA Increasing (Current ROA > Prev ROA)
            net_income_prev = get_val(financials, 'Net Income', t_1)
            # total_assets_prev already fetched above
            roa_prev = net_income_prev / total_assets_prev if total_assets_prev else 0
            
            if roa > roa_prev:
                score += 1
                details['ROA Increasing'] = True
            else:
                details['ROA Increasing'] = False
                
            # 4. Accruals (OCF > Net Income)
            if ocf > net_income:
                score += 1
                details['Quality of Earnings (OCF > NI)'] = True
            else:
                details['Quality of Earnings (OCF > NI)'] = False
                
            # --- LEVERAGE, LIQUIDITY, SOURCE OF FUNDS (3 points) ---
            
            # 5. Lower Leverage (Long Term Debt / Avg Assets) < Prev Year
            # 5. Lower Leverage (Long Term Debt / Avg Assets) < Prev Year
            lt_debt = get_val(balance_sheet, 'Long Term Debt', t)
            lt_debt_prev = get_val(balance_sheet, 'Long Term Debt', t_1)
            
            leverage = lt_debt / avg_assets if avg_assets else 0
            leverage_prev = lt_debt_prev / total_assets_prev if total_assets_prev else 0
            
            if leverage <= leverage_prev:
                score += 1
                details['Lower Leverage'] = True
            else:
                details['Lower Leverage'] = False
                
            # 6. Higher Current Ratio
            # 6. Higher Current Ratio
            curr_assets = get_val(balance_sheet, 'Current Assets', t)
            curr_liab = get_val(balance_sheet, 'Current Liabilities', t)
            curr_ratio = curr_assets / curr_liab if curr_liab else 0
            
            curr_assets_prev = get_val(balance_sheet, 'Current Assets', t_1)
            curr_liab_prev = get_val(balance_sheet, 'Current Liabilities', t_1)
            curr_ratio_prev = curr_assets_prev / curr_liab_prev if curr_liab_prev else 0
            
            if curr_ratio > curr_ratio_prev:
                score += 1
                details['Higher Liquidity (Current Ratio)'] = True
            else:
                details['Higher Liquidity (Current Ratio)'] = False

            # 7. No New Shares (Dilution Check)
            # Hard to get exact shares issued from standard bs/cf, use Ord Shares check or Common Stock
            # 7. No New Shares (Dilution Check)
            shares = get_val(balance_sheet, 'Ordinary Shares Number', t) or get_val(balance_sheet, 'Common Stock', t)
            shares_prev = get_val(balance_sheet, 'Ordinary Shares Number', t_1) or get_val(balance_sheet, 'Common Stock', t_1)
            
            if shares <= shares_prev: # No dilution
                score += 1
                details['No Dilution'] = True
            else:
                details['No Dilution'] = False
                
            # --- OPERATING EFFICIENCY (2 points) ---
            
            # 8. Higher Gross Margin
            # 8. Higher Gross Margin
            revenue = get_val(financials, 'Total Revenue', t)
            gross_profit = get_val(financials, 'Gross Profit', t)
            gm = gross_profit / revenue if revenue else 0
            
            revenue_prev = get_val(financials, 'Total Revenue', t_1)
            gross_profit_prev = get_val(financials, 'Gross Profit', t_1)
            gm_prev = gross_profit_prev / revenue_prev if revenue_prev else 0
            
            if gm > gm_prev:
                score += 1
                details['Higher Gross Margin'] = True
            else:
                details['Higher Gross Margin'] = False
                
            # 9. Higher Asset Turnover
            asset_turnover = revenue / avg_assets if avg_assets else 0
            asset_turnover_prev = revenue_prev / total_assets_prev if total_assets_prev else 0
            
            if asset_turnover > asset_turnover_prev:
                score += 1
                details['Higher Asset Turnover'] = True
            else:
                details['Higher Asset Turnover'] = False
                
        except Exception as e:
            print(f"Error calculating Piotroski Score: {e}")
            
        return {'score': score, 'details': details}

    def get_roic(self, financials: pd.DataFrame, balance_sheet: pd.DataFrame) -> float:
        """
        Calculates ROIC (Return on Invested Capital).
        Formula: Net Income / (Total Equity + Long Term Debt)
        Returns a percentage value (e.g., 15.5 for 15.5%)
        """
        try:
            # Sort columns to ensure we get appropriate year
            cols = sorted(financials.columns, reverse=True)
            if not cols: return 0
            t = cols[0]

            # Helper for safe extraction (re-used logic)
            def get_val(df, row, col):
                if row in df.index:
                    val = df.loc[row, col]
                    return 0 if pd.isna(val) else val
                return 0

            net_income = get_val(financials, 'Net Income', t)
            equity = get_val(balance_sheet, 'Total Stockholder Equity', t) or get_val(balance_sheet, 'Stockholders Equity', t)
            debt = get_val(balance_sheet, 'Long Term Debt', t) or get_val(balance_sheet, 'Total Debt', t)
            
            invested_capital = equity + debt
            
            if invested_capital == 0:
                return 0
                
            return (net_income / invested_capital) * 100
        except Exception as e:
            print(f"Error calculating ROIC: {e}")
            return 0

    def get_altman_z_score(self, financials: pd.DataFrame, balance_sheet: pd.DataFrame, market_cap: float) -> dict:
        """
        Calculates Altman Z-Score for Bankruptcy Prediction.
        Formula (General): 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
        A = Working Capital / Total Assets
        B = Retained Earnings / Total Assets
        C = EBIT / Total Assets
        D = Market Value of Equity / Total Liabilities
        E = Sales / Total Assets
        """
        try:
            if financials.empty or balance_sheet.empty:
                return {'score': 0, 'zone': 'Unknown'}

            cols = financials.columns
            t = cols[0]
            
            total_assets = balance_sheet.loc['Total Assets', t] if 'Total Assets' in balance_sheet.index else 0
            if not total_assets: return {'score': 0, 'zone': 'Unknown'}
            
            curr_assets = balance_sheet.loc['Current Assets', t] if 'Current Assets' in balance_sheet.index else 0
            curr_liab = balance_sheet.loc['Current Liabilities', t] if 'Current Liabilities' in balance_sheet.index else 0
            working_capital = curr_assets - curr_liab
            
            retained_earnings = balance_sheet.loc['Retained Earnings', t] if 'Retained Earnings' in balance_sheet.index else 0
            
            ebit = financials.loc['EBIT', t] if 'EBIT' in financials.index else (
                   financials.loc['Pretax Income', t] + financials.loc['Interest Expense', t] if 'Interest Expense' in financials.index else financials.loc['Pretax Income', t])
            
            total_liab = balance_sheet.loc['Total Liabilities Net Minority Interest', t] if 'Total Liabilities Net Minority Interest' in balance_sheet.index else (
                         balance_sheet.loc['Total Liabilities', t] if 'Total Liabilities' in balance_sheet.index else 0)
            
            sales = financials.loc['Total Revenue', t] if 'Total Revenue' in financials.index else 0
            
            # Components
            A = working_capital / total_assets
            B = retained_earnings / total_assets
            C = ebit / total_assets
            D = market_cap / total_liab if total_liab else 0
            E = sales / total_assets
            
            # Z-Score Formula
            z_score = (1.2 * A) + (1.4 * B) + (3.3 * C) + (0.6 * D) + (1.0 * E)
            
            # Zones
            if z_score > 2.99:
                zone = "Safe (Green)"
            elif z_score > 1.81:
                zone = "Grey Zone (Caution)"
            else:
                zone = "Distress (Red)"
                
            return {'score': round(z_score, 2), 'zone': zone}
            
        except Exception as e:
            print(f"Error calculating Altman Z: {e}")
            return {'score': 0, 'zone': 'Unknown'}
