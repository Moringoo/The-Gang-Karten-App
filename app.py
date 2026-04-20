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
    cb = int(time.time()) 
    url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&cachebust={cb}"
    try:
        df = pd.read_csv(url, dtype=str)
        df = df[df.iloc[:, 0].notna()]
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return None

df = load_data()

if df is not None:
    st.title("💀 THE GANG HQ")

    namen = [str(n).strip() for n in df.iloc[:, 0].unique() if str(n).strip() != ""]
    n_sel = st.selectbox("Wer bist du?", ["Wählen..."] + namen)
    
    if n_sel != "Wählen...":
        sz = df[df.iloc[:, 0].str.strip() == n_sel].copy()
        
        if sz.empty:
            st.warning("Spieler nicht gefunden.")
        else:
            st.markdown(f"### 📋 Deine Deck-Übersicht ({n_sel})")
            
            if st.button("🔄 DATEN FRISCH LADEN"):
                st.rerun()

            st.info("🎤 Gib die 9 Zahlen ein. Die Anzeige unter dem Feld hilft dir beim Zählen!")
            
            alle_inputs = {}

            def save_all():
                erfolg = 0
                prozent_balken = st.progress(0)
                decks_to_save = list(alle_inputs.items())
                
                for i, (d_nr, werte_str) in enumerate(decks_to_save):
                    clean = "".join([c for c in werte_str if c.isdigit()]).ljust(9, '0')[:9]
                    w_send = ",".join(list(clean))
                    
                    sc_idx = 1 + ((d_nr - 1) * 9)
                    old_str = "".join([str(safe_int(sz.iloc[0, sc_idx + k])) for k in range(9)])
                    
                    if clean != old_str:
                        try:
                            requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_nr, "werte": w_send}, timeout=10)
                            erfolg += 1
                        except:
                            pass
                    
                    prozent_balken.progress((i + 1) / len(decks_to_save))

                st.balloons()
                st.success(f"Erfolgreich {erfolg} Decks aktualisiert!")
                time.sleep(2)
                st.rerun()

            if st.button("🚀 ALLE ÄNDERUNGEN SPEICHERN", use_container_width=True, key="save_top"):
                save_all()

            st.markdown("---")
            
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                if sc + 8 < len(sz.columns):
                    current_vals = [safe_int(sz.iloc[0, sc + i]) for i in range(9)]
                    besitz = sum(1 for v in current_vals if v > 0)
                    fehlen = 9 - besitz
                    current_str = "".join([str(v) for v in current_vals])
                    kugeln = DECK_WERTE.get(d, 0)
                    
                    c1, c2 = st.columns([3, 4])
                    with c1:
                        st.markdown(f"**DECK {d}**")
                        st.caption(f"Status: {besitz}/9 (noch {fehlen} fehlen) | 💰 {kugeln} Kugeln")
                    with c2:
