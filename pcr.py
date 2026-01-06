import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="NIFTY PCR (Official NSE Data)")
st.title("📊 NIFTY Put Call Ratio (Official NSE – Legal)")

@st.cache_data
def load_bhavcopy():
    date = datetime.now().strftime("%d%m%Y")

    url = (
        f"https://archives.nseindia.com/content/fo/"
        f"fo{date}.zip"
    )

    try:
        df = pd.read_csv(
            url,
            compression="zip"
        )
        return df
    except:
        return None

df = load_bhavcopy()

if df is None:
    st.error("Bhavcopy not yet available (published after market hours)")
    st.stop()

# Filter NIFTY options
df = df[
    (df["INSTRUMENT"] == "OPTIDX") &
    (df["SYMBOL"] == "NIFTY")
]

total_call_oi = df[df["OPTION_TYP"] == "CE"]["OPEN_INT"].sum()
total_put_oi = df[df["OPTION_TYP"] == "PE"]["OPEN_INT"].sum()

pcr = round(total_put_oi / total_call_oi, 3)

st.metric("Total Call OI", f"{total_call_oi:,}")
st.metric("Total Put OI", f"{total_put_oi:,}")
st.metric("PCR (EOD)", pcr)

st.caption("Source: NSE Official Bhavcopy (End-of-Day)")
