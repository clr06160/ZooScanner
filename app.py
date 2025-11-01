import streamlit as st
import requests
import pandas as pd
import pandas_ta as ta
import warnings

warnings.filterwarnings("ignore")

# -------------------------------------------------
# 1. FMP KEY (must be in Streamlit Secrets)
# -------------------------------------------------
api_key = st.secrets["FMP_API_KEY"]

# -------------------------------------------------
# 2. ONE FUNCTION – returns animal, reason, image URL
# -------------------------------------------------
def get_zoo_animal(ticker: str):
    ticker = ticker.upper().strip()
    if not ticker:
        return "Error", "Empty ticker", None

    try:
        # ---- Quote (price / volume) ----
        q_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
        quote = requests.get(q_url, timeout=8).json()
        if not quote:
            return "Ghost", "Not found", None
        q = quote[0]
        price = q.get("price", 0)
        volume = q.get("volume", 0)
        avg_vol = q.get("avgVolume", volume)
        vol_spike = volume > avg_vol * 1.5

        # ---- Revenue growth ----
        p_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}"
        profile = requests.get(p_url, timeout=8).json()
        revenue_growth = 0
        if profile and "revenueGrowth" in profile[0]:
            revenue_growth = profile[0]["revenueGrowth"] * 100

        # ---- RSI (latest close) ----
        h_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={api_key}&limit=30"
        hist = requests.get(h_url, timeout=8).json()
        rsi = 50
        if "historical" in hist and len(hist["historical"]) >= 14:
            df = pd.DataFrame(hist["historical"])
            df["close"] = pd.to_numeric(df["close"], errors="coerce")
            df = df.dropna(subset=["close"])
            if len(df) >= 14:
                df["rsi"] = ta.rsi(df["close"], length=14)
                rsi_val = df["rsi"].iloc[-1]
                if pd.notna(rsi_val):
                    rsi = rsi_val

        # ---- ANIMAL LOGIC (one block per animal) ----
        # LION
        if rsi > 60:
            return (
                "Lion",
                f"RSI {rsi:.1f} – momentum!",
                "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=300"
            )
        # PHOENIX
        if revenue_growth > 5:
            return (
                "Phoenix",
                f"+{revenue_growth:.1f}% sales growth!",
                "https://images.unsplash.com/photo-1605720750655-5c16b9d8e3a4?w=300"
            )
        # BEAR
        if rsi < 50:
            return (
                "Bear",
                f"RSI {rsi:.1f} – oversold",
                "https://cdn.pixabay.com/photo/2016/12/04/21/58/bear-1882515_1280.jpg"
            )
        # TURTLE (default)
        return (
            "Turtle",
            f"${price:.2f} – steady",
            "https://images.unsplash.com/photo-1560114928-1564499c8b9e?w=300"
        )

    except Exception:
        return "Error", "Data problem", None

# -------------------------------------------------
# 3. STREAMLIT UI
# -------------------------------------------------
st.set_page_config(page_title="ZooScanner", layout="centered")
st.title("ZooScanner")
st.write("**Enter a ticker – get an animal instantly**")

user_input = st.text_input("Ticker (NVDA, AAPL, TSLA, IREN)", "")

if user_input:
    animal, reason, img_url = get_zoo_animal(user_input)

    if animal in ("Error", "Ghost"):
        st.error(f"{animal}: {reason}")
    else:
        col_img, col_txt = st.columns([1, 3])
        with col_img:
            # fallback image if URL fails
            st.image(img_url or "https://via.placeholder.com/300?text=No+Image", use_column_width=True)
        with col_txt:
            st.markdown(f"### {animal} {user_input.upper()}")
            st.write(reason)




















