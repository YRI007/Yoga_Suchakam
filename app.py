import streamlit as st
import pandas as pd
import requests
import time
import hmac
import hashlib
import json
import streamlit.components.v1 as components

# --- પેજ સેટઅપ ---
st.set_page_config(page_title="Yoga_Suchakam | Live Trader", layout="wide")

# સુરક્ષિત રીતે કી મેળવવી (Streamlit Secrets માંથી)
API_KEY = st.secrets.get("DELTA_API_KEY", "MISSING")
API_SECRET = st.secrets.get("DELTA_API_SECRET", "MISSING")
BASE_URL = "https://api.delta.exchange"

# --- સુરક્ષા ફંક્શન ---
def generate_signature(method, path, payload, timestamp):
    signature_data = method + timestamp + path + payload
    return hmac.new(API_SECRET.encode('utf-8'), signature_data.encode('utf-8'), hashlib.sha256).hexdigest()

def delta_request(method, path, payload={}):
    if API_KEY == "MISSING":
        return {"error": "API Keys not set"}
    
    timestamp = str(int(time.time()))
    payload_str = json.dumps(payload) if payload else ""
    signature = generate_signature(method, path, payload_str, timestamp)
    
    headers = {
        "api-key": API_KEY,
        "signature": signature,
        "timestamp": timestamp,
        "Content-Type": "application/json"
    }
    
    url = BASE_URL + path
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, data=payload_str)
        return response.json()
    except:
        return {"error": "Connection Failed"}

# --- UI Layout ---
st.title("🧘 યોગ-સૂચકમ | LIVE TERMINAL")

# સાઇડબાર
st.sidebar.title("🎮 કંટ્રોલ પેનલ")
symbol = st.sidebar.selectbox("Symbol", ["BTCUSD", "ETHUSD", "SOLUSD"])

# લાઈવ બેલેન્સ
st.sidebar.subheader("💰 વોલેટ બેલેન્સ")
account_info = delta_request("GET", "/v2/wallet/balances")
if account_info and 'result' in account_info:
    for asset in account_info['result']:
        st.sidebar.write(f"{asset['asset_symbol']}: {asset['balance']}")
else:
    st.sidebar.warning("બેલેન્સ જોવા માટે સિક્રેટ્સ સેટ કરો.")

# --- મુખ્ય વિભાગ ---
col_chart, col_trade = st.columns([3, 1])

with col_chart:
    # TradingView Live Chart
    chart_html = f'<iframe src="https://s.tradingview.com/widgetembed/?symbol=DELTA:{symbol}&theme=dark" width="100%" height="550px" frameborder="0"></iframe>'
    components.html(chart_html, height=550)

with col_trade:
    st.subheader("⚡ Quick Trade")
    qty = st.number_input("Qty", value=0.001, format="%.3f")
    
    if st.button("BUY / LONG", use_container_width=True, type="primary"):
        st.info("ઓર્ડર પ્લેસ કરવા માટે API કનેક્શન તપાસી રહ્યું છે...")
    
    st.divider()
    st.subheader("📊 Live Positions")
    st.write("પોઝિશન ડેટા લોડ થઈ રહ્યો છે...")

# ઓટો રિફ્રેશ
time.sleep(10)
st.rerun()