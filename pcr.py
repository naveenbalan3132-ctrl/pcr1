import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime

st.set_page_config(page_title="Market Prediction Terminal", layout="wide")
st.title("📊 Market Prediction – India & Global")

# =========================================
# MARKET UNIVERSE (LEGAL SYMBOLS)
# =========================================
MARKETS = {
    "NIFTY 50 (India)": "^NSEI",
    "BANK NIFTY (India)": "^NSEBANK",
    "SENSEX (India)": "^BSESN",
    "S&P 500 (USA)": "^GSPC",
    "NASDAQ 100 (USA)": "^NDX",
    "DOW JONES (USA)": "^DJI",
    "FTSE 100 (UK)": "^FTSE",
    "DAX (Germany)": "^GDAXI",
    "NIKKEI 225 (Japan)": "^N225",
    "HANG SENG (Hong Kong)": "^HSI"
}

selected_market = st.selectbox("Select Market", list(MARKETS.keys()))
symbol = MARKETS[selected_market]

# =========================================
# FETCH DATA (LEGAL)
# =========================================
@st.cache_data(ttl=3600)
def fetch_data(symbol):
    df = yf.download(symbol, period="6mo", interval="1d")
    return df

df = fetch_data(symbol)

if df.empty:
    st.error("Market data unavailable")
    st.stop()

# =========================================
# TECHNICAL INDICATORS
# =========================================
df["EMA20"] = ta.trend.ema_indicator(df["Close"], window=20)
df["EMA50"] = ta.trend.ema_indicator(df["Close"], window=50)
df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
df["ATR"] = ta.volatility.average_true_range(
    df["High"], df["Low"], df["Close"], window=14
)

latest = df.iloc[-1]

# =========================================
# PREDICTION ENGINE (RULE BASED)
# =========================================
score = 0

if latest["Close"] > latest["EMA20"] > latest["EMA50"]:
    score += 2
elif latest["Close"] < latest["EMA20"] < latest["EMA50"]:
    score -= 2

if latest["RSI"] > 55:
    score += 1
elif latest["RSI"] < 45:
    score -= 1

if score >= 2:
    prediction = "Bullish Bias 📈"
elif score <= -2:
    prediction = "Bearish Bias 📉"
else:
    prediction = "Neutral / Range 🟡"

# =========================================
# DISPLAY TERMINAL
# =========================================
st.subheader(f"📍 {selected_market} – Market Snapshot")

col1, col2, col3 = st.columns(3)
col1.metric("Last Close", round(latest["Close"], 2))
col2.metric("RSI (14)", round(latest["RSI"], 2))
col3.metric("ATR (Volatility)", round(latest["ATR"], 2))

st.divider()

st.subheader("🧠 Market Prediction (Short-Term)")
st.write(f"### {prediction}")

st.info(
    "Prediction based on trend + momentum + volatility.\n"
    "Best used for **1–5 day directional bias**, not exact targets."
)

st.caption(
    f"Data Source: Yahoo Finance | "
    f"Last Updated: {df.index[-1].strftime('%d %b %Y')}"
)
