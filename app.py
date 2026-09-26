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

# ડેટા મેળવવાનું સુધારેલું ફંક્શન (વીકેન્ડ સ્પેશિયલ)
def get_market_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # પહેલા ૧ મિનિટનો ડેટા ટ્રાય કરો
        data = ticker.history(period="1d", interval="1m")
        # જો બજાર બંધ હોય તો છેલ્લો ઉપલબ્ધ ડેટા (૫ દિવસનો) ટ્રાય કરો
        if data.empty:
            data = ticker.history(period="5d", interval="1m")
        return data
    except Exception as e:
        return pd.DataFrame()

# UI હેડર
st.title("🧘 યોગ-સૂચકમ")
st.write("---")

# સાઇડબારમાં વ્યાપાર સેટિંગ્સ
st.sidebar.header("⚙️ વ્યાપાર સેટિંગ્સ")
m_type = st.sidebar.selectbox("બજાર પસંદ કરો", ["NSE", "Crypto"])
raw_sym = st.sidebar.text_input("સ્ટોક/કોઈનનું નામ", "RELIANCE")
symbol = f"{raw_sym}.NS" if m_type == "NSE" and ".NS" not in raw_sym else raw_sym

qty = st.sidebar.number_input("જથ્થો (Quantity)", value=10, min_value=1)
tp_pts = st.sidebar.number_input("ટાર્ગેટ (Points)", value=10.0)
sl_pts = st.sidebar.number_input("સ્ટોપલોસ (Points)", value=5.0)
tsl_pts = st.sidebar.number_input("ટ્રેલિંગ SL (Points)", value=2.0)

# મેઈન એરિયા
tab1, tab2 = st.tabs(["🚀 લાઈવ પેપર ટ્રેડિંગ", "🔍 બેકટેસ્ટિંગ"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    df = get_market_data(symbol)
    
    with col1:
        if not df.empty:
            last_price = df['Close'].iloc[-1]
            price = float(round(last_price, 2))
            
            # માર્કેટ સ્ટેટસ ચેક
            is_weekend = datetime.now().weekday() >= 5
            status = "🔴 બજાર બંધ છે (છેલ્લો ભાવ)" if is_weekend else "🟢 બજાર ચાલુ છે"
            st.write(f"**સ્થિતિ:** {status}")
            st.metric(f"{symbol} ભાવ", f"₹{price}")
            
            # સોદો ચાલુ ન હોય તો જ બટન બતાવવું
            if not st.session_state.position:
                if st.button("🚀 ખરીદી કરો (BUY ORDER)", use_container_width=True):
                    st.session_state.position = {
                        "entry": price, "qty": qty, 
                        "tp": price + tp_pts, "sl": price - sl_pts, 
                        "tsl": price - sl_pts, "symbol": symbol
                    }
                    st.success("ઓર્ડર એક્ઝિક્યુટ થયો!")
                    st.rerun()
            else:
                st.info("✅ તમારી પોઝિશન અત્યારે ઓપન છે.")
        else:
            st.error("ભાવ મળી શક્યા નથી. કૃપા કરીને સ્ટોકનું નામ (Symbol) તપાસો.")

    with col2:
        if st.session_state.position:
            p = st.session_state.position
            current_p = float(df['Close'].iloc[-1]) if not df.empty else p['entry']
            pnl = float(round((current_p - p['entry']) * p['qty'], 2))
            
            st.subheader("🔔 ચાલુ સોદાની વિગત")
            st.write(f"સ્ટોક: {p['symbol']} | એન્ટ્રી: {p['entry']}")
            st.metric("નફો / નુકસાન", f"₹{pnl}", delta=pnl)
            
            # Trailing SL Logic
            if current_p > (p['tsl'] + tsl_pts + 1):
                st.session_state.position['tsl'] = current_p - tsl_pts
            
            st.write(f"🎯 Target: {p['tp']} | 🛑 StopLoss: {round(p['tsl'], 2)}")

            if st.button("🚩 સોદો બંધ કરો (Square Off)", type="primary", use_container_width=True):
                st.session_state.balance += pnl
                st.session_state.history.append({
                    "સમય": datetime.now().strftime("%H:%M"),
                    "સ્ટોક": symbol, "PnL": pnl, "Reason": "Manual"
                })
                st.session_state.position = None
                st.rerun()
        else:
            st.write("### 💰 કુલ બેલેન્સ")
            st.title(f"₹{round(st.session_state.balance, 2)}")
            if st.session_state.history:
                st.write("**છેલ્લા સોદાઓ:**")
                st.table(pd.DataFrame(st.session_state.history).tail(3))

# ઓટો રિફ્રેશ
time.sleep(3)
st.rerun()