import streamlit as st
import pandas as pd
import pyotp
from smartapi import SmartConnect
from datetime import datetime

st.set_page_config(page_title="NIFTY Live PCR", layout="centered")
st.title("📊 NIFTY Live PCR Summary (Angel One API)")

# =====================================
# LOGIN (CACHED – INSTITUTIONAL STYLE)
# =====================================
@st.cache_resource
def angel_login():
    api_key = st.secrets["ANGEL_API_KEY"]
    client_id = st.secrets["ANGEL_CLIENT_ID"]
    mpin = st.secrets["ANGEL_MPIN"]
    totp_secret = st.secrets["ANGEL_TOTP_SECRET"]

    smart = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(totp_secret).now()
    smart.generateSession(client_id, mpin, totp)

    return smart

smart = angel_login()

# =====================================
# FETCH OPTION CHAIN (LIVE)
# =====================================
@st.cache_data(ttl=60)
def fetch_option_chain():
    """
    Angel One option chain for NIFTY
    """
    response = smart.optionChain(
        exchange="NFO",
        tradingsymbol="NIFTY",
        strikeprice=0,
        count=100
    )

    if "data" not in response:
        return None

    return pd.DataFrame(response["data"])

df = fetch_option_chain()

if df is None or df.empty:
    st.error("Live option data unavailable")
    st.stop()

# =====================================
# PCR CORE LOGIC (SUMMARY LEVEL)
# =====================================
total_call_oi = df[df["optiontype"] == "CE"]["openinterest"].sum()
total_put_oi = df[df["optiontype"] == "PE"]["openinterest"].sum()

pcr = round(total_put_oi / total_call_oi, 3)

# =====================================
# SUMMARY DASHBOARD
# =====================================
col1, col2, col3 = st.columns(3)

col1.metric("Total Call OI", f"{int(total_call_oi):,}")
col2.metric("Total Put OI", f"{int(total_put_oi):,}")
col3.metric("PCR", pcr)

# =====================================
# INSTITUTIONAL INTERPRETATION
# =====================================
st.subheader("📌 PCR Interpretation")

if pcr >= 1.3:
    st.success("Strongly Bullish (Put writing dominance)")
elif 1.1 <= pcr < 1.3:
    st.info("Bullish Bias")
elif 0.9 <= pcr < 1.1:
    st.warning("Neutral / Range-bound")
elif 0.7 <= pcr < 0.9:
    st.warning("Bearish Bias")
else:
    st.error("Strongly Bearish (Call writing dominance)")

st.caption(
    f"Live via Angel One SmartAPI | "
    f"Updated at {datetime.now().strftime('%H:%M:%S')}"
)
