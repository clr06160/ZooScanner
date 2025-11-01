import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import warnings
from contextlib import contextmanager
import io
import sys

warnings.filterwarnings("ignore")

@contextmanager
def suppress_stdout():
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout

# FMP KEY
api_key = st.secrets["FMP_API_KEY"]

def get_zoo_animal(ticker):
    ticker = ticker.upper().strip()
    if not ticker:
        return "Error", "Empty ticker", "https://via.placeholder.com/200?text=Error"

    # Quote
    quote = requests.get(f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}").json()
    if not quote or len(quote) == 0:
        return "Ghost", "No data", "https://via.placeholder.com/200?text=Ghost"
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
        with suppress_stdout():
            df['rsi'] = ta.rsi(df['close'], length=14)
        rsi_val = df['rsi'].iloc[-1]
        if pd.notna(rsi_val):
            rsi = rsi_val

    # Animal Logic (Simple Steps)
    if rsi > 60:
        animal = "Lion"
        reason = f"RSI {rsi:.1f} – momentum!"
        img = "https://cdn.pixabay.com/photo/2015/09/15/14/09/lion-940142_1280.jpg"
    elif revenue_growth > 5:
        animal = "Phoenix"
        reason = f"+{revenue_growth:.1f}% growth!"
        img = "https://cdn.pixabay.com/photo/2017/08/07/18/08/phoenix-2608684_1280.jpg"
    elif rsi < 50:
        animal = "Bear"
        reason = f"RSI {rsi:.1f} – oversold"
        img = "https://cdn.pixabay.com/photo/2016/12/04/21/58/bear-1882515_1280.jpg"
    else:
        animal = "Turtle"
        reason = f"${price:.2f} – steady"
        img = "https://cdn.pixabay.com/photo/2016/07/11/15/43/turtle-1510103_1280.jpg"

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
            st.image(img or "https://via.placeholder.com/300?text=No+Image", use_column_width=True)
        with col2:
            st.markdown(f"### {animal} {user_input.upper()}")
            st.write(reason)
























