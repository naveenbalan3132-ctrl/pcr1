import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Indian Stock Screener (NSE Data)", layout="wide")
st.title("Indian Stock Screener - NSE Data")

# NSE endpoint for all stock info
NSE_URL = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

@st.cache_data(ttl=300)
def fetch_nse_data():
    session = requests.Session()
    # NSE requires a preliminary request to set cookies
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(NSE_URL, headers=headers)
    data = response.json()
    # Extract useful fields
    df = pd.DataFrame(data['data'])
    df = df[['symbol', 'open', 'dayHigh', 'dayLow', 'lastPrice', 'totalTradedVolume', 'totalTradedValue', 'pChange']]
    # Convert numeric columns
    for col in ['open','dayHigh','dayLow','lastPrice','totalTradedVolume','totalTradedValue','pChange']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df = fetch_nse_data()

# Sidebar filters
st.sidebar.header("Filters")
price_min, price_max = st.sidebar.slider("Last Price Range", float(df['lastPrice'].min()), float(df['lastPrice'].max()), (float(df['lastPrice'].min()), float(df['lastPrice'].max())))
volume_min, volume_max = st.sidebar.slider("Volume Range", int(df['totalTradedVolume'].min()), int(df['totalTradedVolume'].max()), (int(df['totalTradedVolume'].min()), int(df['totalTradedVolume'].max())))
pchange_min, pchange_max = st.sidebar.slider("% Change Range", float(df['pChange'].min()), float(df['pChange'].max()), (float(df['pChange'].min()), float(df['pChange'].max())))

# Apply filters
filtered_df = df[
    (df['lastPrice'] >= price_min) & (df['lastPrice'] <= price_max) &
    (df['totalTradedVolume'] >= volume_min) & (df['totalTradedVolume'] <= volume_max) &
    (df['pChange'] >= pchange_min) & (df['pChange'] <= pchange_max)
]

st.write(f"Showing {len(filtered_df)} stocks")
st.dataframe(filtered_df.sort_values(by='lastPrice', ascending=False))
