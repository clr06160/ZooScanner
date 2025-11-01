import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import warnings
warnings.filterwarnings("ignore")

# FMP KEY
api_key = st.secrets["FMP_API_KEY"]

def get_zoo_animal(ticker):
    ticker = ticker.upper().strip()
    if not ticker:
        return "Error", "Empty", "images/turtle.jpg"

    # Quote
    quote = requests.get(f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}").json()
    if not quote or len(quote) == 0:
        return "Ghost", "No data", "images/turtle.jpg"
    q = quote[0]
    price = q.get('price', 0)

    # Revenue Growth
    profile = requests.get(f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}").json()
    revenue_growth = 0
    if profile and len(profile) > 0 and 'revenueGrowth' in profile[0]:
        revenue_growth = profile[0]['revenueGrowth'] * 100

    # RSI
    hist = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={api_key}&limit=30").json()
    rsi = 50
    if 'historical' in hist and len(hist['historical']) >= 14:
        df = pd.DataFrame(hist['historical'])
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df = df.dropna(subset=['close'])
        if len(df) >= 14:
            df['rsi'] = ta.rsi(df['close'], length=14)
            rsi_val = df['rsi'].iloc[-1]
            if pd.notna(rsi_val):
                rsi = rsi_val

    # Animal + YOUR IMAGES
    if rsi > 60:
        return "Lion", f"RSI {rsi:.1f} – momentum!", "images/lion.jpg"
    elif revenue_growth > 5:
        return "Phoenix", f"+{revenue_growth:.1f}% growth!", "images/phoenix.jpg"
    elif rsi < 50:
        return "Bear", f"RSI {rsi:.1f} – oversold", "images/bear.jpg"
    else:
        return "Turtle", f"${price:.2f} – steady", "images/turtle.jpg"

# APP
st.set_page_config(page_title="ZooScanner")
st.title("ZooScanner")
st.write("**Type a stock → get your animal**")

user_input = st.text_input("Ticker", "")

if user_input:
    animal, reason, img = get_zoo_animal(user_input)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(img, use_column_width=True)
    with col2:
        st.markdown(f"### {animal} {user_input.upper()}")
        st.write(reason)
























