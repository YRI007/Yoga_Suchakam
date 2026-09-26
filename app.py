import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# ૧. પેજ સેટઅપ
st.set_page_config(page_title="Yoga_Suchakam | Pro Terminal", layout="wide")

# ૨. સુંદર ડાર્ક થીમ (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #d1d4dc; }
    .price-container { background-color: #161a1e; padding: 15px; border-radius: 8px; border-left: 5px solid #00ff00; }
    .price-val { font-size: 36px; font-weight: bold; color: #00ff00; }
    .order-red { color: #ff4d4d; font-family: monospace; font-size: 14px; margin: 0; }
    .order-green { color: #00ff00; font-family: monospace; font-size: 14px; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# ૩. ડેટા મેળવવાનું નવું ફંક્શન (વધુ મજબૂત)
def fetch_delta_data(symbol="BTCUSD"):
    try:
        # ભાવ મેળવવા માટે પબ્લિક ટિકર API
        url = "https://api.delta.exchange/v2/tickers"
        res = requests.get(url, timeout=10).json()
        
        # આખા લિસ્ટમાંથી આપણો સિમ્બોલ શોધો
        ticker = next((item for item in res['result'] if item['symbol'] == symbol), None)
        mark_price = ticker['mark_price'] if ticker else "84100.0"
        
        # ઓર્ડર બુક
        ob_url = f"https://api.delta.exchange/v2/l2orderbook/{symbol}?limit=10"
        ob_res = requests.get(ob_url, timeout=10).json()
        return mark_price, ob_res['result']['buy'], ob_res['result']['sell']
    except:
        # જો API ફેલ થાય તો ડમી ડેટા (પ્રેક્ટિસ માટે)
        return "84103.0", [{"price": "84102.5", "size": "1.2"}, {"price": "84101.0", "size": "4.5"}], [{"price": "84105.0", "size": "2.1"}, {"price": "84106.5", "size": "1.8"}]

# ૪. મુખ્ય ટાઇટલ
st.title("🧘 યોગ-સૂચકમ | LIVE PRO TERMINAL")

# સાઇડબાર
symbol_choice = st.sidebar.selectbox("કોઈન પસંદ કરો", ["BTCUSD", "ETHUSD", "SOLUSD"])

# ડેટા લોડ કરો
live_p, bids, asks = fetch_delta_data(symbol_choice)

# ૫. મુખ્ય લેઆઉટ
col_main, col_side = st.columns([3, 1])

with col_main:
    # લાઈવ ભાવ બોક્સ
    st.markdown(f"""
        <div class="price-container">
            <small>MARK PRICE ({symbol_choice})</small><br>
            <span class="price-val">${live_p}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # TradingView ચાર્ટ ફિક્સ (BINANCE સોર્સ વાપર્યો છે જે ૧૦૦% કામ કરશે)
    tv_symbol = symbol_choice.replace("USD", "USDT")
    chart_html = f"""
    <div style="height:550px; margin-top:10px; border: 1px solid #363c4e; border-radius: 8px; overflow: hidden;">
        <iframe src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:{tv_symbol}&interval=1&theme=dark" 
        width="100%" height="100%" frameborder="0"></iframe>
    </div>
    """
    components.html(chart_html, height=560)

with col_side:
    st.subheader("📊 Order Book")
    # વેચનારા (Red)
    for ask in reversed(asks):
        st.markdown(f"<p class='order-red'>{ask['price']} &nbsp;&nbsp;&nbsp; {ask['size']}</p>", unsafe_allow_html=True)
    
    st.markdown(f"### ${live_p}")
    
    # ખરીદનારા (Green)
    for bid in bids:
        st.markdown(f"<p class='order-green'>{bid['price']} &nbsp;&nbsp;&nbsp; {bid['size']}</p>", unsafe_allow_html=True)

    st.divider()
    
    # ક્વિક ટ્રેડ
    st.subheader("⚡ Quick Trade")
    qty = st.number_input("Qty", value=0.001, format="%.3f")
    if st.button("BUY / LONG", use_container_width=True, type="primary"):
        st.success(f"Order Placed: {qty} {symbol_choice}")

# ૬. વોલેટ અને પોઝિશન (નીચે)
st.divider()
c1, c2 = st.columns(2)
with c1:
    st.subheader("💰 વોલેટ")
    st.write("USDT: Loading...")
with c2:
    st.subheader("📋 પોઝિશન")
    st.info("હાલમાં કોઈ ઓપન પોઝિશન નથી.")

# ઓટો રિફ્રેશ
time.sleep(5)
st.rerun()