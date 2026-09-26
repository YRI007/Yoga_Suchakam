import streamlit as st
import pandas as pd
import requests
import time
import hmac
import hashlib
import json
import streamlit.components.v1 as components

# પેજ સેટઅપ
st.set_page_config(page_title="Yoga_Suchakam | Live Terminal", layout="wide")

# CSS થી પ્રોફેશનલ ડાર્ક થીમ (Delta Exchange જેવી)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #d1d4dc; }
    .price-text { font-size: 32px; font-weight: bold; color: #00ff00; }
    .order-red { color: #ff4d4d; font-family: 'Courier New', monospace; font-size: 14px; margin: 0; }
    .order-green { color: #00ff00; font-family: 'Courier New', monospace; font-size: 14px; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# સુરક્ષિત રીતે કી મેળવવી
API_KEY = st.secrets.get("DELTA_API_KEY", "")
API_SECRET = st.secrets.get("DELTA_API_SECRET", "")

# પબ્લિક ડેટા મેળવવાનું ફંક્શન (આના માટે કીની જરૂર નથી)
def get_market_data(symbol="BTCUSD"):
    try:
        # લાઈવ ભાવ
        ticker_url = f"https://api.delta.exchange/v2/tickers/{symbol}"
        res = requests.get(ticker_url).json()
        price = res['result']['mark_price']
        
        # ઓર્ડર બુક
        ob_url = f"https://api.delta.exchange/v2/l2orderbook/{symbol}?limit=10"
        ob_res = requests.get(ob_url).json()
        return price, ob_res['result']['buy'], ob_res['result']['sell']
    except:
        return "0.0", [], []

# --- UI Layout ---
st.title("🧘 યોગ-સૂચકમ | LIVE TERMINAL")

symbol = st.sidebar.selectbox("Symbol", ["BTCUSD", "ETHUSD", "SOLUSD"])
price, bids, asks = get_market_data(symbol)

col_chart, col_trade = st.columns([3, 1])

with col_chart:
    # લાઈવ પ્રાઈસ હેડર
    st.markdown(f"<p class='price-text'>${price}</p>", unsafe_allow_html=True)
    
    # TradingView Chart Fix
    chart_html = f"""
    <div style="height:550px;">
        <iframe src="https://s.tradingview.com/widgetembed/?symbol={symbol}&interval=1&theme=dark" 
        width="100%" height="100%" frameborder="0"></iframe>
    </div>
    """
    components.html(chart_html, height=550)

with col_trade:
    st.subheader("📊 Order Book")
    # Sellers (Asks)
    for ask in reversed(asks[:8]):
        st.markdown(f"<p class='order-red'>{ask['price']} &nbsp;&nbsp;&nbsp; {ask['size']}</p>", unsafe_allow_html=True)
    
    st.markdown(f"### ${price}")
    
    # Buyers (Bids)
    for bid in bids[:8]:
        st.markdown(f"<p class='order-green'>{bid['price']} &nbsp;&nbsp;&nbsp; {bid['size']}</p>", unsafe_allow_html=True)

    st.divider()
    
    # Quick Trade Panel
    st.subheader("⚡ Quick Trade")
    qty = st.number_input("Qty", value=0.001, format="%.3f")
    if st.button("BUY / LONG", use_container_width=True, type="primary"):
        st.balloons()
        st.info("ઓર્ડર પ્રોસેસ થઈ રહ્યો છે...")

# --- Footer: Wallet & Positions ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    st.subheader("💰 વોલેટ બેલેન્સ")
    if not API_KEY:
        st.warning("⚠️ સિક્રેટ્સમાં API કી સેટ કરો.")
    else:
        st.info("API કનેક્ટ થઈ રહ્યું છે...")

with c2:
    st.subheader("📋 લાઈવ પોઝિશન")
    st.write("હજી કોઈ ઓપન પોઝિશન નથી.")

# ઓટો રિફ્રેશ દર ૩ સેકન્ડે
time.sleep(3)
st.rerun()