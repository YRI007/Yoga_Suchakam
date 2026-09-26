import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# ૧. પ્રોફેશનલ પેજ સેટઅપ
st.set_page_config(page_title="Yoga_Suchakam | Pro Terminal", layout="wide", initial_sidebar_state="expanded")

# ૨. ડેલ્ટા એક્સચેન્જ જેવી ડાર્ક થીમ (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #d1d4dc; }
    .price-container { background-color: #161a1e; padding: 10px; border-radius: 5px; border-left: 5px solid #00ff00; margin-bottom: 20px; }
    .price-val { font-size: 32px; font-weight: bold; color: #00ff00; }
    .order-red { color: #ff4d4d; font-family: 'Courier New', monospace; font-size: 14px; margin: 2px 0; }
    .order-green { color: #00ff00; font-family: 'Courier New', monospace; font-size: 14px; margin: 2px 0; }
    .wallet-box { background-color: #1e222d; padding: 15px; border-radius: 8px; border: 1px solid #363c4e; }
    </style>
    """, unsafe_allow_html=True)

# ૩. ડેટા મેળવવાનું મજબૂત ફંક્શન
def fetch_delta_data(symbol="BTCUSD"):
    try:
        # લાઈવ ભાવ માટે (Timeout સાથે જેથી એપ અટકે નહીં)
        ticker_url = f"https://api.delta.exchange/v2/tickers/{symbol}"
        t_res = requests.get(ticker_url, timeout=5).json()
        mark_price = t_res['result']['mark_price'] if 'result' in t_res else "0.00"
        
        # ઓર્ડર બુક માટે
        ob_url = f"https://api.delta.exchange/v2/l2orderbook/{symbol}?limit=10"
        ob_res = requests.get(ob_url, timeout=5).json()
        bids = ob_res['result']['buy'] if 'result' in ob_res else []
        asks = ob_res['result']['sell'] if 'result' in ob_res else []
        
        return mark_price, bids, asks
    except Exception as e:
        return "Offline", [], []

# ૪. મુખ્ય ટાઇટલ
st.title("🧘 યોગ-સૂચકમ | LIVE PRO TERMINAL")

# સાઇડબાર - કંટ્રોલ પેનલ
st.sidebar.title("🎮 ટર્મિનલ કંટ્રોલ")
selected_symbol = st.sidebar.selectbox("કોઈન પસંદ કરો", ["BTCUSD", "ETHUSD", "SOLUSD", "DETOUSD"])
st.sidebar.divider()

# ૫. ડેટા મેળવો
live_price, buy_orders, sell_orders = fetch_delta_data(selected_symbol)

# ૬. મુખ્ય લેઆઉટ (૨ ભાગમાં)
col_left, col_right = st.columns([3, 1])

with col_left:
    # લાઈવ ભાવ બોક્સ
    st.markdown(f"""
        <div class="price-container">
            <small>MARK PRICE ({selected_symbol})</small><br>
            <span class="price-val">${live_price}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # અસલી ટ્રેડિંગ ચાર્ટ (TradingView)
    chart_html = f"""
    <div style="height:550px; border: 1px solid #363c4e; border-radius: 5px; overflow: hidden;">
        <iframe src="https://s.tradingview.com/widgetembed/?symbol=DELTA:{selected_symbol}&interval=1&theme=dark&style=1&timezone=Asia%2FKolkata" 
        width="100%" height="100%" frameborder="0"></iframe>
    </div>
    """
    components.html(chart_html, height=560)

with col_right:
    # ઓર્ડર બુક (જે પેલા લાલ-લીલા આંકડા છે)
    st.subheader("📊 Order Book")
    
    # વેચનારા (Sellers - Red)
    if sell_orders:
        for ask in reversed(sell_orders[:10]):
            st.markdown(f"<p class='order-red'>{ask['price']} &nbsp;&nbsp;&nbsp;&nbsp; {ask['size']}</p>", unsafe_allow_html=True)
    else:
        st.write("Loading asks...")
        
    st.markdown(f"### ${live_price}") # વચ્ચે ચાલુ ભાવ
    
    # ખરીદનારા (Buyers - Green)
    if buy_orders:
        for bid in buy_orders[:10]:
            st.markdown(f"<p class='order-green'>{bid['price']} &nbsp;&nbsp;&nbsp;&nbsp; {bid['size']}</p>", unsafe_allow_html=True)
    else:
        st.write("Loading bids...")

    st.divider()
    
    # ક્વિક ટ્રેડ પેનલ
    st.subheader("⚡ Quick Trade")
    trade_qty = st.number_input("Qty", value=0.001, format="%.3f", step=0.001)
    c_buy, c_sell = st.columns(2)
    c_buy.button("BUY", use_container_width=True, type="primary")
    c_sell.button("SELL", use_container_width=True)

# ૭. નીચેનો ભાગ: વોલેટ અને પોઝિશન
st.divider()
row_bot1, row_bot2 = st.columns(2)

with row_bot1:
    st.subheader("💰 વોલેટ અને બેલેન્સ")
    st.markdown("""
        <div class="wallet-box">
            <p>USDT: <b>Loading...</b></p>
            <p>BTC: <b>Loading...</b></p>
            <small style="color: gray;">(બેલેન્સ જોવા માટે સિક્રેટ્સમાં API કી સેટ કરો)</small>
        </div>
    """, unsafe_allow_html=True)

with row_bot2:
    st.subheader("📋 લાઈવ પોઝિશન")
    st.info("હાલમાં કોઈ ઓપન પોઝિશન નથી.")

# ૮. ઓટો રિફ્રેશ (દર ૨ સેકન્ડે ડેટા બદલાશે)
time.sleep(2)
st.rerun()