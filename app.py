import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Crypto Volume Radar", page_icon="📈", layout="wide")

st.title("📊 Crypto Volume Radar")
st.markdown("Track top 20 coins by 24h trading volume — updates automatically every 60 seconds")

placeholder = st.empty()

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

    coins = []
    for coin in data:
        signal = "BUY" if coin["price_change_percentage_24h"] > 2 else \
                 "SELL" if coin["price_change_percentage_24h"] < -2 else "HOLD"
        coins.append({
            "Coin": coin["name"],
            "Symbol": coin["symbol"].upper(),
            "Price (USD)": f"${coin['current_price']:,.2f}",
            "24h Change (%)": f"{coin['price_change_percentage_24h']:.2f}%",
            "24h Volume (USD)": f"${coin['total_volume']:,.0f}",
            "Signal": signal
        })

    df = pd.DataFrame(coins)
    return df

while True:
    df = fetch_crypto_data()
    with placeholder.container():
        st.dataframe(df, use_container_width=True)
        st.caption("🔁 Auto-refreshing every 60 seconds — powered by CoinGecko API")
    time.sleep(60)
