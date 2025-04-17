import streamlit as st
import requests
from datetime import datetime, timedelta

# --- Page Setup ---
st.set_page_config(page_title="Stock Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 AI Stock Chatbot")
st.write("Ask any question about recent trends in stock performance!")

# --- Inputs ---
symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA):", "AAPL").upper()
user_question = st.text_area("Ask a question about recent stock trends:", placeholder="e.g. Were prices in March higher than usual?")
num_days = st.slider("How many recent trading days to include in context:", 5, 100, 30)

# --- Fetch stock data from Alpha Vantage ---
def get_stock_history(symbol, num_days):
    try:
        api_key = "FEX36O299U3YARGP"
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": api_key,
            "outputsize": "full"  # So we can go back farther than 100 days if needed
        }
        response = requests.get(url, params=params)
        data = response.json()

        series = data.get("Time Series (Daily)", {})
        if not series:
            return None

        records = []
        for date_str in sorted(series.keys(), reverse=True):
            try:
                record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
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

# --- Format data into a summary string for Gemini ---
def format_stock_summary(symbol, data):
    summary = f"Recent stock data for {symbol.upper()}:\n"
    for entry in data:
        summary += (f"{entry['date']}: Open={entry['open']}, High={entry['high']}, "
                    f"Low={entry['low']}, Close={entry['close']}, Volume={entry['volume']}\n")
    return summary

# --- Gemini API Request ---
def ask_gemini(prompt):
    try:
        key = "AIzaSyDV9L06iMrD4vf-PDnOFUqo0P_3ijsV4AQ"  # Replace with your actual key
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
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

# --- Ask button logic ---
if st.button("Ask Gemini"):
    if not symbol or not user_question.strip():
        st.warning("Please enter a symbol and a question.")
    else:
        st.info("Fetching stock data...")
        stock_data = get_stock_history(symbol, num_days)
        if not stock_data:
            st.error("Unable to retrieve stock data. Please check the symbol or try again later.")
        else:
            summary = format_stock_summary(symbol, stock_data)
            prompt = f"""
            The user will ask a question about stock trends. Use the data below to answer with helpful insights.

            {summary}

            Question: {user_question.strip()}
            """
            st.info("Sending data to Gemini...")
            reply = ask_gemini(prompt)
            st.markdown("### 💬 Gemini’s Answer")
            st.success(reply.strip())
