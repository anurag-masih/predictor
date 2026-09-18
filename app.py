import streamlit as st
import yfinance as yf
import feedparser
import pandas as pd

st.set_page_config(page_title="Macro Predictive Dashboard", layout="wide")

st.title("🌐 Mini Predictive Macro & Geopolitical Dashboard")
st.markdown("Tracking leading indicators and policy signals in real-time.")

# --- SECTION 1: LEADING INDICATORS (MARKET DATA) ---
st.header("1. Leading Market Indicators")

@st.cache_data(ttl=3600)
def load_market_data():
    return yf.download(["HG=F", "GC=F"], period="3mo")['Close']

data = load_market_data()

if not data.empty:
    data['Copper_Gold_Ratio'] = data['HG=F'] / data['GC=F']
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Copper / Gold Ratio Trend")
        st.line_chart(data['Copper_Gold_Ratio'])
        
    with col2:
        st.subheader("Latest Values")
        latest_copper = data['HG=F'].iloc[-1]
        latest_gold = data['GC=F'].iloc[-1]
        latest_ratio = data['Copper_Gold_Ratio'].iloc[-1]
        
        st.metric(label="Copper Futures ($/lb)", value=f"{latest_copper:.2f}")
        st.metric(label="Gold Futures ($/oz)", value=f"{latest_gold:.2f}")
        st.metric(label="Copper-to-Gold Ratio", value=f"{latest_ratio:.4f}")
else:
    st.error("Could not fetch market data. Check internet connection.")

# --- SECTION 2: PREDICTIVE LOGIC ENGINE ---
st.markdown("---")
st.header("2. Automated Predictive Signals")

# Simple predictive rule demonstration
if not data.empty:
    rolling_mean = data['Copper_Gold_Ratio'].rolling(window=14).mean().iloc[-1]
    current_ratio = data['Copper_Gold_Ratio'].iloc[-1]
    
    if current_ratio < (rolling_mean * 0.95):
        st.warning("⚠️ **Divergence Alert:** Copper-to-Gold ratio has dropped more than 5% below its 14-day moving average. *Potential signal: Industrial demand deceleration or liquidity tightening.*")
    else:
        st.success("✅ **Baseline Stable:** Leading market ratios are within normal historical bands. No immediate structural anomaly detected.")

# --- SECTION 3: POLICY & THINK-TANK RSS INGESTION ---
st.markdown("---")
st.header("3. Policy & Geopolitical RSS Feed (Live)")

rss_url = "https://www.bis.org/doc-search/rss.rss"

try:
    import requests
    # Use custom headers so institutional firewalls don't block the request
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(rss_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        feed = feedparser.parse(response.content)
        if feed.entries:
            for entry in feed.entries[:5]:
                with st.expander(f"📌 {entry.title}"):
                    st.write(f"**Published:** {entry.get('published', 'N/A')}")
                    st.write(f"[Read Source Document]({entry.link})")
        else:
            st.info("The RSS feed parsed successfully, but no entries were found.")
    else:
        st.warning(f"Could not connect to RSS feed (Status code: {response.status_code})")
except Exception as e:
    st.info("Unable to parse RSS feed at the moment due to network restriction.")
