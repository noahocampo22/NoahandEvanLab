import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Stocks Page", layout="wide")
st.title("📈 Stocks Page")
st.write("Analyze historical stock price data using the Alpha Vantage API.")

# --- User Inputs ---
symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT):", "AAPL")
price_type = st.selectbox("Select Price Type:", ["Open", "High", "Low", "Close"])
days = st.slider("Select number of days:", 10, 100, 30)

# --- API Fetch Function ---
def fetch_stock_data(symbol):
    api_key = "FEX36O299U3YARGP"
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "compact"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

# --- Fetch and Display Logic ---
if st.button("Fetch Stock Data"):
    data = fetch_stock_data(symbol)

    # Check if API limit hit
    if data is None:
        st.error("No response from API.")
    elif "Note" in data:
        st.warning("API call frequency limit reached. Wait and try again.")
    elif "Error Message" in data:
        st.error("Invalid stock symbol.")
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
            except Exception as e:
                continue

        if records:
            df = pd.DataFrame(records)
            df = df.sort_values("Date").tail(days).set_index("Date")
            st.subheader(f"{symbol.upper()} - {price_type} Price History")
            st.dataframe(df)
            st.line_chart(df)
        else:
            st.error("No valid records returned.")
    else:
        st.error("Unexpected API response.")
