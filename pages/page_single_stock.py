# pages/page_single_stock.py
import streamlit as st
from modules.display_components import (
    display_stock_info,
    display_buffett_analysis,
    display_buy_recommendation,
    display_technical_analysis
)

def main():
    st.markdown("<div class='premium-card'><h2>Single Stock Analysis</h2></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    with col1:
        ticker = st.text_input(
            "Enter stock symbol or company name",
            placeholder="TCS, RELIANCE, AAPL",
            label_visibility="collapsed"
        )
    with col2:
        analyze = st.button("Analyze Stock", type="primary", use_container_width=True)

    if analyze and ticker:
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
                            if st.button(f"{s['name']}\n({s['symbol']})", key=s['symbol']):
                                st.session_state.selected = s['symbol']
                                st.rerun()
                return

            # === DISPLAY RESULTS ===
            display_stock_info(stock_data)
            result = st.session_state.analyzer.analyze_stock(stock_data)
            display_buffett_analysis(result)
            display_buy_recommendation(result)
            display_technical_analysis(stock_data)

if __name__ == "__main__":
    main()