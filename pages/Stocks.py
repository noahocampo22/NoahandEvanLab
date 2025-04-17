import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- Page setup ---
st.set_page_config(page_title="Stocks Page", page_icon="📈", layout="centered")
st.title("📈 Stocks Page")
st.write("Analyze historical stock price data using the Alpha Vantage API.")

# --- User Inputs ---
symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT):", "AAPL").upper()
price_type = st.selectbox("Select Price Type:", ["Open", "High", "Low", "Close"])
days = st.slider("Select number of days to display:", 10, 1000, 30)
st.caption("Note: You can enter a symbol and view data going back years. Max 20+ years of historical records.")

# --- Fetch stock data ---
def fetch_stock_data(symbol):
    api_key = st.secrets["key"]  # Pull Gemini/Alpha Vantage key from Streamlit secrets
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "full"  # Get full history (enables >1000 days if needed)
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

# --- Display data ---
if st.button("Fetch Stock Data"):
    data = fetch_stock_data(symbol)

    if data is None:
        st.error("❌ No response from Alpha Vantage API.")
    elif "Note" in data:
        st.warning("⚠️ API limit reached. Try again in a minute.")
    elif "Error Message" in data:
        st.error("❌ Invalid stock symbol.")
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
            df = df.sort_values("Date").tail(days).set_index("Date")
            st.subheader(f"{symbol.upper()} - {price_type} Price History")
            st.dataframe(df)
            st.line_chart(df)
        else:
            st.warning("⚠️ No valid price records found.")
    else:
        st.error("❌ Unexpected API response format.")
