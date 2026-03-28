import streamlit as st
import pandas as pd
import requests
import time
import re

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION ---
GID = "2025591169"
# Deine URL bleibt gleich
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzqvISwbnj74Ab7_NO5X3AeeHyvDeWFNFREiWd420_QBdlKyMWaNI6ZL9I0wyoLjEI/exec" 
ADMIN_PASSWORT = "gang2026" 

def safe_int(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan": return 0
        return int(float(str(val).replace(',', '.')))
    except: return 0

# Initialisiere Speicher, falls nicht vorhanden
if "v_vals" not in st.session_state: st.session_state.v_vals = {}
if "confirm_msg" not in st.session_state: st.session_state.confirm_msg = None

# --- 3. DATEN LADEN ---
@st.cache_data(ttl=60) # Cache für 60 Sekunden, damit die App nicht bei jedem Klick neu lädt
def load_data(ts):
    try:
        url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&t={ts}"
        df = pd.read_csv(url, dtype={0: str})
        return df[df.iloc[:, 0].notna()]
    except: return None

# Wir nutzen die aktuelle Zeit als "Ticket", um den Cache bei Bedarf zu umgehen
df = load_data(int(time.time() / 60))

if df is not None:
    namen = df.iloc[:, 0].unique().tolist()
    st.title("💀 THE GANG HQ")
    
    c1, c2 = st.columns(2)
    n_sel = c1.selectbox("Wer bist du?", ["Wählen..."] + namen)
    d_sel = c2.selectbox("Welches Deck?", list(range(1, 16)))
    
    if n_sel != "Wählen...":
        sz = df[df.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        db_vals = [safe_int(sz.iloc[0, start_c + i]) for i in range(9)]

        # --- SCHNELL-EINGABE ---
        st.markdown("### 🎙️ SCHNELL-EINGABE")
        # Kein on_change mehr, das verursacht oft Loops
        v_in = st.text_input("Zahlenkette (z.B. 120011211) & ENTER:")
        
        if v_in:
            digs = re.findall(r'\d', v_in)
            if len(digs) >= 9:
                for i in range(9): 
                    st.session_state.v_vals[i] = int(digs[i])
                st.session_state.confirm_msg = f"✅ Kette erkannt: {' | '.join(digs[:9])}"
            else:
                st.warning(f"⚠️ Nur {len(digs)} Zahlen gefunden. Brauche 9.")

        if st.session_state.confirm_msg:
            st.success(st.session_state.confirm_msg)
        
        # --- KARTEN-GRID ---
        neue_werte = []
        cols = st.columns(3) + st.columns(3) + st.columns(3)
        for i in range(9):
            with cols[i]:
                # Wir nehmen den Wert aus der Kette, wenn vorhanden, sonst aus dem Sheet
                val_start = st.session_state.v_vals.get(i, db_vals[i])
                v = st.number_input(f"K{i+1}", 0, 9, value=val_start, key=f"kinput_{i}")
                neue_werte.append(v)
        
        if st.button("🚀 ÄNDERUNGEN SPEICHERN", use_container_width=True):
            w_str = ",".join([str(int(x)) for x in neue_werte])
            with st.spinner("Übertrage..."):
                try:
                    r = requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": w_str}, timeout=15)
                    if "Erfolg" in r.text:
                        st.balloons()
                        st.success("🔥 DATEN ERFOLGREICH ÜBERMITTELT!")
                        # Kurz warten und Cache löschen
                        time.sleep(1)
                        st.cache_data.clear()
                        st.session_state.v_vals = {}
                        st.session_state.confirm_msg = None
                        st.rerun()
                    else:
                        st.error(f"Google meldet: {r.text}")
                except Exception as e:
                    st.error(f"Verbindungs-Fehler: {e}")

    # --- ADMIN (Ganz unten und einfach gehalten) ---
    st.markdown("---")
    pwd = st.text_input("Admin-Passwort", type="password")
    if pwd == ADMIN_PASSWORT:
        st.write("Analyse geladen (hier könntest du wieder die Tauschtabelle einfügen)")
