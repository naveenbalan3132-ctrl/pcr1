import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="NIFTY Live PCR", layout="centered")

st.title("📊 NIFTY Live Put Call Ratio (PCR)")

# NSE URLs
BASE_URL = "https://www.nseindia.com"
OPTION_CHAIN_URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

# Headers to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

def get_nifty_pcr():
    session = requests.Session()
    session.headers.update(HEADERS)

    # First hit NSE homepage
    session.get(BASE_URL, timeout=5)
    response = session.get(OPTION_CHAIN_URL, timeout=5)

    data = response.json()

    records = data["records"]["data"]

    total_call_oi = 0
    total_put_oi = 0

    for record in records:
        if "CE" in record:
            total_call_oi += record["CE"]["openInterest"]
        if "PE" in record:
            total_put_oi += record["PE"]["openInterest"]

    pcr = round(total_put_oi / total_call_oi, 3)

    return total_call_oi, total_put_oi, pcr


# Auto refresh option
refresh = st.checkbox("🔄 Auto Refresh (30 sec)")

try:
    call_oi, put_oi, pcr_value = get_nifty_pcr()

    st.metric("Total Call OI", f"{call_oi:,}")
    st.metric("Total Put OI", f"{put_oi:,}")
    st.metric("Put Call Ratio (PCR)", pcr_value)

    if pcr_value > 1.2:
        st.success("📈 Market Sentiment: **Strongly Bullish**")
    elif 1.0 <= pcr_value <= 1.2:
        st.info("📊 Market Sentiment: **Bullish / Neutral**")
    elif 0.8 <= pcr_value < 1.0:
        st.warning("📉 Market Sentiment: **Bearish**")
    else:
        st.error("🔥 Market Sentiment: **Strongly Bearish**")

except Exception as e:
    st.error("⚠ NSE blocked the request. Please refresh after some time.")
    st.text(str(e))

if refresh:
    time.sleep(30)
    st.experimental_rerun()
