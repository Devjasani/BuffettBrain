# 🧠 BuffettBrain - AI-Powered Value Investing Tool

**BuffettBrain** is a sophisticated financial analysis tool designed to help investors identify high-quality stocks using the principles of **Warren Buffett** and **Benjamin Graham**. It automates the complex process of quantitative analysis, providing a clear "Buy", "Hold", or "Avoid" recommendation based on a strict 15-point checklist.

> **⚠️ Disclaimer:** This tool is for educational and informational purposes only. It is a Beta version (`v1.0-beta`). All financial data is fetched live but should be verified. This is **NOT** financial advice or a recommendation to buy/sell assets.

---

## 🚀 Live Demo
You can access the live application here: **[Link to your Streamlit App]** (Update this after deploying)

---

## 📂 Project Structure

| File/Folder | Description |
| :--- | :--- |
| **`app.py`** | **The Main Engine.** The entry point for the Streamlit application. |
| **`stock_analyzer.py`** | **The Brain.** Core logic for the 15-point checklist and Intrinsic Value (DCF) calculations. |
| **`data_fetcher.py`** | **The Sensory System.** Fetches live stock data via `yfinance`. |
| **`modules/`** | Reusable UI components and specialized calculation modules. |
| **`pages/`** | Multi-page Streamlit application structure. |
| **`styles.css`** | The "Cyberpunk/Neon" visual theme. |

---

## 🛠️ Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/BuffettBrain.git
   cd BuffettBrain
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

## 🌐 Deployment Instructions

### Deploying to GitHub
1. Create a new repository on GitHub.
2. Initialize git and push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   git branch -M main
   git remote add origin https://github.com/your-username/BuffettBrain.git
   git push -u origin main
   ```

### Deploying to Streamlit Cloud
1. Go to [Streamlit Cloud](https://share.streamlit.io/).
2. Connect your GitHub account.
3. Select this repository and the `app.py` file.
4. Click **Deploy!**

---

## ✅ The 15-Point Buffett Criteria

| Criteria | Threshold / Rule | Why we use it? |
| :--- | :--- | :--- |
| **Return on Equity (ROE)** | `> 15%` | Measures how efficiently management uses shareholder capital. |
| **Debt-to-Equity Ratio** | `< 0.5` | Ensures the company is not over-leveraged. |
| **Intrinsic Value (MoS)** | `MoS ≥ 20%` | Margin of Safety – Buying significantly below the true value. |
| **Operating Margin (OPM)** | `> 15%` | Indicates strong pricing power and efficiency. |
| **Free Cash Flow** | `Positive` | Real cash generation, not just accounting profits. |
| ... and 10 more institutional-grade metrics. |

---

## 🛠 Tech Stack
*   **Python 3.11+**
*   **Streamlit** (UI Framework)
*   **Plotly** (Advanced Visuals)
*   **Yfinance** (Financial Data)
*   **Pandas/Numpy** (Data Processing)

---
*Created by Dev Jasani* | *BuffettBrain v1.0*

