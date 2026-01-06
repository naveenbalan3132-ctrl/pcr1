import streamlit as st
import pandas as pd
import pyotp
from smartapi import SmartConnect
from datetime import datetime

st.set_page_config(page_title="NIFTY Live PCR (Broker API)")
st.title("📊 NIFTY Live Put Call Ratio (Broker Feed)")

# =============================
# AUTHENTICATION
# =============================
@st.cache_resource
def angel_login():
    api_key = st.secrets["ANGEL_API_KEY"]
    client_id = st.secrets["ANGEL_CLIENT_ID"]
    mpin = st.secrets["ANGEL_MPIN"]
    totp_secret = st.secrets["ANGEL_TOTP"]

    obj = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(totp_secret).now()

    session = obj.generateSession(client_id, mpin, totp)
    return obj

angel = angel_login()

# =============================
# FETCH OPTION CHAIN
# =============================
@st.cache_data(ttl=120)
def fetch_nifty_option_chain():
    response = angel.optionChain(
        exchange="NFO",
        symboltoken="26000",  # NIFTY token (Angel standard)
        interval="ONE_MINUTE"
    )
    return response["data"]

data = fetch_nifty_option_chain()

df = pd.DataFrame(data)

# =============================
# PCR CORE (INSTITUTIONAL)
# =============================
call_oi = df[df["optionType"] == "CE"]["openInterest"].sum()
put_oi = df[df["optionType"] == "PE"]["openInterest"].sum()

pcr = round(put_oi / call_oi, 3)

# =============================
# UI METRICS
# =============================
st.metric("Total Call OI", f"{int(call_oi):,}")
st.metric("Total Put OI", f"{int(put_oi):,}")
st.metric("Put Call Ratio", pcr)

# =============================
# SENTIMENT ENGINE
# =============================
if pcr >= 1.3:
    bias = "Strongly Bullish"
elif 1.1 <= pcr < 1.3:
    bias = "Bullish"
elif 0.9 <= pcr < 1.1:
    bias = "Neutral"
elif 0.7 <= pcr < 0.9:
    bias = "Bearish"
else:
    bias = "Strongly Bearish"

st.subheader("📌 Market Bias")
st.write(f"**{bias}**")

st.caption(
    f"Live via Angel One SmartAPI | "
    f"Updated: {datetime.now().strftime('%H:%M:%S')}"
)
