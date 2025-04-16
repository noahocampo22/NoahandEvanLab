import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.title("📈 Stock Facts")

st.write("Welcome to our AI-powered stock insight tool! Enter a stock symbol and choose a trading date to get a personalized market summary generated by Google Gemini.")

symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA):", placeholder="e.g. AAPL").upper()
date = st.date_input("Select a date to analyze (must be a market day):")

if st.button("Generate Summary"):

    alpha_key = "FEX36O299U3YARGP"
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": alpha_key,
        "outputsize": "compact"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        series = data.get("Time Series (Daily)", {})
        date_str = date.strftime("%Y-%m-%d")

        if date_str in series:
            stock = series[date_str]
            open_price = stock["1. open"]
            high = stock["2. high"]
            low = stock["3. low"]
            close = stock["4. close"]
            volume = stock["5. volume"]

            with st.expander("📊 View Raw Stock Data"):
                df = pd.DataFrame({
                    "Metric": ["Open", "High", "Low", "Close", "Volume"],
                    "Value": [open_price, high, low, close, volume]
                })
                st.dataframe(df)

            prompt = f"""
            Provide a short daily summary for {symbol.upper()} stock on {date_str}.
            Use this data:
            - Open: {open_price}
            - High: {high}
            - Low: {low}
            - Close: {close}
            - Volume: {volume}

            Then add a fun fact related to something unusual, surprising, or historic that happened involving this company on or around that day. 
            Start the fun fact section with "Fun Fact:".
            """

            gemini_key = "AIzaSyDV9L06iMrD4vf-PDnOFUqo0P_3ijsV4AQ" 
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            headers = {"Content-Type": "application/json"}
            body = {
                "contents": [{
                    "role": "user",
                    "parts": [{"text": prompt}]
                }]
            }

            gemini_response = requests.post(gemini_url, headers=headers, json=body)

            if gemini_response.status_code == 200:
                result = gemini_response.json()
                full_text = result['candidates'][0]['content']['parts'][0]['text']

                if "Fun Fact:" in full_text:
                    summary_part, fun_fact = full_text.split("Fun Fact:", 1)
                else:
                    summary_part = full_text
                    fun_fact = "No fun fact available for this company."

                st.markdown("### 📈 Daily Market Summary")
                st.info(summary_part.strip())

                st.markdown("### 💡 Fun Fact of the Day")
                st.success(fun_fact.strip())
            else:
                st.error("❌ Failed to retrieve a response from Gemini.")
        else:
            st.warning(f"No trading data found for {symbol} on {date_str}. Try another weekday.")
    else:
        st.error("Alpha Vantage API call failed. Please check your symbol or try again later.")
