import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# પેજ સેટઅપ
st.set_page_config(page_title="Yoga_Suchakam | Pro Terminal", layout="wide")

# Delta Exchange API ફંક્શન
def get_delta_live_data(symbol="BTCUSD"):
    try:
        # લાઈવ ભાવ માટે
        url = f"https://api.delta.exchange/v2/tickers/{symbol}"
        response = requests.get(url).json()
        price = response['result']['mark_price']
        
        # Order Book (Market Depth) માટે
        orderbook_url = f"https://api.delta.exchange/v2/l2orderbook/{symbol}?limit=5"
        ob_response = requests.get(orderbook_url).json()
        bids = ob_response['result']['buy']
        asks = ob_response['result']['sell']
        
        return float(price), bids, asks
    except:
        return None, [], []

# CSS થી પ્રોફેશનલ લુક
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #d1d4dc; }
    .price-box { font-size: 30px; font-weight: bold; color: #00ff00; background: #161a1e; padding: 10px; border-radius: 5px; }
    .order-green { color: #00ff00; font-family: monospace; }
    .order-red { color: #ff4d4d; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- મુખ્ય લેઆઉટ ---
st.title("🧘 યોગ-સૂચકમ | Live Crypto Terminal")

symbol = st.sidebar.selectbox("પસંદ કરો", ["BTCUSD", "ETHUSD", "SOLUSD", "DETOUSD"])
price, bids, asks = get_delta_live_data(symbol)

col_chart, col_trade = st.columns([3, 1])

with col_chart:
    # લાઈવ પ્રાઈસ ડિસ્પ્લે
    st.markdown(f"<div class='price-box'>${price}</div>", unsafe_allow_html=True)
    
    # TradingView નો અસલી ચાર્ટ (Delta Exchange સ્ટાઈલ)
    chart_html = f"""
    <div style="height:550px;">
        <iframe src="https://s.tradingview.com/widgetembed/?symbol=BITMEX:{symbol}&interval=5&theme=dark" 
        width="100%" height="100%" frameborder="0"></iframe>
    </div>
    """
    components.html(chart_html, height=550)

with col_trade:
    st.subheader("📊 Order Book")
    # લાલ ભાવ (Asks/Sellers)
    for ask in reversed(asks):
        st.markdown(f"<p class='order-red'>{ask['price']} ---- {ask['size']}</p>", unsafe_allow_html=True)
    
    st.markdown(f"### {price}")
    
    # લીલા ભાવ (Bids/Buyers)
    for bid in bids:
        st.markdown(f"<p class='order-green'>{bid['price']} ---- {bid['size']}</p>", unsafe_allow_html=True)

    st.divider()
    
    # ક્વિક ટ્રેડિંગ પેનલ
    st.subheader("⚡ Quick Trade")
    qty = st.number_input("જથ્થો", value=0.001, step=0.001, format="%.3f")
    col_buy, col_sell = st.columns(2)
    if col_buy.button("BUY / LONG", use_container_width=True, type="primary"):
        st.toast(f"Bought {qty} {symbol}")
    if col_sell.button("SELL / SHORT", use_container_width=True):
        st.toast(f"Sold {qty} {symbol}")

# ઇન્વેન્ટરી અને પોઝિશન (નીચેનો ભાગ)
st.divider()
st.subheader("📋 ઓપન પોઝિશન અને હિસ્ટ્રી")
st.write("હજી કોઈ લાઈવ પોઝિશન નથી. પેપર ટ્રેડિંગ ચાલુ છે.")

# દર ૨ સેકન્ડે ઓટો રિફ્રેશ
time.sleep(2)
st.rerun()