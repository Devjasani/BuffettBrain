import streamlit as st

# Page configuration
st.set_page_config(
    page_title="BuffettBrain",
    page_icon="📈",
    layout="wide"
)

# Load CSS
from css_loader import load_css
load_css()

# Initialize session state with cached resources
@st.cache_resource
def get_data_fetcher():
    from data_fetcher import DataFetcher
    return DataFetcher()

@st.cache_resource
def get_analyzer():
    from stock_analyzer import StockAnalyzer
    return StockAnalyzer()

if 'data_fetcher' not in st.session_state:
    st.session_state.data_fetcher = get_data_fetcher()
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = get_analyzer()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# Main Header & Layout
# Fetch live index data
if 'market_indices' not in st.session_state:
    st.session_state.market_indices = st.session_state.data_fetcher.get_market_indices()

# Generate HTML for ticker dynamically
ticker_html_items = ""
for item in st.session_state.market_indices:
    color_class = "ticker-up" if item['change'] >= 0 else "ticker-down"
    arrow = "▲" if item['change'] >= 0 else "▼"
    price_fmt = f"{item['currency']}{item['price']:,.2f}"
    change_fmt = f"{arrow} {abs(item['change']):.2f}%"
    ticker_html_items += f"""<div class="ticker__item"><span class="ticker-symbol">{item['name']}</span> <span class="{color_class}">{price_fmt} {change_fmt}</span></div>"""

# Duplicate for infinite scroll
ticker_full_html = ticker_html_items + ticker_html_items

st.markdown(f"""
<div class="ticker-wrap">
<div class="ticker">
  {ticker_full_html}
</div>
</div>
""", unsafe_allow_html=True)

# Load logos
import base64

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

user_logo_b64 = get_base64_of_bin_file("Logo/Logo - Copy.png")

# Header
st.markdown(f"""
<div class="glass-header">
<div class="header-top-row">
<div class="logo-group">
<!-- Company Logo -->
<div class="logo-container">
<img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Chart%20Increasing.png" width="45">
</div>
<div>
<h1 class="header-title">BuffettBrain <span class="beta-badge">BETA</span></h1>
</div>
</div>
<div class="status-pill success" style="margin-top: 0;">● System Online</div>
</div>
<div class="header-notes-box">
<div class="note-item">
<span class="note-label">IMPORTANT:</span>
<span>Use exact <strong>Stock Ticker Name</strong> (e.g., RELIANCE.NS).</span>
</div>
<div class="note-item">
<span>This site is a <strong>Beta Version</strong> following Buffett & Graham principles. <strong>Not a recommendation.</strong></span>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# Removed: INITIALIZING QUANT DATA STREAMS block as requested


# Clean sidebar with only essential items
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    
    # Simple page selection
    if st.button("🔍 Single Stock Analysis", use_container_width=True):
        st.session_state.page = "single"
        st.rerun()
    


# Set default page
if 'page' not in st.session_state:
    st.session_state.page = "single"

# Page routing
if st.session_state.page == "single":
    from pages.page_single_stock import main
    main()


# Footer (Static at bottom)
user_img_tag = f'<img src="data:image/png;base64,{user_logo_b64}" style="height: 30px; width: 30px; border-radius: 50%; vertical-align: middle; border: 1px solid var(--neon-blue); box-shadow: 0 0 5px var(--neon-blue); margin-left: 8px;">' if user_logo_b64 else ""

st.markdown(f"""
<style>
.app-footer {{
    width: 100%;
    background: rgba(15, 23, 42, 0.98);
    border-top: 1px solid var(--neon-blue);
    color: var(--text-dim);
    text-align: center;
    padding: 30px 20px;
    font-size: 0.85rem;
    margin-top: 60px;
    backdrop-filter: blur(10px);
    box-shadow: 0 -5px 20px rgba(0,0,0,0.5);
}}
.app-footer p {{ margin: 0; line-height: 1.6; }}
</style>
<div class="app-footer">
<p style="margin-bottom: 8px;">
<span style="color: #fff; font-weight: bold;">Creator of site:</span> <span style="color: var(--neon-blue); font-weight: bold; font-size: 1rem;">Dev Jasani</span> {user_img_tag}
</p>

<!-- Social Links -->
<div style="display: flex; justify-content: center; gap: 15px; margin: 15px 0;">
<a href="https://dev-jasani.netlify.app/" target="_blank" style="text-decoration: none;">
<img src="https://img.icons8.com/fluency/48/domain.png" width="30" height="30" title="Portfolio">
</a>
<a href="https://www.linkedin.com/in/dev-jasani-263dj/" target="_blank" style="text-decoration: none;">
<img src="https://img.icons8.com/fluency/48/linkedin.png" width="30" height="30" title="LinkedIn">
</a>
<a href="https://www.instagram.com/_d.jasani_/" target="_blank" style="text-decoration: none;">
<img src="https://img.icons8.com/fluency/48/instagram-new.png" width="30" height="30" title="Instagram">
</a>
<a href="https://medium.com/@devjas263" target="_blank" style="text-decoration: none;">
<img src="https://img.icons8.com/fluency/48/medium-logo.png" width="30" height="30" title="Medium">
</a>
</div>

<p style="font-size: 0.75rem; opacity: 0.8;">
<span style="color: var(--neon-gold);">⚠️ NOTICE:</span> Beta version, fetching live data. 
Do not use score as recommendation. It is just used to identify <span style="color: #fff;">Quality Stock</span>.<br>
<span style="color: var(--error);">Quality stocks can face losses. Not a buy recommendation.</span>
</p>
</div>
""", unsafe_allow_html=True)