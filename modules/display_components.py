# modules/display_components.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import format_currency, get_status_emoji

def display_stock_info(stock_data: dict):
    """Beautiful stock header with live indicator"""
    market = st.session_state.data_fetcher.get_market_from_symbol(stock_data.get('symbol', ''))
    currency_code = stock_data.get('currency', 'INR')
    currency_symbol = st.session_state.data_fetcher.get_currency_symbol(currency_code, market)

    st.markdown("""
    <div class="stock-info-card card-3d">
        <div class="live-indicator">
            <div class="live-dot"></div>
            LIVE DATA
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Stock Overview")
    col1, col2, col3, col4 = st.columns(4)
    change = stock_data.get('change_percent', 0)
    price_class = "price-up" if change >= 0 else "price-down"

    with col1:
        st.metric("Current Price",
                  format_currency(stock_data.get('current_price', 0), currency=currency_symbol),
                  delta=f"{change:+.2f}%")
    with col2:
        st.metric("Market Cap",
                  format_currency(stock_data.get('market_cap', 0), currency=currency_symbol, is_large=True))
    with col3:
        st.metric("P/E Ratio", f"{stock_data.get('pe_ratio', 0):.2f}" if stock_data.get('pe_ratio') else "N/A")
    with col4:
        st.metric("52W High", format_currency(stock_data.get('fifty_two_week_high', 0), currency=currency_symbol))

    with st.expander("Detailed Company Information"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Company:** {stock_data.get('long_name', 'N/A')}")
            st.write(f"**Symbol:** {stock_data.get('symbol', 'N/A')}")
            st.write(f"**Exchange:** {stock_data.get('exchange', 'N/A')}")
        with col2:
            st.write(f"**Sector:** {stock_data.get('sector', 'N/A')}")
            st.write(f"**Industry:** {stock_data.get('industry', 'N/A')}")
            st.write(f"**Currency:** {currency_code} ({currency_symbol})")
            
            # Show Promoter Holding
            ph = stock_data.get('promoter_holding', 0)
            if ph > 0:
                st.write(f"**Promoter Holding:** {ph:.2f}%")
            else:
                st.write("**Promoter Holding:** N/A")
        if stock_data.get('business_summary'):
            st.markdown("**Business Summary (AI Analysis):**")
            # Use the new typewriter effect
            typewriter_text(stock_data['business_summary'], speed=10)

def display_buffett_analysis(analysis_result: dict):
    """15-Point Buffett Score"""
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card-3d'><h3>⚡ Buffett's 15-Point Analysis</h3></div>", unsafe_allow_html=True)

    score = analysis_result['total_score']
    percent = (score / 15) * 100
    grade = "Excellent" if percent >= 75 else "Good" if percent >= 60 else "Average" if percent >= 40 else "Poor"
    color = "🟢" if percent >= 75 else "🔵" if percent >= 60 else "🟡" if percent >= 40 else "🔴"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Score", f"{score}/15")
        st.markdown(f"<div class='score-progress'><div class='score-progress-fill' style='width:{percent}%'></div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='score-badge score-{grade.lower()}'>{color} {grade}</div>", unsafe_allow_html=True)
    # col3 removed as requested

    # Smart List UI
    st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
    for m in analysis_result['metrics']:
        icon = "✅" if m['passed'] else "❌"
        status_color = "var(--neon-green)" if m['passed'] else "var(--error)"
        glow = f"box-shadow: 0 0 10px {status_color};" if m['passed'] else ""
        
        # Format the HTML row
        html = f"""
        <div class="smart-row" style="border-right: 3px solid {status_color}">
            <div class="smart-label">
                {m['name']}
                <span class="smart-sub">Criteria: {m['criteria']}</span>
            </div>
            <div style="display:flex; align-items:center;">
                <span class="smart-value">{m['value']}</span>
                <span class="smart-icon" style="color: {status_color};">{icon}</span>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # DataFrame removed in favor of Smart UI
    # df = pd.DataFrame(metrics)
    # st.dataframe(df, use_container_width=True, hide_index=True)

    # Pie chart removed as requested

def display_buy_recommendation(analysis_result: dict):
    """Big beautiful recommendation card"""
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    rec = analysis_result['recommendation']
    status = rec['status']
    mos = rec.get('margin_of_safety', 0)

    if status == "Buy":
        card_class = "rec-buy"
        icon = "Strong Buy"
        text = "EXCELLENT BUYING OPPORTUNITY"
    elif status == "Hold":
        card_class = "rec-hold"
        icon = "Hold"
        text = "WAIT FOR BETTER PRICE"
    else:
        card_class = "rec-avoid"
        icon = "Avoid"
        text = "OVERVALUED – STAY AWAY"

    currency_symbol = rec.get('currency_symbol', '₹')

    st.markdown(f"<div class='card-3d {card_class}'><h2>{icon} {text}</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Price", format_currency(rec['current_price'], currency=currency_symbol))
    with col2:
        st.metric("Intrinsic Value", format_currency(rec['intrinsic_value'], currency=currency_symbol))
    with col3:
        st.metric("Margin of Safety", f"{mos:.1f}%", delta="Good" if mos > 20 else "Low")

    if status == "Buy":
        st.success(f"Buy Range: {format_currency(rec['buy_price_min'], currency=currency_symbol)} – {format_currency(rec['buy_price_max'], currency=currency_symbol)}")
    elif status == "Hold":
        st.info(f"Wait to buy below: {format_currency(rec.get('target_price', 0), currency=currency_symbol)}")

    # Methodology Explanation
    with st.expander("ℹ️ Methodology: How we calculate this?", expanded=False):
        st.markdown("""
        ### 📊 Valuation Methodology: Graham & Buffett Style
        
        Our **Intrinsic Value** is calculated using a conservative **Discounted Cash Flow (DCF)** model, inspired by **Warren Buffett** and **Benjamin Graham's** principles of value investing.
        
        #### 1. Intrinsic Value Calculation
        We believe a company's true value is the sum of all future cash flows it will generate, discounted back to present value.
        * **Free Cash Flow (FCF):** We prioritize FCF (Cash from Operations - Capex) over net income, as it represents the real cash available to owners.
        * **Growth Rate:** We use a conservative growth estimate based on historical earnings/FCF consistency, capped at 15% to avoid over-optimism.
        * **Discount Rate:** A 10% discount rate is applied (representing the minimum required return/opportunity cost).
        * **Terminal Value:** We assume a modest perpetual growth (2.5%) after 10 years.
        
        #### 2. Margin of Safety (MoS)
        * **Formula:** `(Intrinsic Value - Current Price) / Intrinsic Value`
        * **Why it matters:** Benjamin Graham's "Margin of Safety" is the secret to minimizing risk. We look for a gap between price and value to protect against analysis errors or market downturns.
        * **Our Threshold:** We look for a **20% Margin of Safety** before recommending a "Buy".
        
        #### 3. Buffett's MoS Criteria Guide
        <div class="smart-row" style="margin-top: 10px; flex-direction: column; align-items: flex-start; gap: 10px;">
            <div style="display: flex; justify-content: space-between; width: 100%; border-bottom: 1px solid var(--glass-border); padding-bottom: 5px;">
                <span style="color: var(--neon-green); font-weight: bold;">> 20%</span>
                <span>Safe to Buy (Excellent)</span>
            </div>
            <div style="display: flex; justify-content: space-between; width: 100%; border-bottom: 1px solid var(--glass-border); padding-bottom: 5px;">
                <span style="color: var(--neon-blue); font-weight: bold;">10% - 20%</span>
                <span>Good to Buy (Moderate Risk)</span>
            </div>
            <div style="display: flex; justify-content: space-between; width: 100%; border-bottom: 1px solid var(--glass-border); padding-bottom: 5px;">
                <span style="color: var(--neon-gold); font-weight: bold;">0% - 10%</span>
                <span>Fair Value (Hold)</span>
            </div>
             <div style="display: flex; justify-content: space-between; width: 100%;">
                <span style="color: var(--error); font-weight: bold;">< 0%</span>
                <span>Overvalued (Avoid)</span>
            </div>
        </div>

        *Note: This is a quantitative model and does not account for qualitative factors like management integrity or brand moat (though our 15-point checklist tries to capture some of this).*
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def display_technical_analysis(stock_data: dict):
    """Technical indicators Dashboard with Score"""
    """Technical indicators Dashboard with Score"""
    # Removed st.expander -> Visible by default
    st.markdown("### ⚡ Technical Analysis Dashboard")
    
    tech = st.session_state.analyzer.get_technical_indicators(stock_data)
    currency_symbol = stock_data.get('currency_symbol', '₹')
    
    score = tech.get('technical_score', 50)
    verdict = tech.get('verdict', 'Neutral')
    action = tech.get('action', 'HOLD')
    
    # 1. Score Gauge & Verdict
    col1, col2 = st.columns([1, 2])
    
    with col1:
            # Create Gauge Chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Technical Score", 'font': {'size': 24, 'color': '#8b9bb4'}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#8b9bb4"},
                'bar': {'color': "#2E2E2E"}, # Hide default bar, rely on steps or threshold
                'steps': [
                    {'range': [0, 40], 'color': 'rgba(220, 53, 69, 0.4)'},  # Red
                    {'range': [40, 60], 'color': 'rgba(255, 193, 7, 0.4)'}, # Yellow
                    {'range': [60, 80], 'color': 'rgba(23, 162, 184, 0.4)'}, # Cyan/Blue
                    {'range': [80, 100], 'color': 'rgba(40, 167, 69, 0.4)'} # Green
                ],
                'threshold': {
                    'line': {'color': "#fff", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=250, margin=dict(l=20,r=20,t=40,b=20))
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border-left: 5px solid {'#28a745' if score >= 80 else '#17a2b8' if score >= 60 else '#ffc107' if score >= 40 else '#dc3545'};">
            <h3 style="margin-top:0;">Verdict: <span style="color: {'#28a745' if score >= 80 else '#17a2b8' if score >= 60 else '#ffc107' if score >= 40 else '#dc3545'};">{verdict}</span></h3>
            <p style="color: #8b9bb4; font-size: 1.1rem; margin-top: 10px;">Based on Momentum (RSI, Stoch), Trend (SMA, EMA), and Volatility (BB).</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # 2. Detailed Indicators Grid - Expanded to 5 columns
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    with kpi1:
        st.metric("RSI (14)", f"{tech.get('rsi', 0):.1f}")
    with kpi2:
        st.metric("Stochastic", f"{tech.get('stoch_k', 0):.1f}")
    with kpi3:
        st.metric("MACD", f"{tech.get('macd', 0):.2f}")
    with kpi4:
        st.metric("Fast EMA (9)", f"{tech.get('ema_9', 0):.2f}")
    with kpi5:
        st.metric("Slow EMA (21)", f"{tech.get('ema_21', 0):.2f}")

def display_neon_chart(stock_data: dict):
    """
    3D Neon Glow Chart using Plotly
    """
    if 'history' not in stock_data or stock_data['history'] is None or stock_data['history'].empty:
        st.warning("No historical data available for chart.")
        return

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card-3d'><h3>⚡ Market Performance (1Y)</h3>", unsafe_allow_html=True)
    
    df = stock_data['history']
    
    # Create figure
    fig = go.Figure()

    # Add Glowing Area Chart
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='#00f3ff', width=3),  # Neon Blue Line
        fill='tozeroy',
        fillcolor='rgba(0, 243, 255, 0.1)'  # Faint blue glow under
    ))

    # Add Moving Averages for "Technical" feel
    if len(df) > 50:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'].rolling(window=50).mean(),
            mode='lines', name='50 SMA',
            line=dict(color='#ffd700', width=1, dash='dot') # Neon Gold
        ))

    # Dark Cyberpunk Layout
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(
            showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)',
            showline=False, zeroline=False
        ),
        yaxis=dict(
            showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)',
            showline=False, zeroline=False
        ),
        hovermode="x unified",
        font=dict(family="JetBrains Mono, monospace", color="#8b9bb4")
    )
    
    # Custom "Glow" effect via Marker Line (hacky but visually effective in JS, here we rely on line color)
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

def typewriter_text(text: str, speed: int = 20):
    """
    Displays text in a styled 'Cyberpunk Terminal' card using native Streamlit markdown.
    This avoids iframe layout issues and ensures full responsiveness.
    """
    safe_text = text.replace("\n", " ").strip()
    
    st.markdown(f"""
    <div class="terminal-card">
        <div class="terminal-header">
            <span class="terminal-dot red"></span>
            <span class="terminal-dot yellow"></span>
            <span class="terminal-dot green"></span>
            <span class="terminal-title">AI_ANALYSIS_Module_v2.0</span>
        </div>
        <div class="terminal-body">
            <p>{safe_text}<span class="cursor">_</span></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_advanced_metrics(analysis_result):
    """
    Displays the Piotroski F-Score, Graham Number, and Altman Z-Score
    in a styled "Pro Fundamentals" card.
    """
    adv = analysis_result.get('advanced_metrics', {})
    if not adv:
        return

    piotroski = adv.get('piotroski', {'score': 0})
    altman = adv.get('altman_z', {'score': 0}) # Explicitly defined

    # Logic for styling
    p_score = piotroski.get('score', 0)
    if p_score >= 7:
        p_color = "var(--neon-green)"
        p_label = "Strong"
    elif p_score >= 4:
        p_color = "var(--neon-gold)" 
        p_label = "Average"
    else:
        p_color = "var(--error)"
        p_label = "Weak"
        
    roic = adv.get('roic', 0)
    if roic > 15:
        r_color = "var(--neon-green)"
        r_label = "Excellent"
    elif roic > 10:
        r_color = "var(--neon-green)" # Still good
        r_label = "Good"
    elif roic > 0:
        r_color = "var(--neon-gold)"
        r_label = "Average"
    else:
        r_color = "var(--error)"
        r_label = "Poor"
    
    z_score = altman.get('score', 0)
    z_zone = altman.get('zone', 'Unknown')
    if z_score > 2.99:
        z_color = "var(--neon-green)"
        z_label = "Safe Zone"
    elif z_score > 1.8:
        z_color = "var(--neon-gold)"
        z_label = "Grey Zone"
    else:
        z_color = "var(--error)"
        z_label = "Distress Zone"
    
    st.markdown(f"""
<div class="card-3d" style="border-top: 3px solid var(--neon-purple);">
<h3 style="color: var(--neon-purple); margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
💎 Pro Fundamentals <span style="font-size: 0.7em; opacity: 0.7; border: 1px solid var(--neon-purple); border-radius: 4px; padding: 2px 6px;">INSTITUTIONAL GRADE</span>
</h3>


<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">

<!-- Piotroski F-Score -->
<div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; border-left: 3px solid {p_color};">
<div style="color: var(--text-dim); font-size: 0.9em;">Piotroski F-Score (0-9)</div>
<div style="font-size: 1.8em; font-weight: bold; color: {p_color}; font-family: var(--font-mono); margin: 5px 0;">
{p_score}/9 <span style="font-size: 0.5em; text-transform: uppercase;">{p_label}</span>
</div>
<div style="font-size: 0.75em; color: var(--text-dim); margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px;">
<span style="background: rgba(0,0,0,0.3); padding: 2px 5px; border-radius: 4px; font-family: monospace; color: var(--neon-blue);">Criteria: 7-9=Good, 0-3=Weak</span>
</div>
</div>

<!-- ROIC -->
<div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; border-left: 3px solid {r_color};">
<div style="color: var(--text-dim); font-size: 0.9em;">ROIC (Return on Capital)</div>
<div style="font-size: 1.8em; font-weight: bold; color: {r_color}; font-family: var(--font-mono); margin: 5px 0;">
{f"{roic:.2f}%"} <span style="font-size: 0.5em; text-transform: uppercase;">{r_label}</span>
</div>
<div style="font-size: 0.75em; color: var(--text-dim); margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px;">
<span style="background: rgba(0,0,0,0.3); padding: 2px 5px; border-radius: 4px; font-family: monospace; color: var(--neon-blue);">Criteria: &gt;10% Good, &gt;15% Great</span>
</div>
</div>

<!-- Altman Z-Score -->
<div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; border-left: 3px solid {z_color};">
<div style="color: var(--text-dim); font-size: 0.9em;">Altman Z-Score</div>
<div style="font-size: 1.8em; font-weight: bold; color: {z_color}; font-family: var(--font-mono); margin: 5px 0;">
{z_score} <span style="font-size: 0.5em; text-transform: uppercase;">{z_label}</span>
</div>
<div style="font-size: 0.75em; color: var(--text-dim); margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px;">
<span style="background: rgba(0,0,0,0.3); padding: 2px 5px; border-radius: 4px; font-family: monospace; color: var(--neon-blue);">Criteria: &gt; 3 Safe, &lt; 1.8 Risk</span>
</div>
</div>

</div>

<div style="margin-top: 20px;">
<details>
<summary style="cursor: pointer; color: var(--text-dim); font-size: 0.9em;">View Piotroski Details</summary>
<div style="margin-top: 10px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
{''.join([f'<div style="font-size: 0.85em; color: {"var(--neon-green)" if v else "var(--error)"};">{"✔" if v else "✘"} {k}</div>' for k, v in piotroski.get('details', {}).items()])}
</div>
</details>
</div>
</div>
""", unsafe_allow_html=True)