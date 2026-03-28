import streamlit as st
import pandas as pd
import requests
import time

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION ---
GID = "2025591169"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzqvISwbnj74Ab7_NO5X3AeeHyvDeWFNFREiWd420_QBdlKyMWaNI6ZL9I0wyoLjEI/exec" 
ADMIN_PASSWORT = "gang2026" 

def safe_int(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan": return 0
        return int(float(str(val).replace(',', '.')))
    except: return 0

# --- 3. DATEN LADEN ---
@st.cache_data(ttl=10) 
def load_data(ts):
    try:
        url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&t={ts}"
        df = pd.read_csv(url, dtype={0: str})
        return df[df.iloc[:, 0].notna()]
    except: return None

df = load_data(int(time.time() / 10))

if df is not None:
    namen = df.iloc[:, 0].unique().tolist()
    st.title("💀 THE GANG HQ")
    
    col1, col2 = st.columns(2)
    with col1:
        n_sel = st.selectbox("Wer bist du?", ["Wählen..."] + namen)
    with col2:
        d_sel = st.selectbox("Welches Deck?", list(range(1, 16)))
    
    if n_sel != "Wählen...":
        sz = df[df.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        db_vals = [safe_int(sz.iloc[0, start_c + i]) for i in range(9)]

        st.markdown(f"### 🃏 Deck {d_sel} bearbeiten")
        
        # Das 3x3 Raster
        neue_werte = []
        for row_idx in range(3):
            cols = st.columns(3)
            for col_idx in range(3):
                i = row_idx * 3 + col_idx
                with cols[col_idx]:
                    v = st.number_input(f"Karte {i+1}", 0, 9, value=db_vals[i], key=f"k{i}_{n_sel}_{d_sel}")
                    neue_werte.append(v)
        
        if st.button("🚀 ÄNDERUNGEN SPEICHERN", use_container_width=True):
            w_str = ",".join([str(int(x)) for x in neue_werte])
            with st.spinner("Speichere im Google Sheet..."):
                try:
                    r = requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": w_str}, timeout=15)
                    if "Erfolg" in r.text:
                        st.balloons()
                        st.success("✅ Erledigt!")
                        time.sleep(1
