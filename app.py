import streamlit as st
import pandas as pd
import requests
import time
import re

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION ---
GID = "2025591169"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaIWcjmJ5Nn5MsRR66ptz97MBjJ-S0O-B7TVp1Y4pq81Xc1Q0VLNzDFWDn6c9NcB4/exec" 
ADMIN_PASSWORT = "gang2026" 

def safe_int(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan": return 0
        return int(float(str(val).replace(',', '.')))
    except: return 0

# --- 3. SESSION STATE ---
if "form_iter" not in st.session_state:
    st.session_state.form_iter = 0

def trigger_reset():
    st.session_state.form_iter += 1
    for i in range(9):
        if f"voice_val_{i}" in st.session_state:
            del st.session_state[f"voice_val_{i}"]

# --- 4. DATEN LADEN ---
def load_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&t={int(time.time())}"
        df = pd.read_csv(url, dtype={0: str})
        df = df[df.iloc[:, 0].notna() & (df.iloc[:, 0].str.strip() != "")]
        df = df[~df.iloc[:, 0].str.strip().str.lower().isin(['leer', 'platzhalter'])]
        return df
    except Exception as e:
        st.error(f"Download-Fehler: {e}")
        return None

# --- 5. DESIGN ---
st.markdown("<style>.stApp { background-color: #0e1117; color: white; } .voice-area { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 2px solid #3b82f6; }</style>", unsafe_allow_html=True)

# --- 6. LOGIK ---
df = load_data()

if df is not None:
    namen = df.iloc[:, 0].unique().tolist()
    st.title("💀 THE GANG HQ")

    col1, col2 = st.columns(2)
    n_sel = col1.selectbox("Wer bist du?", ["Wählen..."] + namen, on_change=trigger_reset)
    d_sel = col2.selectbox("Welches Deck?", list(range(1, 16)), on_change=trigger_reset)
    
    if n_sel != "Wählen...":
        sz = df[df.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        db_vals = [safe_int(sz.iloc[0, start_c + i]) for i in range(9)]

        st.markdown('<div class="voice-area">', unsafe_allow_html=True)
        v_in = st.text_input("Zahlenkette (9 Ziffern):", key=f"v_{st.session_state.form_iter}")
        if v_in:
            digs = re.findall(r'\d', v_in)
            if len(digs) >= 9:
                for i in range(9): st.session_state[f"voice_val_{i}"] = int(digs[i])
                st.session_state.form_iter += 1
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        neue_werte = []
        cols = st.columns(3) + st.columns(3) + st.columns(3)
        for i in range(9):
            with cols[i]:
                cur = st.session_state.get(f"voice_val_{i}", db_vals[i])
                v = st.number_input(f"K{i+1}", 0, 9, value=cur, key=f"k_{i}_{st.session_state.form_iter}")
                neue_werte.append(v)
        
        if st.button("🚀 SPEICHERN", use_container_width=True):
            w_str = ",".join([str(int(x)) for x in neue_werte])
            with st.spinner("Sende..."):
                try:
                    r = requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": w_str}, timeout=10)
                    if r.status_code == 200:
                        st.success("Gespeichert!")
                        trigger_reset()
                        time.sleep(1)
                        st.rerun()
                    else: st.error(f"Fehler: {r.status_code}")
                except Exception as e: st.error(f"Verbindung weg: {e}")

    st.markdown("---")
    if st.text_input("Admin", type="password") == ADMIN_PASSWORT:
        st.markdown("### 🕵️ Tausch-Check")
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
