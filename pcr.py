import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta

st.set_page_config(page_title="Multi-Timeframe TA", layout="wide")
st.title("📊 Multi-Timeframe Technical Analysis Terminal")

# ============================
# USER INPUT
# ============================
symbol = st.text_input("Enter Symbol", "NIFTY50.NS")
timeframes = {
    "Daily": "1d",
    "Hourly": "1h",
    "15 Min": "15m"
}

# ============================
# TECHNICAL CALCULATIONS
# ============================
def analyze(df):
    df["EMA20"] = ta.trend.ema_indicator(df["Close"], 20)
    df["EMA50"] = ta.trend.ema_indicator(df["Close"], 50)
    df["RSI"] = ta.momentum.rsi(df["Close"], 14)
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()

    latest = df.iloc[-1]

    score = 0
    if latest["Close"] > latest["EMA20"] > latest["EMA50"]:
        score += 1
    if latest["RSI"] > 50:
        score += 1
    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 1

    if score >= 2:
        bias = "Bullish"
    elif score <= 1:
        bias = "Bearish"
    else:
        bias = "Neutral"

    return bias, latest

# ============================
# DATA FETCH
# ============================
results = []

for tf, interval in timeframes.items():
    data = yf.download(
        symbol,
        period="60d" if interval != "1d" else "6mo",
        interval=interval,
        progress=False
    )

    if data.empty:
        continue

    bias, latest = analyze(data)

    results.append({
        "Timeframe": tf,
        "Close": round(latest["Close"], 2),
        "RSI": round(latest["RSI"], 2),
        "EMA20": round(latest["EMA20"], 2),
        "EMA50": round(latest["EMA50"], 2),
        "MACD": round(latest["MACD"], 2),
        "Bias": bias
    })

# ============================
# DISPLAY
# ============================
df_result = pd.DataFrame(results)

st.subheader("📌 Multi-Timeframe Technical View")
st.dataframe(df_result, use_container_width=True)

# ============================
# FINAL SIGNAL ENGINE
# ============================
bullish_count = df_result[df_result["Bias"] == "Bullish"].shape[0]
bearish_count = df_result[df_result["Bias"] == "Bearish"].shape[0]

st.subheader("🧠 Institutional Bias Engine")

if bullish_count >= 2:
    st.success("📈 Strong Buy Bias (Multi-Timeframe Alignment)")
elif bearish_count >= 2:
    st.error("📉 Strong Sell Bias (Multi-Timeframe Alignment)")
else:
    st.warning("⚠️ No Clear Trend – Wait")

st.caption("For educational & analytical use only")
