import streamlit as st

st.set_page_config(page_title="Web Development Lab03", layout="centered")

st.title("Web Development Lab03")

st.header("CS 1301")
st.subheader("Team 4, Web Development - Section A")
st.subheader("Noah Ocampo, Evan Sigman")

st.write("""
Welcome to our Streamlit Web Development Lab03 app! You can navigate between the pages using the sidebar to the left. The following pages are:

1. **Stock Viewer**: Uses the Alpha Vantage API to display daily stock data based on user-selected symbol and date.

2. **LLM Summary**: Uses Google Gemini to generate AI-written summaries of the stock data from Phase 2.

3. **AI Chatbot Implementation**: Uses an AI chatbot to answer any question you have from retrieving data from the stocks API

4. **Extra Page**: (Optional)
""")
