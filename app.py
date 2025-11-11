import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
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
            "sparkline": True
        }
        response = requests.get(url, params=params)
        data = response.json()

        if not isinstance(data, list):
            st.warning("⚠ API returned unexpected data. Try again later.")
            return pd.DataFrame()

        coins = []
        for coin in data:
            change = coin.get("price_change_percentage_24h", 0) or 0

            if change > 2:
                signal = "🟢 BUY"
            elif change < -2:
                signal = "🔴 SELL"
            else:
                signal = "⚪ HOLD"

            coins.append({
                "Coin": coin["name"],
                "Symbol": coin["symbol"].upper(),
                "Price (USD)": coin["current_price"],
                "24h Change (%)": change,
                "24h Volume (USD)": coin["total_volume"],
                "Signal": signal,
                "Sparkline": coin.get("sparkline_in_7d", {}).get("price", [])
            })

        return pd.DataFrame(coins)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Fetch data
df = fetch_crypto_data()

if df.empty:
    st.stop()

# Display data table
st.dataframe(
    df[["Coin", "Symbol", "Price (USD)", "24h Change (%)", "24h Volume (USD)", "Signal"]],
    use_container_width=True
)
st.caption("🔁 Auto-refreshes every 60 seconds — powered by CoinGecko API")

# Select coin to view chart
selected_coin = st.selectbox("📈 Choose a coin to view 7-day trend:", df["Coin"])

coin_data = df[df["Coin"] == selected_coin].iloc[0]
sparkline = coin_data["Sparkline"]

# Chart for the selected coin
if isinstance(sparkline, list) and len(sparkline) > 0:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=sparkline,
        mode="lines",
        name=selected_coin,
        line=dict(width=2)
    ))
    fig.update_layout(
        title=f"{selected_coin} - 7 Day Price Trend",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("⚠ No 7-day chart data available for this coin."
        

# Manual refresh
if st.button("🔄 Refresh Now"):
    st.experimental_rerun()

# Auto-refresh every 60s
time.sleep(60)
st.experimental_rerun()
