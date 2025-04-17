import streamlit as st
import requests
from datetime import datetime, timedelta

st.title("🤖 AI Stock Chatbot")
st.write("Ask any question about recent stock performance trends.")

symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA):", "AAPL").upper()
user_question = st.text_area("Ask a question about this stock:", placeholder="e.g. Were prices in March higher than usual?")
num_days = st.slider("How many trading days to include:", 5, 200, 60)

def get_stock_history(symbol, num_days):
    try:
        api_key = "FEX36O299U3YARGP"
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": api_key,
            "outputsize": "full"
        }
        response = requests.get(url, params=params)
        data = response.json()

        series = data.get("Time Series (Daily)", {})
        if not series:
            return None

        records = []
        for date_str in sorted(series.keys(), reverse=True):
            try:
                if len(records) >= num_days:
                    break
                stock = series[date_str]
                records.append({
                    "date": date_str,
                    "open": stock["1. open"],
                    "high": stock["2. high"],
                    "low": stock["3. low"],
                    "close": stock["4. close"],
                    "volume": stock["5. volume"]
                })
            except:
                continue
        return records
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return None

def format_stock_summary(symbol, data):
    summary = f"Recent stock data for {symbol.upper()}:\n"
    for entry in data:
        summary += (f"{entry['date']}: Open={entry['open']}, High={entry['high']}, "
                    f"Low={entry['low']}, Close={entry['close']}, Volume={entry['volume']}\n")
    return summary

def ask_gemini(prompt):
    try:
        gemini_key = "AIzaSyDV9L06iMrD4vf-PDnOFUqo0P_3ijsV4AQ"
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
        headers = {"Content-Type": "application/json"}
        body = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }]
        }
        response = requests.post(gemini_url, headers=headers, json=body)
        if response.status_code != 200:
            raise Exception(f"Gemini API error {response.status_code}: {response.text}")
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"⚠️ Gemini API Error: {e}"

if st.button("Ask Gemini"):
    if not symbol or not user_question.strip():
        st.warning("Please enter a stock symbol and a question.")
    else:
        st.info("Fetching stock data...")
        stock_data = get_stock_history(symbol, num_days)
        if not stock_data:
            st.error("Unable to retrieve stock data. Please check the symbol or try again.")
        else:
            summary = format_stock_summary(symbol, stock_data)
            prompt = f"""
            Use the following time series data to answer the user's question about recent stock trends.

            {summary}

            Question: {user_question.strip()}
            """
            st.info("Sending to Gemini...")
            reply = ask_gemini(prompt)
            st.markdown("### 💬 Gemini’s Response")
            st.success(reply.strip())
