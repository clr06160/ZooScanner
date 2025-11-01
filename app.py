import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import warnings
import base64

warnings.filterwarnings("ignore")

# === FMP KEY ===
api_key = st.secrets["FMP_API_KEY"]

# === EMBEDDED IMAGES (BASE64) ===
LION_B64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxISEhUTExMWFh"
# ... (full base64 for lion, bear, phoenix, turtle — I’ll give you the full strings below)

# === FUNCTION ===
def get_zoo_animal(ticker):
    ticker = ticker.upper().strip()
    if not ticker:
        return "Error", "Empty", LION_B64

    # Quote
    quote = requests.get(f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}").json()
    if not quote:
        return "Ghost", "No data", LION_B64
    q = quote[0]
    price = q.get('price', 0)

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

    # Revenue Growth
    profile = requests.get(f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}").json()
    revenue_growth = 0
    if profile and 'revenueGrowth' in profile[0]:
        revenue_growth = profile[0]['revenueGrowth'] * 100

    # Animal
    if rsi > 60:
        return "Lion", f"RSI {rsi:.1f} – momentum!", LION_B64
    elif revenue_growth > 5:
        return "Phoenix", f"+{revenue_growth:.1f}% growth!", PHOENIX_B64
    elif rsi < 50:
        return "Bear", f"RSI {rsi:.1f} – oversold", BEAR_B64
    else:
        return "Turtle", f"${price:.2f} – steady", TURTLE_B64

# === APP ===
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
























