# pages/page_single_stock.py
import streamlit as st
from modules.display_components import (
    display_stock_info,
    display_buffett_analysis,
    display_buy_recommendation,
    display_technical_analysis,
    display_advanced_metrics
)


def main():
    # Professional Hero Section
    st.markdown("""
    <style>
    .hero-container {
        padding: 20px 20px; /* Reduced padding */
        text-align: center;
        background: radial-gradient(circle at center, rgba(0,243,255,0.05) 0%, rgba(0,0,0,0) 70%); /* Subtler gradient */
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .hero-title {
        font-size: 2.2rem; /* Reduced from 3rem */
        font-weight: 700;
        background: linear-gradient(90deg, #fff, #8b9bb4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 10px;
    }
    .dynamic-sub {
        font-family: var(--font-mono);
        font-size: 0.8rem;
        color: var(--neon-blue);
        opacity: 0.8;
    }
    </style>
    
    <div class="hero-container">
        <h1 class="hero-title">Intelligent Stock Analysis</h1>
        <p class="hero-subtitle">Institutional-grade valuation & fundamentals at your fingertips</p>
        <div class="dynamic-sub">
            Find stock fundamentals of India, USA, UK, Canada, Germany, Japan, Australia 🌍
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    # Initialize session state for robust search box handling
    if 'search_key_id' not in st.session_state:
        st.session_state.search_key_id = 0
    if 'ticker_input' not in st.session_state:
        st.session_state.ticker_input = ""

    # Callback to handle suggestion click
    def select_stock(symbol):
        # Update the value we want in the box
        st.session_state.ticker_input = symbol
        # Increment key ID to force completley new widget render
        st.session_state.search_key_id += 1
        st.session_state.auto_run_analysis = True
        # Explicitly trigger rerun for consistent behavior in deployment
        st.rerun()

    # Check for auto-run flag
    if st.session_state.get('auto_run_analysis', False):
        auto_run = True
        st.session_state.auto_run_analysis = False # Reset flag
    else:
        auto_run = False

    with col1:
        # We use a dynamic key to support "resetting" the widget from code
        # When search_key_id changes, this is treated as a brand new widget,
        # so it ignores previous frontend state and uses 'value' argument.
        ticker = st.text_input(
            "Enter stock symbol or company name",
            value=st.session_state.ticker_input,
            placeholder="Search Stock (e.g., TCS, RELIANCE, AAPL)...",
            label_visibility="collapsed",
            key=f"search_box_{st.session_state.search_key_id}"
        )
        
        # Sync the widget value back to session state variable for next re-renders (if user types)
        if ticker != st.session_state.ticker_input:
             st.session_state.ticker_input = ticker
             
    with col2:
        analyze = st.button("Analyze Stock", type="primary", use_container_width=True)

    if (analyze or auto_run) and ticker:
        with st.spinner("Fetching live data and analyzing..."):
            # Directly use session_state without re-initialization
            stock_data, suggestions = st.session_state.data_fetcher.get_stock_with_suggestions(ticker)

            if not stock_data:
                st.error("Stock not found or invalid symbol")
                if suggestions:
                    st.info("Did you mean one of these?")
                    cols = st.columns(3)
                    for i, s in enumerate(suggestions[:3]):
                        with cols[i]:
                            # Use callback for reliable state update
                            st.button(
                                f"{s['name']}\n({s['symbol']})", 
                                key=f"{s['symbol']}_{i}",
                                on_click=select_stock,
                                args=(s['symbol'],)
                            )
                return

            # === DISPLAY RESULTS ===
            display_stock_info(stock_data)
            
            # Analyze stock FIRST to get result
            result = st.session_state.analyzer.analyze_stock(stock_data)
            
            # Phase 2: Neon Chart
            from modules.display_components import display_neon_chart
            display_neon_chart(stock_data)

            # Radar Chart
            st.markdown("### 🕸️ 5-Point Health Check")
            from modules.visualizations import create_radar_chart
            radar_fig = create_radar_chart(result)
            st.plotly_chart(radar_fig, use_container_width=True)

            display_buffett_analysis(result)
            display_advanced_metrics(result)
            
            display_buy_recommendation(result)
            display_technical_analysis(stock_data)

if __name__ == "__main__":
    main()
