# pages/page_comparison.py
import streamlit as st
from stock_analyzer import StockAnalyzer
from data_fetcher import DataFetcher
import plotly.express as px
import pandas as pd

# ====================== INITIALIZE ======================
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = StockAnalyzer()
if 'data_fetcher' not in st.session_state:
    st.session_state.data_fetcher = DataFetcher()

# ====================== MAIN FUNCTION ======================
def main():
    st.markdown("<div class='premium-card'><h2>Stock Comparison</h2></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        stock1 = st.text_input("Stock 1", placeholder="e.g. TCS", key="comp1")
    with col2:
        stock2 = st.text_input("Stock 2", placeholder="e.g. INFY", key="comp2")
    with col3:
        stock3 = st.text_input("Stock 3 (optional)", placeholder="e.g. HDFCBANK", key="comp3")

    stocks_to_compare = [s.strip().upper() for s in [stock1, stock2, stock3] if s.strip()]

    if st.button("Compare Stocks", type="primary") and len(stocks_to_compare) >= 2:
        with st.spinner("Fetching and comparing..."):
            results = []
            for symbol in stocks_to_compare:
                data = st.session_state.data_fetcher.get_stock_data(symbol)
                if data:
                    analysis = st.session_state.analyzer.analyze_stock(data)
                    rec = "Strong Buy" if analysis['recommendation']['status'] == "Buy" else "Hold/Avoid"
                    results.append({
                        "Symbol": data['symbol'],
                        "Company": data.get('short_name', 'N/A'),
                        "Price": f"₹{data.get('current_price', 0):,.2f}",
                        "Buffett Score": f"{analysis['total_score']}/16",
                        "Recommendation": rec,
                        "P/E": f"{data.get('pe_ratio', 0):.1f}" if data.get('pe_ratio') else "N/A",
                        "ROE": f"{data.get('return_on_equity', 0):.1f}%" if data.get('return_on_equity') else "N/A"
                    })

            if results:
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)

                # Beautiful bar chart
                scores = [int(r["Buffett Score"].split("/")[0]) for r in results]
                symbols = [r["Symbol"] for r in results]
                fig = px.bar(
                    x=symbols,
                    y=scores,
                    text=scores,
                    color=scores,
                    color_continuous_scale="Viridis",
                    title="Buffett Score Comparison"
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data found for the entered stocks.")

# ====================== RUN MAIN ======================
if __name__ == "__main__":
    main()   # ← This line must be indented with 4 spaces!