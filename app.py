import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import io
import sys
from contextlib import contextmanager

@contextmanager
def suppress_stdout():
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout

# === GET FMP KEY FROM SECRETS ===
api_key = st.secrets["FMP_API_KEY"]

def get_zoo_animal(ticker):
    ticker = ticker.upper().strip()
    if not ticker:
        return None, None, None

    # 1. Quote (price + volume)
    quote_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
    quote = requests.get(quote_url).json()
    if not quote or len(quote) == 0:
        return "Ghost", "No data", None
    q = quote[0]
    price = q.get('price', 0)
    volume = q.get('volume', 0)
    avg_vol = q.get('avgVolume', volume)
    vol_spike = volume > avg_vol * 1.5

    # 2. Profile (revenue growth)
    profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}"
    profile = requests.get(profile_url).json()
    revenue_growth = 0
    if profile and len(profile) > 0 and 'revenueGrowth' in profile[0]:
        revenue_growth = profile[0]['revenueGrowth'] * 100

    # 3. RSI (FMP historical) — Suppress output
    hist_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={api_key}&limit=30"
    hist = requests.get(hist_url).json()
    rsi = 50
    if 'historical' in hist and len(hist['historical']) >= 14:
        df = pd.DataFrame(hist['historical'])
        df['close'] = df['close'].astype(float)
        with suppress_stdout():
            df['rsi'] = ta.rsi(df['close'], length=14)
        rsi_val = df['rsi'].iloc[0]
        if pd.notna(rsi_val):
            rsi = rsi_val

    # 4. Animal + Photo (SUPER LOOSE RULES FOR VARIETY)
    if rsi > 55:  # Looser for Lion
        animal = "🦁 Lion"
        reason = f"RSI {rsi:.1f} – momentum rising!"
        img = "https://cdn.pixabay.com/photo/2015/09/15/14/09/lion-940142_1280.jpg"  # Lion photo
    elif revenue_growth > 10:  # Looser for Phoenix
        animal = "🔥 Phoenix"
        reason = f"+{revenue_growth:.1f}% sales growth!"
        img = "https://cdn.pixabay.com/photo/2017/08/07/18/08/phoenix-2608684_1280.jpg"  # Phoenix photo
    elif rsi < 50:  # Looser for Bear
        animal = "🐻 Bear"
        reason = f"RSI {rsi:.1f} – getting cheap"
        img = "https://cdn.pixabay.com/photo/2017/01/12/22/50/bear-1974795_1280.jpg"  # Bear photo
    else:
        animal = "🐢 Turtle"
        reason = f"${price:.2f} – steady"
        img = "https://cdn.pixabay.com/photo/2017/02/20/18/03/cat-2083492_1280.jpg"  # Turtle photo (using cat as placeholder; swap if needed)

    return animal, reason, img

# === STREAMLIT APP ===
st.set_page_config(page_title="ZooScanner", layout="centered")
st.title("🦁 ZooScanner")
st.write("**Type any stock → get your animal instantly**")

# Input
user_input = st.text_input("Enter stock ticker (e.g. NVDA, AAPL)", "")

if user_input:
    animal, reason, img = get_zoo_animal(user_input)
    if animal and "Ghost" not in animal:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(img, use_column_width=True)
        with col2:
            st.markdown(f"### {animal} {user_input.upper()}")
            st.write(reason)
    else:
        st.error("Stock not found. Try NVDA, AAPL, TSLA.")








