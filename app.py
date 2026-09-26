import streamlit as st
import pandas as pd
import yfinance as yf
import time
from datetime import datetime, timedelta

# પેજ સેટઅપ
st.set_page_config(page_title="Yoga_Suchakam Terminal", layout="wide")

# ડેટા સ્ટોરેજ
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'history' not in st.session_state: st.session_state.history = []
if 'position' not in st.session_state: st.session_state.position = None

# ડેટા મેળવવાનું ફંક્શન (લાઈવ અને હિસ્ટોરિકલ)
def get_market_data(symbol, period="1d", interval="1m"):
    try:
        data = yf.download(symbol, period=period, interval=interval, progress=False)
        return data
    except: return pd.DataFrame()

# UI હેડર
st.title("🧘 યોગ-સૂચકમ: સનાતન ટ્રેડિંગ ટર્મિનલ")

tab1, tab2 = st.tabs(["🚀 લાઈવ પેપર ટ્રેડિંગ", "🔍 બેકટેસ્ટિંગ (જૂની માહિતી તપાસો)"])

# --- TAB 1: લાઈવ ટ્રેડિંગ ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.sidebar.header("⚙️ વ્યાપાર સેટિંગ્સ")
        m_type = st.sidebar.selectbox("બજાર પસંદ કરો", ["NSE (ભારતીય)", "Crypto (ગ્લોબલ)"])
        raw_sym = st.sidebar.text_input("સ્ટોક/કોઈનનું નામ", "RELIANCE")
        symbol = f"{raw_sym}.NS" if m_type == "NSE (ભારતીય)" and ".NS" not in raw_sym else raw_sym
        
        qty = st.sidebar.number_input("જથ્થો (Qty)", value=10)
        tp = st.sidebar.number_input("ટાર્ગેટ (Points)", value=10.0)
        sl = st.sidebar.number_input("સ્ટોપલોસ (Points)", value=5.0)
        tsl = st.sidebar.number_input("ટ્રેલિંગ SL (Points)", value=2.0)

        df = get_market_data(symbol)
        if not df.empty:
            price = round(df['Close'].iloc[-1], 2)
            st.metric(f"{symbol} લાઈવ ભાવ", f"₹{price}")
            if st.button("🚀 ખરીદી (BUY)", use_container_width=True) and not st.session_state.position:
                st.session_state.position = {"entry": price, "qty": qty, "tp": price + tp, "sl": price - sl, "tsl": price - sl, "symbol": symbol}
                st.success("ઓર્ડર પ્લેસ થયો!")

    with col2:
        if st.session_state.position:
            p = st.session_state.position
            pnl = round((price - p['entry']) * p['qty'], 2)
            st.subheader("🔔 એક્ટિવ ટ્રેડ")
            st.metric("નફો / નુકસાન", f"₹{pnl}", delta=pnl)
            
            # Trailing SL
            if price > (p['tsl'] + tsl + 1): st.session_state.position['tsl'] = price - tsl
            
            if price >= p['tp'] or price <= p['tsl']:
                res = "Target Hit" if price >= p['tp'] else "TSL Hit"
                st.session_state.balance += pnl
                st.session_state.history.append({"Stock": symbol, "PnL": pnl, "Reason": res})
                st.session_state.position = None
                st.warning(f"સોદો બંધ: {res}")
        else: st.info("કોઈ પોઝિશન નથી. નવો ટ્રેડ શરૂ કરો.")

# --- TAB 2: BACKTESTING ---
with tab2:
    st.subheader("⌛ ભૂતકાળનું વિશ્લેષણ")
    b_days = st.slider("કેટલા દિવસનો ડેટા તપાસવો છે?", 5, 60, 30)
    if st.button("પરીક્ષણ શરૂ કરો (Run Backtest)"):
        with st.spinner("ડેટા એનાલિસિસ ચાલુ છે..."):
            bt_df = get_market_data(symbol, period=f"{b_days}d", interval="15m")
            if not bt_df.empty:
                bt_bal, wins = 0, 0
                for i in range(len(bt_df)):
                    entry = bt_df['Open'].iloc[i]
                    if bt_df['High'].iloc[i] >= entry + tp: 
                        bt_bal += (tp * qty)
                        wins += 1
                    elif bt_df['Low'].iloc[i] <= entry - sl: bt_bal -= (sl * qty)
                
                c1, c2 = st.columns(2)
                c1.metric("અંદાજિત નફો/નુકસાન", f"₹{round(bt_bal, 2)}")
                c2.metric("વિન રેટ (Win Rate)", f"{round((wins/len(bt_df))*100, 2)}%")
                st.line_chart(bt_df['Close'])
                st.success("✅ બેકટેસ્ટિંગ પૂર્ણ. તમારા નિયમો આ સ્ટોકમાં કામ કરી રહ્યા છે.")
            else: st.error("ડેટા મળી શક્યો નથી.")

# ઓટો રિફ્રેશ
time.sleep(3)
st.rerun()