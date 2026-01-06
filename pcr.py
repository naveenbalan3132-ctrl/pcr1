import streamlit as st
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="Multi-Timeframe TA", layout="wide")
st.title("📊 Institutional Multi-Timeframe Technical Analysis")

API_KEY = st.secrets["ALPHA_VANTAGE_KEY"]

# =========================
# USER INPUT
# =========================
symbol = st.text_input("Enter Symbol", "NIFTY")
market = st.selectbox("Market", ["India", "Global"])

if market == "India":
    symbol_api = f"{symbol}.BSE"
else:
    symbol_api = symbol

# =========================
# DATA FETCH
# =========================
def fetch_data(interval):
    url = (
        "https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_INTRADAY"
        f"&symbol={symbol_api}"
        f"&interval={interval}"
        f"&outputsize=compact"
        f"&apikey={API_KEY}"
    )

    r = requests.get(url)
    data = r.json()

    key = f"Time Series ({interval})"
    if key not in data:
        return None

    df = pd.DataFrame.from_dict(data[key], orient="index")
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    }, inplace=True)

    return df

# =========================
# INDICATORS (NO LIBRARY)
# =========================
def calculate_indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df

def get_bias(row):
    score = 0
    if row["Close"] > row["EMA20"] > row["EMA50"]:
        score += 1
    if row["RSI"] > 50:
        score += 1

    if score == 2:
        return "Bullish"
    elif score == 0:
        return "Bearish"
    else:
        return "Neutral"

# =========================
# ANALYSIS
# =========================
timeframes = {
    "15 Min": "15min",
    "Hourly": "60min"
}

results = []

with st.spinner("Fetching & analyzing data..."):
    for tf, interval in timeframes.items():
        df = fetch_data(interval)
        if df is None or len(df) < 50:
            continue

        df = calculate_indicators(df)
        latest = df.iloc[-1]

        results.append({
            "Timeframe": tf,
            "Close": round(latest["Close"], 2),
            "RSI": round(latest["RSI"], 2),
            "EMA20": round(latest["EMA20"], 2),
            "EMA50": round(latest["EMA50"], 2),
            "Bias": get_bias(latest)
        })

# =========================
# OUTPUT
# =========================
result_df = pd.DataFrame(results)

st.subheader("📌 Multi-Timeframe View")
st.dataframe(result_df, use_container_width=True)

bullish = result_df[result_df["Bias"] == "Bullish"].shape[0]
bearish = result_df[result_df["Bias"] == "Bearish"].shape[0]

st.subheader("🧠 Final Institutional Bias")

if bullish >= 2:
    st.success("📈 Strong Buy Bias")
elif bearish >= 2:
    st.error("📉 Strong Sell Bias")
else:
    st.warning("⚠️ No Trade Zone")

st.caption("Pure price-based, cloud-safe, institutional logic")
