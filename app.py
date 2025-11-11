import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from binance.client import Client
from datetime import datetime
import time

# ---------------------------
# Binance API setup
# ---------------------------
client = Client("", "")  # public data only; no trading keys

st.set_page_config(page_title="Crypto Volume Radar", layout="wide")

# ---------------------------
# Sidebar controls
# ---------------------------
st.sidebar.title("Crypto Dashboard Upgraded")
interval = st.sidebar.selectbox(
    "Select Interval",
    ["1d", "1h", "30m", "15m", "10m"]
)
limit = st.sidebar.slider("Number of Candles", 50, 500, 100)
refresh = st.sidebar.checkbox("Auto Refresh Every Minute", True)

# ---------------------------
# Fetch top coins by 24h volume
# ---------------------------
@st.cache_data(ttl=300)
def get_top_coins(limit=20):
    tickers = client.get_ticker()
    df = pd.DataFrame(tickers)
    df['quoteVolume'] = df['quoteVolume'].astype(float)
    df['priceChangePercent'] = df['priceChangePercent'].astype(float)
    top = df.sort_values('quoteVolume', ascending=False).head(limit)
    return top[['symbol', 'quoteVolume', 'lastPrice', 'priceChangePercent']]

top_coins = get_top_coins(limit=20)
coin_list = top_coins['symbol'].tolist()

# Dropdown to select coin
symbol = st.sidebar.selectbox("Select Coin", coin_list, index=0)

# ---------------------------
# Fetch historical data
# ---------------------------
@st.cache_data(ttl=60)
def fetch_data(symbol, interval, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'Open_time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close_time', 'Quote_asset_volume', 'Number_of_trades',
        'Taker_buy_base', 'Taker_buy_quote', 'Ignore'
    ])
    df['Open_time'] = pd.to_datetime(df['Open_time'], unit='ms')
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    return df

# ---------------------------
# Candlestick chart with SMA & max volume
# ---------------------------
def plot_candlestick(df, symbol):
    max_volume_idx = df['Volume'].idxmax()
    df['Max_Volume'] = False
    df.loc[max_volume_idx, 'Max_Volume'] = True

    # SMA signals
    df['SMA20'] = df['Close'].rolling(20).mean()
    df['SMA50'] = df['Close'].rolling(50).mean()
    df['Signal'] = ""
    df.loc[df['SMA20'] > df['SMA50'], 'Signal'] = "Buy"
    df.loc[df['SMA20'] < df['SMA50'], 'Signal'] = "Sell"

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['Open_time'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=symbol
    ))
    # Highlight max volume candle
    fig.add_trace(go.Scatter(
        x=df.loc[df['Max_Volume'], 'Open_time'],
        y=df.loc[df['Max_Volume'], 'High'],
        mode='markers',
        marker=dict(color='red', size=12, symbol='star'),
        name='Max Volume'
    ))
    # SMA lines
    fig.add_trace(go.Scatter(
        x=df['Open_time'],
        y=df['SMA20'],
        line=dict(color='blue', width=1),
        name='SMA20'
    ))
    fig.add_trace(go.Scatter(
        x=df['Open_time'],
        y=df['SMA50'],
        line=dict(color='orange', width=1),
        name='SMA50'
    ))
    fig.update_layout(
        title=f"{symbol} - {interval} Chart",
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        xaxis_rangeslider_visible=False,
        template='plotly_dark'
    )
    return fig, df

# ---------------------------
# Volume heatmap
# ---------------------------
def plot_volume_heatmap(top_coins_df):
    fig = px.imshow(
        [top_coins_df['quoteVolume'].values],
        labels=dict(x="Symbol", y="Volume", color="Volume"),
        x=top_coins_df['symbol'],
        y=["Volume"],
        color_continuous_scale='Viridis',
        text_auto=True
    )
    fig.update_layout(
        title="Top Coins by 24h Volume Heatmap",
        xaxis_title="Coin",
        yaxis_showticklabels=False,
        template='plotly_dark'
    )
    return fig

# ---------------------------
# Main dashboard layout
# ---------------------------
st.title("🚀 Crypto Dashboard Upgraded")

# Top coins leaderboard
st.subheader("Top Coins by 24h Volume")
st.dataframe(top_coins)

# Candlestick chart
data = fetch_data(symbol, interval, limit)
fig_chart, df_signals = plot_candlestick(data, symbol)
st.plotly_chart(fig_chart, use_container_width=True)

# Latest data with signals
st.subheader(f"Latest Data & Signals for {symbol}")
st.dataframe(df_signals.tail(10))

# Volume heatmap
st.subheader("Top Coins Volume Heatmap")
fig_heatmap = plot_volume_heatmap(top_coins)
st.plotly_chart(fig_heatmap, use_container_width=True)

# ---------------------------
# Auto-refresh logic
# ---------------------------
if refresh:
    while True:
        time.sleep(60)
        top_coins = get_top_coins(limit=20)
        data = fetch_data(symbol, interval, limit)
        fig_chart, df_signals = plot_candlestick(data, symbol)
        st.experimental_rerun()
