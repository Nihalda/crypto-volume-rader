import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Crypto Volume Radar", page_icon="📈", layout="wide")

st.title("📊 Crypto Volume Radar")
st.markdown("Track top 20 coins by 24h trading volume — updates every 60 seconds")

# Function to fetch crypto data
def fetch_crypto_data():
    try:
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
            change = coin.get("price_change_percentage_24h", 0)
            if change is None:
                change = 0

            if change > 2:
                signal = "🟢 BUY"
            elif change < -2:
                signal = "🔴 SELL"
            else:
                signal = "⚪ HOLD"

            coins.append({
                "Coin": coin["name"],
                "Symbol": coin["symbol"].upper(),
                "Price (USD)": f"${coin['current_price']:,.2f}",
                "24h Change (%)": f"{change:.2f}%",
                "24h Volume (USD)": f"${coin['total_volume']:,.0f}",
                "Signal": signal
            })

        df = pd.DataFrame(coins)
        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Show data
df = fetch_crypto_data()
st.dataframe(df, use_container_width=True)
st.caption("🔁 Auto-refreshing every 60 seconds — powered by CoinGecko API")

# Refresh button
st.button("Refresh Now")

# Auto-refresh every 60 seconds (Streamlit Cloud safe)
st.experimental_rerun()
time.sleep(60)
