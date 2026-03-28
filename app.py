import streamlit as st
import pandas as pd
import requests
import time
import re

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
@st.cache_data(ttl=30) # Kürzerer Cache für schnellere Updates
def load_data(ts):
    try:
        url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&t={ts}"
        df = pd.read_csv(url, dtype={0: str})
        return df[df.iloc[:, 0].notna()]
    except: return None

df = load_data(int(time.time() / 30))

if df is not None:
    namen = df.iloc[:, 0].unique().tolist()
    st.title("💀 THE GANG HQ")
    
    c1, c2 = st.columns(2)
    n_sel = c1.selectbox("Wer bist du?", ["Wählen..."] + namen, key="main_user_sel")
    d_sel = c2.selectbox("Welches Deck?", list(range(1, 16)), key="main_deck_sel")
    
    if n_sel != "Wählen...":
        sz = df[df.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        # Die aktuellen Werte aus dem Google Sheet
        db_vals = [safe_int(sz.iloc[0, start_c + i]) for i in range(9)]

        st.markdown("### 🎙️ SCHNELL-EINGABE")
        v_in = st.text_input("Zahlenkette (z.B. 120011211) & ENTER:", key="chain_input")
        
        # Logik für die Kette
        kette_zahlen = []
        if v_in:
            digs = re.findall(r'\d', v_in)
            if len(digs) >= 9:
                kette_zahlen = [int(d) for d in digs[:9]]
                st.success(f"✅ Kette erkannt: {' | '.join(digs[:9])}")
            else:
                st.warning(f"⚠️ Erst {len(digs)} von 9 Zahlen...")

        # --- DAS GRID ---
        st.markdown("---")
        neue_werte = []
        cols = st.columns(3) + st.columns(3) + st.columns(3)
        
        for i in range(9):
            with cols[i]:
                # WICHTIG: Wenn eine Kette da ist, nimm die Zahl aus der Kette. 
                # Sonst nimm den Wert aus dem Google Sheet.
                if kette_zahlen:
                    default_val = kette_zahlen[i]
                else:
                    default_val = db_vals[i]
                
                # Jedes Feld bekommt einen absolut eindeutigen Key
                v = st.number_input(f"K{i+1}", 0, 9, value=default_val, key=f"k_field_{n_sel}_{d_sel}_{i}")
                neue_werte.append(v)
        
        if st.button("🚀 ÄNDERUNGEN SPEICHERN", use_container_width=True):
            w_str = ",".join([str(int(x)) for x in neue_werte])
            with st.spinner("Sende an Google..."):
                try:
                    r = requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": w_str}, timeout=15)
                    if "Erfolg" in r.text:
                        st.balloons()
                        st.success("🔥 DATEN ERFOLGREICH ÜBERMITTELT!")
                        time.sleep(1.5)
                        # Cache leeren und Seite komplett neu laden
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"Google Fehler: {r.text}")
                except Exception as e:
                    st.error(f"Verbindungs-Fehler: {e}")

    # --- ADMIN BEREICH ---
    st.markdown("---")
    if st.text_input("Admin-Passwort", type="password", key="admin_pwd") == ADMIN_PASSWORT:
        st.info("Tauschanalyse bereit.")
