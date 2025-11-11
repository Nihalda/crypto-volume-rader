# ================================
# 🚀 Crypto Volume Radar (Streamlit)
# Track top 20 cryptos by 24h trading volume
# ================================

import streamlit as st
import pandas as pd
import requests
import numpy as np
import time

# --------------------------------
# Page setup
# --------------------------------
st.set_page_config(page_title="Crypto Volume Radar", page_icon="💹", layout="wide")
st.title("💹 Crypto Volume Radar")
st.caption("Track top 20 coins by 24h trading volume — Auto-refreshes every hour")

# --------------------------------
# Function to fetch crypto data
# --------------------------------
@st.cache_data(ttl=3600)  # auto-refresh every hour
def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 20,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data)[['name', 'symbol', 'current_price', 'price_change_percentage_24h', 'total_volume']]
    return df

# --------------------------------
# RSI Calculation Function
# --------------------------------
def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return None
    delta = np.diff(prices)
    gains = delta.clip(min=0)
    losses = -delta.clip(max=0)
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

# --------------------------------
# Fetch and process data
# --------------------------------
with st.spinner("Fetching live market data..."):
    df = fetch_crypto_data()

# --------------------------------
# Generate Buy/Sell Signals (approximation)
# --------------------------------
signals = []
for _, row in df.iterrows():
    # Simplified RSI based on price change %
    rsi_value = 50 + row['price_change_percentage_24h']  # rough estimate
    if rsi_value < 30:
        signal = "🟢 BUY"
    elif rsi_value > 70:
        signal = "🔴 SELL"
    else:
        signal = "⚪ HOLD"
    signals.append(signal)

df['Signal'] = signals
df.rename(columns={
    'name': 'Coin',
    'symbol': 'Symbol',
    'current_price': 'Price (USD)',
    'price_change_percentage_24h': '24h Change (%)',
    'total_volume': '24h Volume (USD)'
}, inplace=True)

# --------------------------------
# Display Data
# --------------------------------
st.dataframe(df.style.format({
    'Price (USD)': '${:,.2f}',
    '24h Change (%)': '{:.2f}%',
    '24h Volume (USD)': '${:,.0f}'
}))

st.success("✅ Auto-refresh every hour with latest data.")

# --------------------------------
# Optional Manual Refresh
# --------------------------------
if st.button("🔄 Refresh Now"):
    st.cache_data.clear()
    st.experimental_rerun()
