import streamlit as st
import pandas as pd
import numpy as np
import requests

st.set_page_config(
    page_title="Institutional Multi-Timeframe Technical Analysis",
    layout="wide"
)

st.title("📊 Institutional Multi-Timeframe Technical Analysis")

# ======================================
# API KEY HANDLING (SAFE)
# ======================================
api_key = None

if "ALPHA_VANTAGE_KEY" in st.secrets:
    api_key = st.secrets["ALPHA_VANTAGE_KEY"]
else:
    api_key = st.text_input(
        "Enter Alpha Vantage API Key",
        type="password",
        help="Get a free key from https://www.alphavantage.co"
    )

if not api_key:
    st.warning("⚠️ Please enter API key to continue")
    st.stop()

# ======================================
# USER INPUT
# ======================================
symbol = st.text_input("Enter Symbol", "NIFTY")
market = st.selectbox("Market", ["India", "Global"])

if market == "India":
    symbol_api = f"{symbol}.BSE"
else:
    symbol_api = symbol

# ======================================
# DATA FETCH FUNCTION
# ======================================
def fetch_data(interval):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol_api,
        "interval": interval,
        "outputsize": "compact",
        "apikey": api_key
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    key = f"Time Series ({interval})"
    if key not in data:
        return None

    df = pd.DataFrame.from_dict(data[key], orient="index").astype(float)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    return df

# ======================================
# INDICATORS (PURE PANDAS)
# ======================================
def indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df

def bias_logic(row):
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

# ======================================
# MULTI-TIMEFRAME ANALYSIS
# ======================================
timeframes = {
    "15 Min": "15min",
    "Hourly": "60min"
}

results = []

with st.spinner("Fetching & analyzing data..."):
    for tf, interval in timeframes.items():
        df = fetch_data(interval)

        if df is None or len(df) < 60:
            continue

        df = indicators(df)
        last = df.iloc[-1]

        results.append({
            "Timeframe": tf,
            "Close": round(last["Close"], 2),
            "RSI": round(last["RSI"], 2),
            "EMA20": round(last["EMA20"], 2),
            "EMA50": round(last["EMA50"], 2),
            "Bias": bias_logic(last)
        })

# ======================================
# DISPLAY
# ======================================
if not results:
    st.error("❌ Data unavailable (API limit / wrong symbol)")
    st.stop()

df_result = pd.DataFrame(results)

st.subheader("📌 Multi-Timeframe Technical Summary")
st.dataframe(df_result, use_container_width=True)

bull = df_result[df_result["Bias"] == "Bullish"].shape[0]
bear = df_result[df_result["Bias"] == "Bearish"].shape[0]

st.subheader("🧠 Institutional Bias Engine")

if bull >= 2:
    st.success("📈 Strong Buy Bias (Timeframe Alignment)")
elif bear >= 2:
    st.error("📉 Strong Sell Bias (Timeframe Alignment)")
else:
    st.warning("⚠️ Sideways / No Trade Zone")

st.caption("Pure price-based | Cloud-safe | Institutional logic")
