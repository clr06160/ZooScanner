import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta

# === YOUR FMP KEY ===
api_key = st.secrets["FMP_API_KEY"] # ← Paste your working key

def get_zoo_animal(ticker):
    ticker = ticker.upper().strip()
    if not ticker:
        return None, None, None

    # Quote
    quote_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
    quote = requests.get(quote_url).json()
    if not quote or len(quote) == 0:
        return "Ghost", "No data", "https://via.placeholder.com/80?text=?"

    q = quote[0]
    price = q['price']
    volume = q['volume']
    avg_vol = q.get('avgVolume', volume)
    vol_spike = volume > avg_vol * 1.5

    # Profile
    profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}"
    profile = requests.get(profile_url).json()
    revenue_growth = profile[0].get('revenueGrowth', 0) * 100 if profile else 0

    # RSI
    hist_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={api_key}&limit=30"
    hist = requests.get(hist_url).json()
    rsi = 50
    if 'historical' in hist and len(hist['historical']) >= 14:
        df = pd.DataFrame(hist['historical'])
        df['close'] = df['close'].astype(float)
        df['rsi'] = ta.rsi(df['close'], length=14)
        rsi = df['rsi'].iloc[0]
        if pd.isna(rsi):
            rsi = 50

    # Animal + Image
        # Animal + Emoji (no external images)
    if rsi > 70 and vol_spike:
        animal = "Lion"
        reason = f"RSI {rsi:.1f} + volume spike!"
        img = None  # No image, use emoji
    elif revenue_growth > 25:
        animal = "Phoenix"
        reason = f"+{revenue_growth:.1f}% sales growth!"
        img = None
    elif rsi < 35:
        animal = "Bear"
        reason = f"RSI {rsi:.1f} – oversold"
        img = None
    else:
        animal = "Turtle"
        reason = f"${price:.2f} – calm"
        img = None

# === STREAMLIT APP ===
st.set_page_config(page_title="ZooScanner", layout="centered")
st.title("ZooScanner")
st.write("**Type any stock → get your animal instantly**")

# Input
user_input = st.text_input("Enter stock ticker (e.g. NVDA, AAPL)", "")
if user_input:
    animal, reason, img = get_zoo_animal(user_input)
    if animal:
        col1, col2 = st.columns([1, 3])
                col1, col2 = st.columns([1, 4])
        with col1:
            if animal == "Lion":
                st.write("")
            elif animal == "Phoenix":
                st.write("")
            elif animal == "Bear":
                st.write("")
            else:  # Turtle
                st.write("")
        with col2:
            st.markdown(f"### **{animal} {user_input.upper()}**")
            st.write(reason)
    else:

        st.error("Stock not found. Try again.")

