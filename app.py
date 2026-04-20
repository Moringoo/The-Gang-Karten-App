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

    # --- SPIELER-BEREICH (Listen-Layout für schnelle Eingabe & Sprache) ---
    namen = df.iloc[:, 0].unique().tolist()
    n_sel = st.selectbox("Wer bist du?", ["Wählen..."] + namen)
    
    if n_sel != "Wählen...":
        st.markdown(f"### 📋 Deine Decks ({n_sel})")
        st.info("Klicke in das Feld und nutze das Mikrofon oder tippe die 9 Zahlen (z.B. 002100001).")
        
        sz = df[df.iloc[:, 0] == n_sel]
        
        for d in range(1, 16):
            sc = 1 + ((d - 1) * 9)
            current_vals = [safe_int(sz.iloc[0, sc + i]) for i in range(9)]
            besitz = sum(1 for v in current_vals if v > 0)
            current_str = "".join([str(v) for v in current_vals])
            
            c1, c2, c3 = st.columns([2, 3, 2])
            with c1:
                st.markdown(f"**Deck {d}** ({besitz}/9)")
                st.caption(f"{DECK_WERTE.get(d)} Kugeln")
            with c2:
                user_input = st.text_input(
                    f"Eingabe D{d}", value=current_str, key=f"in_{n_sel}_{d}", 
                    label_visibility="collapsed", max_chars=12 # Puffer für Leerzeichen bei Sprache
                )
            with c3:
                if st.button(f"💾 Speichern D{d}", key=f"btn_{n_sel}_{d}"):
                    # Filtert alles außer Zahlen (entfernt Leerzeichen der Spracheingabe)
                    clean_input = "".join([c for c in user_input if c.isdigit()])
                    clean_input = clean_input.ljust(9, '0')[:9]
                    w_str = ",".join(list(clean_input))
                    
                    with st.spinner("Wird im Sheet eingetragen..."):
                        try:
                            # Wir senden den Befehl mit Timeout-Puffer
                            requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d, "werte": w_str}, timeout=5)
                            st.success(f"Deck {d} gespeichert!")
                            time.sleep(0.5)
                            st.rerun()
                        except:
                            # Falls das Script langsam ist, prüfen wir nur ob es im Sheet ankommt
                            st.warning("Verbindung langsam – bitte im Sheet prüfen, ob es da ist.")
                            time.sleep(2)
                            st.rerun()

    # --- ADMIN BEREICH (Optimierte Tauschanalyse) ---
    st.markdown("---")
    pwd = st.text_input("Admin-Passwort für Tauschanalyse", type="password")
    if pwd == ADMIN_PASSWORT:
        st.markdown("### 🎯 PROFIT-OPTIMIERTE TAUSCHVORSCHLÄGE")
        
        gbt, bdr = [], []
        for _, row in df.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                cols_deck = df.columns[sc:sc+9]
                dia_dichte = sum(1 for c in cols_deck if "(D)" in str(c))
                besitz = sum(1 for i in range(9) if safe_int(row.
