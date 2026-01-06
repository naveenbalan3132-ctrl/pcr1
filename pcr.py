import streamlit as st
import pandas as pd
import pyotp
from smartapi import SmartConnect
from datetime import datetime

st.set_page_config(page_title="Intraday Stocks", layout="wide")
st.title("📈 Intraday Stocks Dashboard (Angel One API)")

# ======================================
# LOGIN (CACHED – SAFE)
# ======================================
@st.cache_resource
def angel_login():
    smart = SmartConnect(api_key=st.secrets["ANGEL_API_KEY"])
    totp = pyotp.TOTP(st.secrets["ANGEL_TOTP_SECRET"]).now()
    smart.generateSession(
        st.secrets["ANGEL_CLIENT_ID"],
        st.secrets["ANGEL_MPIN"],
        totp
    )
    return smart

smart = angel_login()

# ======================================
# STOCK LIST (EDITABLE)
# ======================================
STOCKS = {
    "RELIANCE": "2885",
    "TCS": "11536",
    "INFY": "1594",
    "ICICIBANK": "4963",
    "HDFCBANK": "1333"
}

# ======================================
# FETCH INTRADAY DATA
# ======================================
@st.cache_data(ttl=30)
def fetch_intraday_data():
    data = []

    for symbol, token in STOCKS.items():
        quote = smart.ltpData(
            exchange="NSE",
            tradingsymbol=symbol,
            symboltoken=token
        )

        ltp = quote["data"]["ltp"]
        open_price = quote["data"]["open"]
        high = quote["data"]["high"]
        low = quote["data"]["low"]
        prev_close = quote["data"]["close"]

        change_pct = round(
            ((ltp - prev_close) / prev_close) * 100, 2
        )

        data.append([
            symbol, ltp, open_price, high, low, prev_close, change_pct
        ])

    return pd.DataFrame(
        data,
        columns=[
            "Stock", "LTP", "Open", "High", "Low", "Prev Close", "Change %"
        ]
    )

df = fetch_intraday_data()

# ======================================
# DISPLAY TABLE
# ======================================
st.dataframe(
    df.style.format({
        "LTP": "₹{:.2f}",
        "Open": "₹{:.2f}",
        "High": "₹{:.2f}",
        "Low": "₹{:.2f}",
        "Prev Close": "₹{:.2f}",
        "Change %": "{:.2f}%"
    }),
    use_container_width=True
)

st.caption(
    f"Live data via Angel One SmartAPI | "
    f"Updated at {datetime.now().strftime('%H:%M:%S')}"
)
