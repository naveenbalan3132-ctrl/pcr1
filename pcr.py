import streamlit as st
import requests
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Technical Stock Screener (NSE)", layout="wide")
st.title("Technical Stock Screener - NSE Stocks")

# -------------------------------
# Helper function to get NSE historical data
# -------------------------------
def get_nse_historical(symbol, start_date, end_date):
    """
    Fetch historical data from NSE official JSON API
    """
    url = f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22EQ%22]&from={start_date}&to={end_date}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)  # Initialize cookies
    response = session.get(url, headers=headers)
    data = response.json()
    df = pd.DataFrame(data['data'])
    if df.empty:
        return None
    df['date'] = pd.to_datetime(df['CH_DT'], format='%d-%b-%Y')
    df['close'] = pd.to_numeric(df['CLOSE_PRICE'], errors='coerce')
    df['open'] = pd.to_numeric(df['OPEN_PRICE'], errors='coerce')
    df['high'] = pd.to_numeric(df['HIGH_PRICE'], errors='coerce')
    df['low'] = pd.to_numeric(df['LOW_PRICE'], errors='coerce')
    df['volume'] = pd.to_numeric(df['TOTTRDQTY'], errors='coerce')
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']].sort_values('date')
    return df

# -------------------------------
# Technical Indicators (Pandas only)
# -------------------------------
def add_technical_indicators(df):
    # SMA & EMA
    df['SMA20'] = df['close'].rolling(window=20).mean()
    df['SMA50'] = df['close'].rolling(window=50).mean()
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    
    # RSI14
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['RSI14'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    df['BB_middle'] = df['close'].rolling(window=20).mean()
    df['BB_std'] = df['close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + 2 * df['BB_std']
    df['BB_lower'] = df['BB_middle'] - 2 * df['BB_std']
    
    return df

# -------------------------------
# Streamlit Sidebar Inputs
# -------------------------------
symbol = st.text_input("Enter NSE Stock Symbol (e.g., INFY, TCS)", value="INFY").upper()
start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=180))
end_date = st.date_input("End Date", datetime.date.today())

if st.button("Get Technical Analysis"):

    df = get_nse_historical(symbol, start_date.strftime('%d-%m-%Y'), end_date.strftime('%d-%m-%Y'))
    
    if df is None or df.empty:
        st.error("No data found for this symbol!")
    else:
        df = add_technical_indicators(df)
        
        st.subheader(f"{symbol} Technical Data (Last 10 Days)")
        st.dataframe(df.tail(10))  # Show last 10 rows
        
        # -------------------------------
        # Simple Technical Screener Signals
        # -------------------------------
        st.subheader("Technical Screener Signals")
        signals = []

        # SMA50
        if df['close'].iloc[-1] > df['SMA50'].iloc[-1]:
            signals.append("Price above 50-SMA (Bullish)")
        else:
            signals.append("Price below 50-SMA (Bearish)")

        # RSI
        if df['RSI14'].iloc[-1] < 30:
            signals.append("RSI oversold (Buy opportunity)")
        elif df['RSI14'].iloc[-1] > 70:
            signals.append("RSI overbought (Sell signal)")

        # MACD
        if df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1]:
            signals.append("MACD bullish crossover")
        else:
            signals.append("MACD bearish crossover")
        
        # Bollinger Bands
        if df['close'].iloc[-1] > df['BB_upper'].iloc[-1]:
            signals.append("Price above upper Bollinger Band (Overbought)")
        elif df['close'].iloc[-1] < df['BB_lower'].iloc[-1]:
            signals.append("Price below lower Bollinger Band (Oversold)")

        st.write(signals)
