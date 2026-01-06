import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="NIFTY PCR Analysis", layout="centered")
st.title("📊 NIFTY Historical PCR (Official NSE Data)")

# ===============================
# USER INPUT
# ===============================
days = st.slider("Select past trading days", 5, 60, 20)

# ===============================
# LOAD NSE FO BHAVCOPY
# ===============================
@st.cache_data
def load_bhavcopy(date):
    date_str = date.strftime("%d%m%Y")
    url = f"https://archives.nseindia.com/content/fo/fo{date_str}.zip"
    try:
        return pd.read_csv(url, compression="zip")
    except:
        return None

# ===============================
# CALCULATE PCR
# ===============================
records = []
current_date = datetime.today()

while len(records) < days:
    df = load_bhavcopy(current_date)

    if df is not None:
        nifty = df[
            (df["INSTRUMENT"] == "OPTIDX") &
            (df["SYMBOL"] == "NIFTY")
        ]

        if not nifty.empty:
            call_oi = nifty[nifty["OPTION_TYP"] == "CE"]["OPEN_INT"].sum()
            put_oi = nifty[nifty["OPTION_TYP"] == "PE"]["OPEN_INT"].sum()

            if call_oi > 0:
                pcr = round(put_oi / call_oi, 3)
                records.append({
                    "Date": current_date.date(),
                    "PCR": pcr
                })

    current_date -= timedelta(days=1)

pcr_df = pd.DataFrame(records).sort_values("Date").set_index("Date")

# ===============================
# DISPLAY DATA
# ===============================
st.subheader("📋 PCR Data")
st.dataframe(pcr_df, use_container_width=True)

# ===============================
# PCR CHART (NO MATPLOTLIB)
# ===============================
st.subheader("📈 PCR Trend")
st.line_chart(pcr_df["PCR"])

# ===============================
# INTERPRETATION
# ===============================
latest_pcr = pcr_df.iloc[-1]["PCR"]

st.subheader("🧠 Market Sentiment")

if latest_pcr > 1.3:
    st.success("Extreme Bullish (Put-heavy positioning)")
elif 1.1 <= latest_pcr <= 1.3:
    st.info("Bullish Bias")
elif 0.9 <= latest_pcr < 1.1:
    st.warning("Neutral Zone")
elif 0.7 <= latest_pcr < 0.9:
    st.warning("Bearish Bias")
else:
    st.error("Extreme Bearish Sentiment")

st.caption("Source: NSE Official FO Bhavcopy | End-of-Day Data")
