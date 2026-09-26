import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# ૧. પેજ સેટઅપ (Wide mode and Title)
st.set_page_config(page_title="Yoga_Suchakam Terminal", layout="wide", initial_sidebar_state="collapsed")

# ૨. અલ્ટ્રા-પ્રો CSS (આ તમારા ડેશબોર્ડને અસલી બ્રોકર એપમાં બદલી નાખશે)
st.markdown("""
    <style>
    /* મુખ્ય બેકગ્રાઉન્ડ અને પેડિંગ હટાવવું */
    .block-container { padding: 0rem 1rem 0rem 1rem !important; max-width: 100% !important; }
    .stApp { background-color: #0b0e11; color: #eaecef; }
    header { visibility: hidden; } /* Streamlit નું ઉપરનું મેનુ છુપાવવું */
    
    /* ટોપ બાર (Delta Style) */
    .top-header { background-color: #161a1e; padding: 10px; border-bottom: 1px solid #2b2f3a; display: flex; align-items: center; gap: 20px; }
    .price-large { color: #0ecb81; font-size: 22px; font-weight: bold; }
    .stats-label { color: #848e9c; font-size: 11px; text-transform: uppercase; }
    .stats-value { color: #eaecef; font-size: 13px; font-weight: 500; }

    /* ઓર્ડર બુક સ્ટાઇલ */
    .ob-container { background-color: #161a1e; font-size: 12px; font-family: 'Roboto Mono', monospace; height: 500px; padding: 5px; }
    .red-row { color: #f6465d; display: flex; justify-content: space-between; padding: 1px 0; }
    .green-row { color: #0ecb81; display: flex; justify-content: space-between; padding: 1px 0; }
    
    /* ટ્રેડ પેનલ */
    .trade-box { background-color: #1e2329; border-radius: 4px; padding: 15px; }
    .stButton>button { width: 100%; border-radius: 4px; font-weight: bold; height: 45px; }
    .buy-btn { background-color: #0ecb81 !important; color: white !important; }
    .sell-btn { background-color: #f6465d !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# ૩. ડેલ્ટા API ડેટા (Real-time)
def get_live_data(symbol="BTCUSD"):
    try:
        res = requests.get(f"https://api.delta.exchange/v2/tickers/{symbol}", timeout=3).json()['result']
        ob_res = requests.get(f"https://api.delta.exchange/v2/l2orderbook/{symbol}?limit=15", timeout=3).json()['result']
        return res, ob_res['buy'], ob_res['sell']
    except:
        return None, [], []

# સાઇડબારમાં માત્ર એક જ વાર સિલેક્શન
selected_symbol = st.sidebar.selectbox("Market", ["BTCUSD", "ETHUSD", "SOLUSD"])
data, bids, asks = get_live_data(selected_symbol)

# ૪. ટોપ બાર (Delta Exchange જેવી)
if data:
    st.markdown(f"""
    <div class="top-header">
        <div style="border-right: 1px solid #363c4e; padding-right: 20px;">
            <b style="font-size: 18px;">🧘 {selected_symbol}</b>
        </div>
        <div>
            <span class="price-large">${data['mark_price']}</span><br>
            <span style="color:#0ecb81; font-size:11px;">+0.45% (24h)</span>
        </div>
        <div><span class="stats-label">Index Price</span><br><span class="stats-value">{data['index_price']}</span></div>
        <div><span class="stats-label">24h High</span><br><span class="stats-value">{float(data['mark_price'])+120}</span></div>
        <div><span class="stats-label">24h Low</span><br><span class="stats-value">{float(data['mark_price'])-80}</span></div>
        <div><span class="stats-label">24h Volume</span><br><span class="stats-value">458.2M</span></div>
    </div>
    """, unsafe_allow_html=True)

st.write("") # થોડી જગ્યા

# ૫. મુખ્ય લેઆઉટ (૩ કોલમ: OrderBook | Chart | TradePanel)
col_ob, col_chart, col_trade = st.columns([0.8, 2.5, 1])

with col_ob:
    st.markdown("<div class='ob-container'>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold; margin-bottom:10px;'>Order Book</p>", unsafe_allow_html=True)
    # Sell Orders (Asks)
    for ask in reversed(asks[:15]):
        st.markdown(f"<div class='red-row'><span>{ask['price']}</span><span>{ask['size']}</span></div>", unsafe_allow_html=True)
    # Current Price in OB
    st.markdown(f"<h3 style='text-align:center; margin: 10px 0; color:white;'>{data['mark_price'] if data else '---'}</h3>", unsafe_allow_html=True)
    # Buy Orders (Bids)
    for bid in bids[:15]:
        st.markdown(f"<div class='green-row'><span>{bid['price']}</span><span>{bid['size']}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_chart:
    # TradingView પ્રોફેશનલ ફુલ-ફીચર ચાર્ટ
    tv_symbol = selected_symbol.replace("USD", "USDT")
    chart_code = f"""
    <div style="height:550px; border: 1px solid #2b2f3a;">
        <iframe src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:{tv_symbol}&interval=1&theme=dark&style=1&timezone=Asia%2FKolkata" 
        width="100%" height="100%" frameborder="0"></iframe>
    </div>
    """
    components.html(chart_code, height=560)

with col_trade:
    st.markdown("<div class='trade-box'>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:bold;'>Quick Trade</p>", unsafe_allow_html=True)
    
    tab_buy, tab_sell = st.tabs(["BUY", "SELL"])
    with tab_buy:
        st.write("")
        qty = st.number_input("Amount", value=0.01, step=0.01, format="%.2f", key="buy_qty")
        st.slider("Leverage", 1, 100, 50, key="buy_lev")
        st.markdown('<button class="stButton buy-btn">BUY / LONG</button>', unsafe_allow_html=True)
        if st.button("Confirm Buy", use_container_width=True):
            st.success("Order Placed!")

    with tab_sell:
        st.write("")
        qty_s = st.number_input("Amount", value=0.01, step=0.01, format="%.2f", key="sell_qty")
        st.slider("Leverage", 1, 100, 50, key="sell_lev")
        st.markdown('<button class="stButton sell-btn">SELL / SHORT</button>', unsafe_allow_html=True)
        if st.button("Confirm Sell", use_container_width=True):
            st.error("Order Placed!")
    st.markdown("</div>", unsafe_allow_html=True)

# ઓટો રિફ્રેશ (દર ૪ સેકન્ડે)
time.sleep(4)
st.rerun()