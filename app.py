h9yHY7Dp8yVg3LPKLiHASU5uYB0DtLv4ar6jv30ERAcq4ZPbiqyYrZoUUxF9import streamlit as st
import pandas as pd
import requests
import time
import hmac
import hashlib
import json
import streamlit.components.v1 as components

# --- પેજ સેટઅપ ---
st.set_page_config(page_title="Yoga_Suchakam | Live Trader", layout="wide")

# API કી મેળવવી (Secrets માંથી)
API_KEY = st.secrets["DELTA_API_KEY"]
API_SECRET = st.secrets["DELTA_API_SECRET"]
BASE_URL = "https://api.delta.exchange"

# --- સુરક્ષા: API સહી (Signature) બનાવવાનું ફંક્શન ---
def generate_signature(method, path, payload, timestamp):
    signature_data = method + timestamp + path + payload
    return hmac.new(API_SECRET.encode('utf-8'), signature_data.encode('utf-8'), hashlib.sha256).hexdigest()

# --- ડેલ્ટા એક્સચેન્જ માંથી ડેટા મેળવવો ---
def delta_request(method, path, payload={}):
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
    if method == "GET":
        return requests.get(url, headers=headers).json()
    else:
        return requests.post(url, headers=headers, data=payload_str).json()

# --- લાઈવ ડેટા અને બેલેન્સ ---
def get_account_data():
    try:
        balance_data = delta_request("GET", "/v2/wallet/balances")
        # BTC અથવા USDT બેલેન્સ શોધો
        return balance_data['result']
    except: return []

# --- UI Layout ---
st.title("🧘 યોગ-સૂચકમ | LIVE TERMINAL")

symbol = st.sidebar.selectbox("Symbol", ["BTCUSD", "ETHUSD"])
account_info = get_account_data()

# સાઇડબારમાં સાચું બેલેન્સ
st.sidebar.subheader("💰 સાચું બેલેન્સ")
if account_info:
    for asset in account_info:
        st.sidebar.write(f"{asset['asset_symbol']}: {asset['balance']}")

# --- મુખ્ય વિભાગ: ચાર્ટ અને ટ્રેડિંગ ---
col_chart, col_trade = st.columns([3, 1])

with col_chart:
    # TradingView Live Chart
    chart_html = f'<iframe src="https://s.tradingview.com/widgetembed/?symbol=DELTA:{symbol}&theme=dark" width="100%" height="500px"></iframe>'
    components.html(chart_html, height=500)

with col_trade:
    st.subheader("⚡ Quick Order")
    qty = st.number_input("જથ્થો (Qty)", value=1, min_value=1)
    
    if st.button("BUY / LONG", use_container_width=True, type="primary"):
        # અસલી ઓર્ડર પ્લેસ કરવાનું લોજિક (સાવચેતીથી વાપરજો)
        # payload = {"product_id": 1, "size": qty, "side": "buy", "order_type": "market_order"}
        # res = delta_request("POST", "/v2/orders", payload)
        st.warning("લાઈવ ઓર્ડર ફંક્શન ટેસ્ટિંગમાં છે...")

st.divider()
st.subheader("📜 ઓપન પોઝિશન (Live Positions)")
# અહીં તમારી લાઈવ પોઝિશન દેખાશે
pos_data = delta_request("GET", "/v2/positions")
if pos_data and 'result' in pos_data:
    st.write(pos_data['result'])
else:
    st.info("કોઈ પોઝિશન ખુલ્લી નથી.")

# ઓટો રિફ્રેશ
time.sleep(5)
st.rerun()