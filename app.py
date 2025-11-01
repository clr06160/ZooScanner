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
        return "Error", "Empty ticker", "https://via.placeholder.com/200?text=No+Stock"

    try:
        # 1. Quote
        quote = requests.get(f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}", timeout=10).json()
        if not quote or len(quote) == 0:
            return "Ghost", "Not found", "https://via.placeholder.com/200?text=Not+Found"
        q = quote[0]
        price = q.get('price', 0)
        volume = q.get('volume', 0)
        avg_vol = q.get('avgVolume', volume)
        vol_spike = volume > avg_vol * 1.5

        # 2. Revenue Growth
        profile = requests.get(f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}", timeout=10).json()
        revenue_growth = 0
        if profile and len(profile) > 0 and 'revenueGrowth' in profile[0]:
            revenue_growth = profile[0]['revenueGrowth'] * 100

        # 3. RSI — LATEST + NaN fix
        hist = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={api_key}&limit=30", timeout=10).json()
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

        # 4. Animal + RELIABLE IMAGE
        if rsi > 60:
            animal = "Lion"
            reason = f"RSI {rsi:.1f} – momentum!"
            img = "https://images.unsplash.com/photo-1546182990-dffeafbe841d?auto=format&fit=crop&w=300"
        elif revenue_growth > 5:
            animal = "Phoenix"
            reason = f"+{revenue_growth:.1f}% growth!"
            img = "https://images.unsplash.com/photo-1605720750655-5c16b9d8e3a4?auto=format&fit=crop&w=300"
        elif rsi < 50:
            animal = "Bear"
            reason = f"RSI {rsi:.1f} – oversold"
            img = "https://images.unsplash.com/photo-1530595467537-0b0d7a9c3c3c?auto=format&fit=crop&w=300"
        else:
            animal = "Turtle"
            reason = f"${price:.2f} – steady"
            img = "https://images.unsplash.com/photo-1560114928-1564499c8b9e?auto=format&fit=crop&w=300"

        return animal, reason, img

    except Exception as e:
        return "Error", "Data issue", "https://via.placeholder.com/200?text=Error"

# === APP ===
st.set_page_config(page_title="ZooScanner", layout="centered")
st.title("ZooScanner")
st.write("**Type a stock → get your animal**")

user_input = st.text_input("Ticker (NVDA, AAPL, TSLA, IREN)", "")

if user_input:
    animal, reason, img = get_zoo_animal(user_input)
    if animal not in ["Ghost", "Error"]:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(img, use_column_width=True)
        with col2:
            st.markdown(f"### {animal} {user_input.upper()}")
            st.write(reason)
    else:
        st.error(f"{animal}: {reason}")
















