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
    <div class="stock-info-card">
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
        if stock_data.get('business_summary'):
            st.markdown("**Business:**")
            st.write(stock_data['business_summary'])

def display_buffett_analysis(analysis_result: dict):
    """16-Point Buffett Score + Pie Chart"""
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='premium-card'><h3>Buffett's 16-Point Analysis</h3></div>", unsafe_allow_html=True)

    score = analysis_result['total_score']
    percent = (score / 16) * 100
    grade = "Excellent" if percent >= 75 else "Good" if percent >= 60 else "Average" if percent >= 40 else "Poor"
    color = "🟢" if percent >= 75 else "🔵" if percent >= 60 else "🟡" if percent >= 40 else "🔴"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Score", f"{score}/16")
        st.markdown(f"<div class='score-progress'><div class='score-progress-fill' style='width:{percent}%'></div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='score-badge score-{grade.lower()}'>{color} {grade}</div>", unsafe_allow_html=True)
    with col3:
        st.metric("Passed Criteria", score, delta=f"{percent:.0f}%")

    # Detailed table
    metrics = []
    for m in analysis_result['metrics']:
        metrics.append({
            "Criteria": m['name'],
            "Value": m['value'],
            "Status": "Passed" if m['passed'] else "Failed",
            "Buffett Threshold": m['criteria']  # Show actual criteria instead of Yes/No
        })
    df = pd.DataFrame(metrics)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Pie chart
    passed = sum(1 for m in analysis_result['metrics'] if m['passed'])
    failed = 16 - passed
    fig = go.Figure(data=[go.Pie(labels=['Passed', 'Failed'], values=[passed, failed], hole=0.5,
                                 marker_colors=['#10b981', '#ef4444'])])
    fig.update_layout(title="Criteria Breakdown", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

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

    st.markdown(f"<div class='rec-card {card_class}'><h2>{icon} {text}</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Price", format_currency(rec['current_price']))
    with col2:
        st.metric("Intrinsic Value", format_currency(rec['intrinsic_value']))
    with col3:
        st.metric("Margin of Safety", f"{mos:.1f}%", delta="Good" if mos > 20 else "Low")

    if status == "Buy":
        st.success(f"Buy Range: {format_currency(rec['buy_price_min'])} – {format_currency(rec['buy_price_max'])}")
    elif status == "Hold":
        st.info(f"Wait to buy below: {format_currency(rec.get('target_price', 0))}")

    st.markdown("</div>", unsafe_allow_html=True)

def display_technical_analysis(stock_data: dict):
    """Technical indicators in expandable box"""
    with st.expander("Technical Analysis & Indicators", expanded=False):
        tech = st.session_state.analyzer.get_technical_indicators(stock_data)
        col1, col2, col3 = st.columns(3)
        with col1:
            rsi = tech.get('rsi', 50)
            rsi_status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
            st.metric("RSI (14)", f"{rsi:.1f}", delta=rsi_status)
        with col2:
            st.metric("50-Day SMA", format_currency(tech.get('sma_50', 0)))
        with col3:
            st.metric("200-Day SMA", format_currency(tech.get('sma_200', 0)))

        price = stock_data.get('current_price', 0)
        sma50 = tech.get('sma_50', 0)
        sma200 = tech.get('sma_200', 0)
        if price > sma50 > sma200:
            st.success("Strong Bullish Trend – Price above both SMAs")
        elif price > sma50:
            st.info("Moderate Uptrend")
        else:
            st.warning("Weak Trend or Downtrend")