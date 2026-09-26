import streamlit as st
import pandas as pd
import yfinance as yf
import time
from datetime import datetime

# પેજ સેટઅપ
st.set_page_config(page_title="Yoga_Suchakam Terminal", layout="wide")

# ડેટા સ્ટોરેજ
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'history' not in st.session_state: st.session_state.history = []
if 'position' not in st.session_state: st.session_state.position = None

# ડેટા મેળવવાનું ફંક્શન
def get_market_data(symbol, period="1d", interval="1m"):
    try:
        # multi_level_download=False રાખવાથી ડેટા સિમ્પલ ફોર્મેટમાં મળશે
        data = yf.download(symbol, period=period, interval=interval, progress=False, multi_level_download=False)
        return data
    except: return pd.DataFrame()

# UI હેડર
st.title("🧘 યોગ-સૂચકમ")

tab1, tab2 = st.tabs(["🚀 લાઈવ પેપર ટ્રેડિંગ", "🔍 બેકટેસ્ટિંગ (જૂની માહિતી)"])

# --- TAB 1: લાઈવ ટ્રેડિંગ ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.sidebar.header("⚙️ વ્યાપાર સેટિંગ્સ")
        m_type = st.sidebar.selectbox("બજાર પસંદ કરો", ["NSE", "Crypto"])
        raw_sym = st.sidebar.text_input("સ્ટોક/કોઈનનું નામ", "RELIANCE")
        symbol = f"{raw_sym}.NS" if m_type == "NSE" and ".NS" not in raw_sym else raw_sym
        
        qty = st.sidebar.number_input("જથ્થો", value=10)
        tp_pts = st.sidebar.number_input("ટાર્ગેટ (Points)", value=10.0)
        sl_pts = st.sidebar.number_input("સ્ટોપલોસ (Points)", value=5.0)
        tsl_pts = st.sidebar.number_input("ટ્રેલિંગ SL (Points)", value=2.0)

        df = get_market_data(symbol)
        if not df.empty:
            # ભાવને ચોક્કસ નંબર (float) માં ફેરવવો
            last_price = df['Close'].iloc[-1]
            price = float(round(last_price, 2))
            
            st.metric(f"{symbol} લાઈવ ભાવ", f"₹{price}")
            if st.button("🚀 ખરીદી (BUY)", use_container_width=True) and not st.session_state.position:
                st.session_state.position = {
                    "entry": price, "qty": qty, 
                    "tp": price + tp_pts, "sl": price - sl_pts, 
                    "tsl": price - sl_pts, "symbol": symbol
                }
                st.success("ઓર્ડર પ્લેસ થયો!")

    with col2:
        if st.session_state.position:
            p = st.session_state.position
            pnl = float(round((price - p['entry']) * p['qty'], 2))
            st.subheader("🔔 એક્ટિવ ટ્રેડ")
            st.metric("નફો / નુકસાન", f"₹{pnl}", delta=pnl)
            
            # Trailing SL Logic
            if price > (p['tsl'] + tsl_pts + 1):
                st.session_state.position['tsl'] = price - tsl_pts
            
            # Exit Conditions
            if price >= p['tp'] or price <= p['tsl']:
                res = "Target Hit" if price >= p['tp'] else "TSL Hit"
                st.session_state.balance += pnl
                st.session_state.history.append({"Stock": symbol, "PnL": pnl, "Reason": res})
                st.session_state.position = None
                st.warning(f"સોદો બંધ: {res}")
        else:
            st.info("કોઈ પોઝિશન નથી. નવો ટ્રેડ શરૂ કરો.")

# --- TAB 2: BACKTESTING ---
with tab2:
    st.subheader("⌛ જૂની માહિતી તપાસો")
    b_days = st.slider("દિવસો", 5, 60, 30)
    if st.button("Run Backtest"):
        bt_df = get_market_data(symbol, period=f"{b_days}d", interval="15m")
        if not bt_df.empty:
            st.line_chart(bt_df['Close'])
            st.success("બેકટેસ્ટિંગ ડેટા લોડ થયો છે.")

# ઓટો રિફ્રેશ
time.sleep(3)
st.rerun()