import streamlit as st
import pandas as pd
import requests
import time
import random

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION & WERTE ---
GID = "2025591169"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzqvISwbnj74Ab7_NO5X3AeeHyvDeWFNFREiWd420_QBdlKyMWaNI6ZL9I0wyoLjEI/exec" 
ADMIN_PASSWORT = "gang2026" 

# Belohnungstabelle (Munition)
DECK_WERTE = {
    1: 500, 2: 550, 3: 750, 4: 1000, 5: 1600, 
    6: 2500, 7: 3000, 8: 4000, 9: 4500, 10: 6000, 
    11: 6500, 12: 10000, 13: 1500, 14: 4000, 15: 6100
}

def safe_int(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan": return 0
        return int(float(str(val).replace(',', '.')))
    except: return 0

def load_data():
    cb = random.randint(1, 1000000)
    url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&cb={cb}"
    try:
        df = pd.read_csv(url, dtype={0: str})
        return df[df.iloc[:, 0].notna()]
    except: return None

df = load_data()

if df is not None:
    st.title("💀 THE GANG HQ")

    # --- SPIELER-BEREICH ---
    namen = df.iloc[:, 0].unique().tolist()
    n_sel = st.selectbox("Wer bist du?", ["Wählen..."] + namen)
    
    if n_sel != "Wählen...":
        st.markdown(f"### 📋 Deine Deck-Übersicht ({n_sel})")
        st.info("🎤 Sprich oder tippe die **9 Zahlen** für dein Deck hintereinander weg.")
        
        sz = df[df.iloc[:, 0] == n_sel]
        
        # Alle 15 Decks untereinander
        for d in range(1, 16):
            sc = 1 + ((d - 1) * 9)
            current_vals = [safe_int(sz.iloc[0, sc + i]) for i in range(9)]
            besitz = sum(1 for v in current_vals if v > 0)
            fehlen = 9 - besitz
            current_str = "".join([str(v) for v in current_vals])
            
            # Layout Zeile
            c1, c2, c3 = st.columns([2, 3, 2])
            
            with c1:
                st.markdown(f"**DECK {d}**")
                st.caption(f"Status: {besitz}/9 (noch {fehlen} fehlen) | {DECK_WERTE.get(d)} Kugeln")
            
            with c2:
                user_input = st.text_input(
                    f"Zahlen Deck {d}", 
                    value=current_str, 
                    key=f"input_d{d}_{n_sel}", 
                    label_visibility="collapsed"
                )
            
            with c3:
                if st.button(f"💾 Speichern", key=f"save_d{d}_{n_sel}"):
                    clean_input = "".join([c for c in user_input if c.isdigit()])
                    clean_input = clean_input.ljust(9, '0')[:9]
                    w_str = ",".join(list(clean_input))
                    
                    with st.spinner("Wird übertragen..."):
                        try:
                            requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d, "werte": w_str}, timeout=5)
                            st.balloons() # <--- Da sind sie wieder! 🎈
                            st.success(f"Deck {d} aktualisiert!")
                            time.sleep(1) # Etwas mehr Zeit für die Ballons
                            st.rerun()
                        except:
                            st.warning("Verbindung hakt – kurz warten.")
                            time.sleep(1)
                            st.rerun()

    # --- ADMIN BEREICH ---
    st.markdown("---")
    pwd =
