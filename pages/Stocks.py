import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.title("📊 Stock Price Viewer")
st.write("Explore historical stock price data using the Alpha Vantage API.")

symbol = st.text_input("Enter a stock symbol (e.g., AAPL, MSFT):", value="AAPL").upper()
price_type = st.selectbox("Select price type to view:", ["Open", "High", "Low", "Close"])
num_days = st.slider("How many days of data to display?", 10, 1000, 30)

def fetch_stock_data(symbol):
    api_key = "FEX36O299U3YARGP"  
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "full"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

if st.button("Fetch Stock Data"):
    data = fetch_stock_data(symbol)

    if data is None:
        st.error("❌ Could not connect to the API.")
    elif "Note" in data:
        st.warning("⚠️ API rate limit reached. Try again shortly.")
    elif "Error Message" in data:
        st.error("❌ Invalid stock symbol. Please try again.")
    elif "Time Series (Daily)" in data:
        series = data["Time Series (Daily)"]
        column_map = {
            "Open": "1. open",
            "High": "2. high",
            "Low": "3. low",
            "Close": "4. close"
        }
        key = column_map[price_type]

        records = []
        for date_str, values in series.items():
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                price = float(values[key])
                records.append({"Date": date, f"{price_type} Price": price})
            except:
                continue

        if records:
            df = pd.DataFrame(records)
            df = df.sort_values("Date").tail(num_days).set_index("Date")
            st.subheader(f"{symbol} – {price_type} Price (Last {num_days} Days)")
            st.dataframe(df)
            st.line_chart(df)
        else:
            st.warning("⚠️ No valid data found in the API response.")
    else:
        st.error("❌ Unexpected response structure from the API.")
