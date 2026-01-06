import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="Historical PCR Analysis", layout="centered")
st.title("📊 Historical Put–Call Ratio (PCR) – NIFTY")

# =====================================
# USER INPUT
# =====================================
days = st.slider("Select number of past trading days", 5, 60, 20)

# =====================================
# FUNCTION TO LOAD NSE BHAVCOPY
# =====================================
@st.cache_data
def load_bhavcopy(date):
    date_str = date.strftime("%d%m%Y")
    url = f"https://archives.nseindia.com/content/fo/fo{date_str}.zip"

    try:
        df = pd.read_csv(url, compression="zip")
        return df
    except:
        return None

# =====================================
# COLLECT HISTORICAL PCR
# =====================================
records = []
today = datetime.today()

while len(records) < days:
    df = load_bhavcopy(today)

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
                    "Date": today.date(),
                    "PCR": pcr
                })

    today -= timedelta(days=1)

pcr_df = pd.DataFrame(records).sort_values("Date")

# =====================================
# DISPLAY TABLE
# =====================================
st.subheader("📋 Historical PCR Table")
st.dataframe(pcr_df, use_container_width=True)

# =====================================
# PCR TREND CHART
# =====================================
st.subheader("📈 PCR Trend")

fig, ax = plt.subplots()
ax.plot(pcr_df["Date"], pcr_df["PCR"], marker="o")
ax.axhline(1.0, linestyle="--")
ax.set_ylabel("PCR")
ax.set_xlabel("Date")
ax.set_title("NIFTY Historical PCR")

st.pyplot(fig)

# =====================================
# INTERPRETATION
# =====================================
latest_pcr = pcr_df.iloc[-1]["PCR"]

st.subheader("🧠 Interpretation")

if latest_pcr > 1.3:
    st.success("Extreme Bullish Sentiment (Put heavy)")
elif 1.1 <= latest_pcr <= 1.3:
    st.info("Bullish Bias")
elif 0.9 <= latest_pcr < 1.1:
    st.warning("Neutral / Balanced")
elif 0.7 <= latest_pcr < 0.9:
    st.warning("Bearish Bias")
else:
    st.error("Extreme Bearish Sentiment")

st.caption("Source: NSE Official FO Bhavcopy | End-of-Day Data")
