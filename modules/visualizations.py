import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_radar_chart(analysis_results: dict):
    """
    Create a 5-axis Radar Chart ("Buffett's Eye") to visualize stock health.
    Axes: Value, Quality, Stability, Growth, Moat
    """
    
    # Extract metrics and normalize to 0-100 scale based on criteria
    metrics = analysis_results.get('metrics', [])
    
    # 1. VALUE (P/E, P/B, Intrinsic Value)
    value_score = 0
    value_count = 0
    for m in metrics:
        if m['name'] in ['Price-to-Earnings (P/E) Ratio', 'Price-to-Book (P/B) Ratio', 'Intrinsic Value vs Market Price']:
            value_count += 1
            if m['passed']: value_score += 100
            elif m['status'] == 'caution': value_score += 50
    value_final = value_score / value_count if value_count else 0
    
    # 2. QUALITY (ROE, ROCE, OPM)
    quality_score = 0
    quality_count = 0
    for m in metrics:
        if m['name'] in ['Return on Equity (ROE)', 'Return on Capital Employed (ROCE)', 'Operating Profit Margin (OPM)']:
            quality_count += 1
            if m['passed']: quality_score += 100
            elif m['status'] == 'caution': quality_score += 50
    quality_final = quality_score / quality_count if quality_count else 0
    
    # 3. STABILITY (Debt, Current Ratio, Earnings Consistency)
    stability_score = 0
    stability_count = 0
    for m in metrics:
        if m['name'] in ['Debt-to-Equity Ratio', 'Current Ratio', 'Consistent Earnings']:
            stability_count += 1
            if m['passed']: stability_score += 100
            elif m['status'] == 'caution': stability_score += 50
    stability_final = stability_score / stability_count if stability_count else 0
    
    # 4. GROWTH (Earnings Growth, Revenue Growth/Alignment, PEG)
    growth_score = 0
    growth_count = 0
    for m in metrics:
        if m['name'] in ['Earnings Growth', 'Revenue vs Profit Growth', 'PEG Ratio']:
            growth_count += 1
            if m['passed']: growth_score += 100
            elif m['status'] == 'caution': growth_score += 50
    growth_final = growth_score / growth_count if growth_count else 0
    
    # 5. MOAT (FCF, Dividend, Promoter)
    moat_score = 0
    moat_count = 0
    for m in metrics:
        if m['name'] in ['Free Cash Flow', 'Dividend History']: # Promoter holding often missing, stick to reliable ones
            moat_count += 1
            if m['passed']: moat_score += 100
            elif m['status'] == 'caution': moat_score += 50
    moat_final = moat_score / moat_count if moat_count else 0
    
    categories = ['Value', 'Quality', 'Stability', 'Growth', 'Moat']
    values = [value_final, quality_final, stability_final, growth_final, moat_final]
    
    # Close the loop
    categories = [*categories, categories[0]]
    values = [*values, values[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Stock Score',
        line_color='#3b82f6',
        fillcolor='rgba(59, 130, 246, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                linecolor='rgba(255, 255, 255, 0.1)',
                gridcolor='rgba(255, 255, 255, 0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#94a3b8'),
                linecolor='rgba(255, 255, 255, 0.1)',
                gridcolor='rgba(255, 255, 255, 0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=20),
        height=300
    )
    
    return fig
