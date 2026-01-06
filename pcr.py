import streamlit as st
import requests
import pandas as pd
import numpy as np
import datetime
import ta  # Technical Analysis library

st.set_page_config(page_title="Technical Stock Screener (NSE)", layout="wide")
st.title("Technical Stock Screener - NSE Stocks")

# Helper function to get NSE historical data
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

# Sidebar inputs
symbol = st.text_input("Enter NSE Stock Symbol (e.g., INFY, TCS)", value="INFY").upper()
start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=180))
end_date = st.date_input("End Date", datetime.date.today())

if st.button("Get Technical Analysis"):

    df = get_nse_historical(symbol, start_date.strftime('%d-%m-%Y'), end_date.strftime('%d-%m-%Y'))
    
    if df is None or df.empty:
        st.error("No data found for this symbol!")
    else:
        # Compute Technical Indicators
        df['SMA20'] = ta.trend.sma_indicator(df['close'], window=20)
        df['SMA50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['EMA20'] = ta.trend.ema_indicator(df['close'], window=20)
        df['RSI14'] = ta.momentum.rsi(df['close'], window=14)
        macd = ta.trend.MACD(df['close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['BB_upper'] = ta.volatility.BollingerBands(df['close']).bollinger_hband()
        df['BB_lower'] = ta.volatility.BollingerBands(df['close']).bollinger_lband()
        
        st.subheader(f"{symbol} Technical Data")
        st.dataframe(df.tail(10))  # Show last 10 rows

        # Simple technical screen example
        st.subheader("Technical Screener Signals")
        signals = []

        if df['close'].iloc[-1] > df['SMA50'].iloc[-1]:
            signals.append("Price above 50-SMA (Bullish)")
        else:
            signals.append("Price below 50-SMA (Bearish)")

        if df['RSI14'].iloc[-1] < 30:
            signals.append("RSI oversold (Buy opportunity)")
        elif df['RSI14'].iloc[-1] > 70:
            signals.append("RSI overbought (Sell signal)")

        if df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1]:
            signals.append("MACD bullish crossover")
        else:
            signals.append("MACD bearish crossover")

        st.write(signals)
