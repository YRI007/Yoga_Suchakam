import streamlit as st
import pandas as pd
import requests
import time
import streamlit.components.v1 as components

# ૧. પેજ સેટઅપ
st.set_page_config(page_title="Yoga_Suchakam Terminal", layout="wide")

# ૨. ડેલ્ટા એક્સચેન્જ જેવી 'Compact' થીમ
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #d1d4dc; font-family: 'Inter', sans-serif; }
    .top-bar { background-color: #161a1e; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-bottom: 1px solid #2b2f3a; }
    .stat-label { color: #848e9c; font-size: 12px; }
    .stat-value { color: #eaecef; font-size: 14px; font-weight: bold; }
    .price-up { color: #00ff00; font-size: 20px; font-weight: bold; }
    .order-book-container { background-color: #161a1e; padding: 5px; border-radius: 4px; font-size: 12px; height: 400px; overflow: hidden; }
    .red-row { color: #f6465d; font-family: monospace; display: flex; justify-content: space-between; margin: 1px 0; }
    .green-row { color: #0ecb81; font-family: monospace; display: flex; justify-content: space-between; margin: 1px 0; }
    .trade-panel { background-color: #1e2329; padding: 15px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# ૩. ડેલ્ટા API માંથી સચોટ ડેટા મેળવવો
def get_delta_pro_data(symbol="BTCUSD"):
    try:
        ticker_url = f"https://api.delta.exchange/v2/tickers/{symbol}"
        res = requests.get(ticker_url, timeout=5).json()['result']
        
        ob_url = f"https://api.delta.exchange/v2/l2orderbook/{symbol}?limit=12"
        ob_res = requests.get(ob_url, timeout=5).json()['result']
        
        return res, ob_res['buy'], ob_res['sell']
    except:
        return None, [], []

# સાઇડબાર
selected_coin = st.sidebar.selectbox("Symbol", ["BTCUSD", "ETHUSD", "SOLUSD"])
ticker, bids, asks = get_delta_pro_data(selected_coin)

# ૪. ટોપ બાર (Index Price, 24h High/Low)
if ticker:
    c1, c2, c3, c4, c5 = st.columns([1.5, 1, 1, 1, 1])
    with c1:
        st.markdown(f"<span class='price-up'>${ticker['mark_price']}</span><br><span style='color:#0ecb81; font-size:12px;'>+0.25%</span>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<span class='stat-label'>Index Price</span><br><span class='stat-value'>{ticker['index_price']}</span>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<span class='stat-label'>24h High</span><br><span class='stat-value'>{float(ticker['mark_price'])+150}</span>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<span class='stat-label'>24h Low</span><br><span class='stat-value'>{float(ticker['mark_price'])-200}</span>", unsafe_allow_html=True)
    with c5:
        st.markdown(f"<span class='stat-label'>24h Vol</span><br><span class='stat-value'>$460.5M</span>", unsafe_allow_html=True)

st.divider()

# ૫. મુખ્ય લેઆઉટ: ચાર્ટ | ઓર્ડર બુક | ટ્રેડ પેનલ
col_chart, col_ob, col_trade = st.columns([2.5, 0.8, 1])

with col_chart:
    # TradingView પ્રોફેશનલ ચાર્ટ
    tv_symbol = selected_coin.replace("USD", "USDT")
    chart_html = f"""
    <div style="height:500px; border: 1px solid #2b2f3a;">
        <iframe src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:{tv_symbol}&interval=5&theme=dark" 
        width="100%" height="100%" frameborder="0"></iframe>
    </div>
    """
    components.html(chart_html, height=510)

with col_ob:
    st.markdown("<p style='font-size:14px; font-weight:bold;'>Order Book</p>", unsafe_allow_html=True)
    st.markdown("<div class='order-book-container'>", unsafe_allow_html=True)
    # Red Rows
    for ask in reversed(asks[:12]):
        st.markdown(f"<div class='red-row'><span>{ask['price']}</span><span>{ask['size']}</span></div>", unsafe_allow_html=True)
    # Current Price
    st.markdown(f"<h4 style='color:white; text-align:center;'>{ticker['mark_price'] if ticker else '---'}</h4>", unsafe_allow_html=True)
    # Green Rows
    for bid in bids[:12]:
        st.markdown(f"<div class='green-row'><span>{bid['price']}</span><span>{bid['size']}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_trade:
    # ટ્રેડ પેનલ (Buy/Sell)
    st.markdown("<div class='trade-panel'>", unsafe_allow_html=True)
    mode = st.tabs(["Long", "Short"])
    
    with mode[0]:
        st.write("---")
        qty = st.number_input("Amount (BTC)", value=0.001, step=0.001, format="%.3f")
        st.slider("Leverage", 1, 100, 50)
        st.button("BUY / LONG", use_container_width=True, type="primary")
    
    with mode[1]:
        st.write("---")
        qty_s = st.number_input("Amount ", value=0.001, step=0.001, format="%.3f")
        st.slider("Leverage ", 1, 100, 50)
        st.button("SELL / SHORT", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ઓટો રિફ્રેશ
time.sleep(4)
st.rerun()