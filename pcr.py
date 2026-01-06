import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from io import BytesIO
import zipfile

st.set_page_config(page_title="NIFTY PCR Analysis", layout="centered")
st.title("📊 NIFTY Historical Put–Call Ratio (PCR)")
st.caption("Source: NSE Official FO Bhavcopy")

# ======================================
# USER INPUT
# ======================================
days = st.slider("Select number of past trading days", 5, 60, 20)

# ======================================
# NSE BHAVCOPY FETCH (LEGAL)
# ======================================
@st.cache_data
def fetch_bhavcopy(date):
    date_str = date.strftime("%d%m%Y")
    url = f"https://archives.nseindia.com/content/fo/fo{date_str}.zip"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None

        z = zipfile.ZipFile(BytesIO(r.content))
        csv_name = z.namelist()[0]
        df = pd.read_csv(z.open(csv_name))
        return df
    except:
        return None

# ======================================
# PCR CALCULATION
# ======================================
records = []
date = datetime.today()

with st.spinner("Fetching historical data..."):
    while len(records) < days:
        df = fetch_bhavcopy(date)

        if df is not None:
            nifty = df[
                (df["INSTRUMENT"] == "OPTIDX") &
                (df["SYMBOL"] == "NIFTY")
            ]

            if not nifty.empty:
                call_oi = nifty[nifty["OPTION_TYP"] == "CE"]["OPEN_INT"].sum()
                put_oi = nifty[nifty["OPTION_TYP"] == "PE"]["OPEN_INT"].sum()

                if call_oi > 0:
                    records.append({
                        "Date": date.date(),
                        "PCR": round(put_oi / call_oi, 3)
                    })

        date -= timedelta(days=1)

pcr_df = pd.DataFrame(records).sort_values("Date").reset_index(drop=True)

# ======================================
# DISPLAY TABLE
# ======================================
st.subheader("📋 Historical PCR Data")
st.dataframe(pcr_df, use_container_width=True)

# ======================================
# STREAMLIT NATIVE CHART (NO MATPLOTLIB)
# ======================================
st.subheader("📈 PCR Trend")
st.line_chart(pcr_df.set_index("Date")["PCR"])

# ======================================
# INTERPRETATION
# ======================================
latest_pcr = pcr_df.iloc[-1]["PCR"]

st.subheader("🧠 Market Sentiment")

if latest_pcr > 1.3:
    st.success("Extreme Bullish Sentiment (Put Heavy)")
elif 1.1 <= latest_pcr <= 1.3:
    st.info("Bullish Bias")
elif 0.9 <= latest_pcr < 1.1:
    st.warning("Neutral Zone")
elif 0.7 <= latest_pcr < 0.9:
    st.warning("Bearish Bias")
else:
    st.error("Extreme Bearish Sentiment")

st.caption("End-of-Day PCR | Suitable for Research & Analysis")
