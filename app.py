import streamlit as st
from auth import check_password

# Add authentication at the very top
if not check_password():
    st.stop()  # Stop execution if not authenticated

# Page configuration
st.set_page_config(
    page_title="BuffettBrain",
    page_icon="📈",
    layout="wide"
)

# Load CSS
from css_loader import load_css
load_css()

# Initialize session state
if 'data_fetcher' not in st.session_state:
    from data_fetcher import DataFetcher
    st.session_state.data_fetcher = DataFetcher()
if 'analyzer' not in st.session_state:
    from stock_analyzer import StockAnalyzer
    st.session_state.analyzer = StockAnalyzer()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# Main title
st.markdown("<div class='main-header'><h1>📈 BuffettBrain</h1></div>", unsafe_allow_html=True)

# Clean sidebar with only essential items
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    
    # Simple page selection
    if st.button("🔍 Single Stock Analysis", use_container_width=True):
        st.session_state.page = "single"
        st.rerun()
    
    if st.button("⚖️ Stock Comparison", use_container_width=True):
        st.session_state.page = "comparison"
        st.rerun()

# Set default page
if 'page' not in st.session_state:
    st.session_state.page = "single"

# Page routing
if st.session_state.page == "single":
    from pages.page_single_stock import main
    main()
elif st.session_state.page == "comparison":
    from pages.page_comparison import main
    main()