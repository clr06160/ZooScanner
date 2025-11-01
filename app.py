import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta

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

    # 3. RSI (FMP historical)
    hist_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={api_key}&limit=30"
    hist = requests.get(hist_url).json()
    rsi = 50
    if 'historical' in hist and len(hist['historical']) >= 14:
        df = pd.DataFrame(hist['historical'])
        df['close'] = df['close'].astype(float)
        df['rsi'] = ta.rsi(df['close'], length=14)
        rsi_val = df['rsi'].iloc[0]
        if pd.notna(rsi_val):
            rsi = rsi_val

    # 4. Animal + Image URL
    if rsi > 70 and vol_spike:
        animal = "Lion"
        reason = f"RSI {rsi:.1f} + volume spike!"
        img = "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=150"
    elif revenue_growth > 25:
        animal = "Phoenix"
        reason = f"+{revenue_growth:.1f}% sales growth!"
        img = "https://images.unsplash.com/photo-1605720750655-5c16b9d8e3a4?w=150"
    elif rsi < 35:
        animal = "Bear"
        reason = f"RSI {rsi:.1f} – oversold"
        img = "https://images.unsplash.com/photo-1570545887596-2a8c3cbcf116?w=150"
    else:
        animal = "Turtle"
        reason = f"${price:.2f} – calm"
        img = "https://images.unsplash.com/photo-1548767793-6c4e8b1b21e3?w=150"

    return animal, reason, img

# === STREAMLIT APP ===
st.set_page_config(page_title="ZooScanner", layout="centered")
st.title("ZooScanner")
st.write("**Type any stock → get your animal instantly**")

# Input
user_input = st.text_input("Enter stock ticker (e.g. NVDA, AAPL)", "")

if user_input:
    animal, reason, img = get_zoo_animal(user_input)
    if animal and animal != "Ghost":
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(img, use_column_width=True)
        with col2:
            emoji = ""
            if animal == "Lion": emoji = "Lion"
            elif animal == "Phoenix": emoji = "Phoenix"
            elif animal == "Bear": emoji = "Bear"
            elif animal == "Turtle": emoji = "Turtle"
            st.markdown(f"### **{emoji} {user_input.upper()}**")
            st.write(reason)
    else:
        st.error("Stock not found. Try NVDA, AAPL, TSLA.")



