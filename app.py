import streamlit as st
import pandas as pd
import yfinance as yf
import streamlit.components.v1 as components
import time

# પ્રોફેશનલ ડાર્ક થીમ સેટઅપ
st.set_page_config(page_title="Yoga_Suchakam", layout="wide", initial_sidebar_state="expanded")

# CSS થી લુક સુધારવો (બ્રોકર જેવો લુક)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .metric-container { background-color: #1e222d; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ડેટા સ્ટોરેજ
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'position' not in st.session_state: st.session_state.position = None

# --- સાઇડબાર: ઓર્ડર પેનલ (Fyers જેવી) ---
st.sidebar.title("⚡ Quick Order")
symbol = st.sidebar.text_input("Symbol", "NSE:NIFTY50").upper()
order_type = st.sidebar.radio("Type", ["BUY (CE)", "SELL (PE)"])
qty = st.sidebar.number_input("Qty", value=50, step=50)
st.sidebar.divider()
st.sidebar.subheader("🛡️ Risk Guard")
tp = st.sidebar.number_input("Target Points", value=20.0)
sl = st.sidebar.number_input("Stop Loss", value=10.0)

# --- મુખ્ય સ્ક્રીન લેઆઉટ ---
col_chart, col_orders = st.columns([3, 1])

with col_chart:
    st.title("🧘 યોગ-સૂચકમ")
    # TradingView ચાર્ટ એમ્બેડ કરવો (આ બ્રોકર જેવો જ ચાર્ટ બતાવશે)
    chart_html = f"""
    <div style="height:500px;">
        <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_76d4d&symbol={symbol}&interval=5&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=[]&theme=dark&style=1&timezone=Asia%2FKolkata" 
        width="100%" height="100%" frameborder="0" allowfullscreen></iframe>
    </div>
    """
    components.html(chart_html, height=500)

with col_orders:
    st.subheader("📊 Market Depth")
    # કાલ્પનિક ઓર્ડર બુક (Live બ્રોકર વગર આ બતાવવું મુશ્કેલ છે, પણ આપણે લુક આપી શકીએ)
    st.write("🟢 Buy Orders | 🔴 Sell Orders")
    st.code("23140.50 - 5500\n23139.00 - 1200\n23142.10 - 3400", language="bash")
    
    st.divider()
    
    # લાઈવ પોઝિશન ટ્રેકર
    if st.session_state.position:
        st.success("🎯 Active Position Running")
        if st.button("🔴 SQUARE OFF (EXIT)"):
            st.session_state.position = None
            st.rerun()
    else:
        if st.sidebar.button("🚀 PLACE ORDER", use_container_width=True):
            st.session_state.position = {"status": "OPEN"}
            st.balloons()

# --- નીચેનો ભાગ: ઓપ્શન ચેઈન સ્ટાઈલ ---
st.divider()
st.subheader("⛓️ Option Chain (NIFTY)")
option_data = {
    "Calls (OI)": [1200, 3400, 5600],
    "Strike": [23100, 23150, 23200],
    "Puts (OI)": [4500, 2100, 900]
}
st.table(pd.DataFrame(option_data))

time.sleep(5)