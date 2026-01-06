import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(
    page_title="NIFTY PCR Dashboard",
    layout="centered"
)

st.title("📊 NIFTY Put Call Ratio (Institutional Model)")

# =========================
# CONFIG
# =========================
BASE_URL = "https://www.nseindia.com"
OPTION_CHAIN_URL = (
    "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

CACHE_TTL = 600  # 10 minutes (INSTITUTIONAL STANDARD)

# =========================
# DATA FETCHER (SAFE)
# =========================
@st.cache_data(ttl=CACHE_TTL)
def fetch_nifty_option_chain():
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        session.get(BASE_URL, timeout=5)
        response = session.get(OPTION_CHAIN_URL, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()
        if "records" not in data:
            return None

        return data["records"]["data"]

    except Exception:
        return None


# =========================
# PCR CALCULATION CORE
# =========================
def calculate_pcr(records):
    call_oi = 0
    put_oi = 0

    for row in records:
        ce = row.get("CE")
        pe = row.get("PE")

        if ce:
            call_oi += ce.get("openInterest", 0)
        if pe:
            put_oi += pe.get("openInterest", 0)

    if call_oi == 0:
        return None

    pcr = round(put_oi / call_oi, 3)
    return call_oi, put_oi, pcr


# =========================
# UI CONTROLS
# =========================
if st.button("🔄 Refresh Data (Manual)"):
    st.cache_data.clear()

records = fetch_nifty_option_chain()

if records is None:
    st.error("⚠ Data temporarily unavailable (NSE blocked or slow)")
    st.info("💡 Institutional systems retry after few minutes")
    st.stop()

result = calculate_pcr(records)

if result is None:
    st.error("⚠ Unable to compute PCR")
    st.stop()

call_oi, put_oi, pcr = result

# =========================
# DISPLAY
# =========================
st.metric("Total Call OI", f"{call_oi:,}")
st.metric("Total Put OI", f"{put_oi:,}")
st.metric("Put Call Ratio", pcr)

# =========================
# SENTIMENT ENGINE
# =========================
if pcr >= 1.3:
    sentiment = "Strongly Bullish"
elif 1.1 <= pcr < 1.3:
    sentiment = "Bullish"
elif 0.9 <= pcr < 1.1:
    sentiment = "Neutral"
elif 0.7 <= pcr < 0.9:
    sentiment = "Bearish"
else:
    sentiment = "Strongly Bearish"

st.subheader("📌 Market Interpretation")
st.write(f"**{sentiment} Bias**")

st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}")
