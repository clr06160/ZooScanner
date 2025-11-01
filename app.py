import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import warnings
import base64  # For embedded images

warnings.filterwarnings("ignore")

# FMP KEY
api_key = st.secrets["FMP_API_KEY"]

# Base64-encoded images (embedded—no URLs, no 404s)
BEAR_IMAGE = "iVBORw0KGgoAAAANSUhEUgAA...[truncated for brevity—full base64 in your repo; I can provide if needed]"
LION_IMAGE = "iVBORw0KGgoAAAANSUhEUgAA...[truncated]"
PHOENIX_IMAGE = "iVBORw0KGgoAAAANSUhEUgAA...[truncated]"
TURTLE_IMAGE = "iVBORw0KGgoAAAANSUhEUgAA...[truncated]"

def get_zoo_animal(ticker):
    ticker = ticker.upper().strip()
    if not ticker:
        return "Error", "Empty ticker", None

    # Quote
    quote = requests.get(f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}").json()
    if not quote or len(quote) == 0:
        return "Ghost", "No data", None
    q = quote[0]
    price = q.get('price', 0)
    volume = q.get('volume', 0)
    avg_vol = q.get('avgVolume', volume)
    vol_spike = volume > avg_vol * 1.5

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
        df['close'] = df['close'].astype(float)
        df['rsi'] = ta.rsi(df['close'], length=14)
        rsi_val = df['rsi'].iloc[-1]
        if pd.notna(rsi_val):
            rsi = rsi_val

    # Animal Logic (Simple if blocks)
    if rsi > 60:
        animal = "Lion"
        reason = f"RSI {rsi:.1f} – momentum!"
        img = LION_IMAGE
    elif revenue_growth > 5:
        animal = "Phoenix"
        reason = f"+{revenue_growth:.1f}% growth!"
        img = PHOENIX_IMAGE
    elif rsi < 50:
        animal = "Bear"
        reason = f"RSI {rsi:.1f} – oversold"
        img = BEAR_IMAGE
    else:
        animal = "Turtle"
        reason = f"${price:.2f} – steady"
        img = TURTLE_IMAGE

    return animal, reason, img

# APP
st.set_page_config(page_title="ZooScanner")
st.title("ZooScanner")
st.write("**Type a stock → get your animal**")

user_input = st.text_input("Ticker (NVDA, AAPL, TSLA, IREN)", "")

if user_input:
    animal, reason, img = get_zoo_animal(user_input)
    if animal == "Ghost":
        st.error("Not found.")
    else:
        col1, col2 = st.columns([1, 3])
        with col1:
            if img:
                st.image(base64.b64decode(img), use_column_width=True)
            else:
                st.image("https://via.placeholder.com/300?text=No+Image", use_column_width=True)
        with col2:
            st.markdown(f"### {animal} {user_input.upper()}")
            st.write(reason)























