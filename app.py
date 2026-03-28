import streamlit as st
import pandas as pd
import requests
import time
import re

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION ---
GID = "2025591169"
# DEINE NEUE URL IST HIER BEREITS EINGEBAUT:
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzqvISwbnj74Ab7_NO5X3AeeHyvDeWFNFREiWd420_QBdlKyMWaNI6ZL9I0wyoLjEI/exec" 
ADMIN_PASSWORT = "gang2026" 

def safe_int(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan": return 0
        return int(float(str(val).replace(',', '.')))
    except: return 0

# Session State für stabilere Eingabe
if "form_iter" not in st.session_state: st.session_state.form_iter = 0
if "v_vals" not in st.session_state: st.session_state.v_vals = {}
if "confirm_msg" not in st.session_state: st.session_state.confirm_msg = None

def trigger_reset():
    st.session_state.form_iter += 1
    st.session_state.v_vals = {}
    st.session_state.confirm_msg = None

# --- 3. DATEN LADEN ---
def load_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&t={int(time.time())}"
        df = pd.read_csv(url, dtype={0: str})
        return df[df.iloc[:, 0].notna()]
    except: return None

# --- 4. HAUPT-LOGIK ---
df = load_data()

if df is not None:
    namen = df.iloc[:, 0].unique().tolist()
    st.title("💀 THE GANG HQ")
    
    c1, c2 = st.columns(2)
    n_sel = c1.selectbox("Wer bist du?", ["Wählen..."] + namen, on_change=trigger_reset)
    d_sel = c2.selectbox("Welches Deck?", list(range(1, 16)), on_change=trigger_reset)
    
    if n_sel != "Wählen...":
        sz = df[df.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        db_vals = [safe_int(sz.iloc[0, start_c + i]) for i in range(9)]

        # --- SCHNELL-EINGABE (SPRACHE/KETTE) ---
        st.markdown("### 🎙️ SCHNELL-EINGABE")
        v_in = st.text_input("Zahlenkette (z.B. 120011211) & ENTER:", key=f"v_{st.session_state.form_iter}")
        
        if v_in:
            digs = re.findall(r'\d', v_in)
            if len(digs) >= 9:
                for i in range(9): st.session_state.v_vals[i] = int(digs[i])
                st.session_state.confirm_msg = f"✅ Kette erkannt: {' | '.join(digs[:9])}"
                st.rerun()

        if st.session_state.confirm_msg:
            st.success(st.session_state.confirm_msg)
        
        # --- KARTEN-GRID (MANUELL) ---
        neue_werte = []
        cols = st.columns(3) + st.columns(3) + st.columns(3)
        for i in range(9):
            with cols[i]:
                # Wert aus Kette nehmen, sonst aus der Datenbank (Sheet)
                cur = st.session_state.v_vals.get(i, db_vals[i])
                v = st.number_input(f"K{i+1}", 0, 9, value=cur, key=f"k_{i}_{st.session_state.form_iter}")
                neue_werte.append(v)
        
        if st.button("🚀 ÄNDERUNGEN SPEICHERN", use_container_width=True):
            w_str = ",".join([str(int(x)) for x in neue_werte])
            with st.spinner("Übertrage an Google Sheet..."):
                try:
                    r = requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": w_str}, timeout=20)
                    if "Erfolg" in r.text:
                        st.balloons()
                        st.success("🔥 DATEN ERFOLGREICH ÜBERMITTELT!")
                        time.sleep(2)
                        trigger_reset()
                        st.rerun()
                    else:
                        st.error(f"Google meldet: {r.text}")
                except Exception as e:
                    st.error(f"Verbindungs-Fehler: {e}")

    # --- TAUSCH-CHECK (ADMIN) ---
    st.markdown("---")
    if st.text_input("Admin-Passwort", type="password") == ADMIN_PASSWORT:
        st.markdown("### 🕵️‍♂️ TAUSCH-CHECK")
        gbt, bdr = [], []
        for _, row in df.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                bz = sum(1 for i in range(9) if safe_int(row.iloc[sc+i]) > 0)
                for i in range(9):
                    cn, val = df.columns[sc+i], safe_int(row.iloc[sc+i])
                    if val >= 2: gbt.append({"s": sp, "k": cn})
                    elif val == 0: bdr.append({"s": sp, "k": cn, "f": bz})
        
        bdr = sorted(bdr, key=lambda x: x['f'], reverse=True)
        t1, t2 = st.tabs(["🌕 Gold", "💎 Diamant"])
        for tab, is_d in zip([t1, t2], [False, True]):
            with tab:
                weg = set()
                for b in bdr:
                    if (("(D)" in b["k"]) == is_d):
                        for g in gbt:
                            if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                                st.write(f"({b['f']}/9) {g['s']} ➔ {b['s']} ({g['k']})")
                                weg.add(g["s"])
                                break
