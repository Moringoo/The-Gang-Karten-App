import streamlit as st
import pandas as pd
import requests
import time
import re

st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

# KONFIGURATION
GID = "2025591169"
# Hier die URL aus dem Google-Script einfügen!
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaIWcjmJ5Nn5MsRR66ptz97MBjJ-S0O-B7TVp1Y4pq81Xc1Q0VLNzDFWDn6c9NcB4/exec" 
ADMIN_PASSWORT = "gang2026"

def safe_int(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan": return 0
        return int(float(str(val).replace(',', '.')))
    except: return 0

if "form_iter" not in st.session_state: st.session_state.form_iter = 0
if "v_vals" not in st.session_state: st.session_state.v_vals = {}

def trigger_reset():
    st.session_state.form_iter += 1
    st.session_state.v_vals = {}

def load_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&t={int(time.time())}"
        df = pd.read_csv(url, dtype={0: str})
        return df[df.iloc[:, 0].notna()]
    except: return None

df = load_data()
if df is not None:
    namen = df.iloc[:, 0].unique().tolist()
    st.title("💀 THE GANG HQ")
    c1, c2 = st.columns(2)
    n_sel = c1.selectbox("Spieler", ["Wählen..."] + namen, on_change=trigger_reset)
    d_sel = c2.selectbox("Deck", list(range(1, 16)), on_change=trigger_reset)
    
    if n_sel != "Wählen...":
        sz = df[df.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        db_vals = [safe_int(sz.iloc[0, start_c + i]) for i in range(9)]

        v_in = st.text_input("Zahlenkette (z.B. 110022111):", key=f"v_{st.session_state.form_iter}")
        if v_in:
            digs = re.findall(r'\d', v_in)
            if len(digs) >= 9:
                for i in range(9): st.session_state.v_vals[i] = int(digs[i])
                st.success(f"Erkannt: {' | '.join(digs[:9])}")

        neue_werte = []
        cols = st.columns(3) + st.columns(3) + st.columns(3)
        for i in range(9):
            with cols[i]:
                cur = st.session_state.v_vals.get(i, db_vals[i])
                v = st.number_input(f"K{i+1}", 0, 9, value=cur, key=f"k_{i}_{st.session_state.form_iter}")
                neue_werte.append(v)
        
        if st.button("🚀 SPEICHERN", use_container_width=True):
            w_str = ",".join([str(int(x)) for x in neue_werte])
            try:
                r = requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": w_str}, timeout=15)
                st.balloons()
                st.success("Gesendet! Prüfe dein Sheet.")
                time.sleep(2)
                trigger_reset()
                st.rerun()
            except Exception as e: st.error(f"Fehler: {e}")
