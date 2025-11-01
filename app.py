import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import warnings
warnings.filterwarnings("ignore")

# === FMP KEY ===
api_key = st.secrets["FMP_API_KEY"]

def get_zoo_animal(ticker):
    ticker = ticker.upper().strip()
    if not ticker:
        return None, None, None

    # 1. Quote
    quote = requests.get(f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}").json()
    if not quote:
        return "Ghost", "No data", None
    q = quote[0]
    price = q.get('price', 0)
    volume = q.get('volume', 0)
    avg_vol = q.get('avgVolume', volume)
    vol_spike = volume > avg_vol * 1.5

    # 2. Revenue Growth
    profile = requests.get(f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}").json()
    revenue_growth = profile[0].get('revenueGrowth', 0) * 100 if profile else 0

    # 3. RSI — LATEST
    hist = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={api_key}&limit=30").json()
    rsi = 50
    if 'historical' in hist and len(hist['historical']) >= 14:
        df = pd.DataFrame(hist['historical'])
        df['close'] = df['close'].astype(float)
        df['rsi'] = ta.rsi(df['close'], length=14)
        rsi = df['rsi'].iloc[-1]
        if pd.isna(rsi):
            rsi = 50

    # 4. Animal + Image (FORCED VARIETY)
    if rsi > 60:
        animal = "Lion"
        reason = f"RSI {rsi:.1f} – momentum!"
        img = "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=200"
    elif revenue_growth > 5:
        animal = "Phoenix"
        reason = f"+{revenue_growth:.1f}% growth!"
        img = "https://images.unsplash.com/photo-1605720750655-5c16b9d8e3a4?w=200"
    elif rsi < 50:
        animal = "Bear"
        reason = f"RSI {rsi:.1f} – oversold"
        img = "https://images.unsplash.com/photo-1570545887596-2a8c3cbcf116?w=200"
    else:
        animal = "Turtle"
        reason = f"${price:.2f} – steady"
        img = "https://images.unsplash.com/photo-1560114928-1564499c8b9e?w=200"

    return animal, reason, img

# === APP ===
st.set_page_config(page_title="ZooScanner")
st.title("ZooScanner")
st.write("**Type a stock → get your animal**")

user_input = st.text_input("Ticker (NVDA, AAPL, TSLA)", "")

if user_input:
    animal, reason, img = get_zoo_animal(user_input)
    if animal != "Ghost":
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(img, use_column_width=True)
        with col2:
            st.markdown(f"### {animal} {user_input.upper()}")
            st.write(reason)
    else:
        st.error("Not found.")












