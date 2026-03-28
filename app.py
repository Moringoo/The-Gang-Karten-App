import streamlit as st
import pandas as pd
import requests
import time
import re

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ Final", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaIWcjmJ5Nn5MsRR66ptz97MBjJ-S0O-B7TVp1Y4pq81Xc1Q0VLNzDFWDn6c9NcB4/exec" 
GID = "2025591169"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"
ADMIN_PASSWORT = "gang2026" 

def safe_int(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan": return 0
        return int(float(str(val).replace(',', '.')))
    except: return 0

def text_to_numbers(text):
    d = {"null": "0", "eins": "1", "zwei": "2", "drei": "3", "vier": "4", 
         "fünf": "5", "sechs": "6", "sieben": "7", "acht": "8", "neun": "9"}
    text = text.lower()
    for word, num in d.items():
        text = text.replace(word, num)
    return text

# --- 3. SESSION STATE INITIALISIEREN ---
if 'karten_werte' not in st.session_state:
    st.session_state.karten_werte = [0] * 9

# --- 4. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-title { text-align: center; color: #fbbf24; font-size: 2.2rem; font-weight: bold; margin-bottom: 20px; }
    .voice-hint { background-color: #262730; padding: 10px; border-radius: 5px; border-left: 5px solid #3b82f6; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

try:
    df_raw = pd.read_csv(SHEET_URL, dtype={0: str})
    df_raw = df_raw[df_raw.iloc[:, 0].notna() & (df_raw.iloc[:, 0].str.strip() != "")]
    df_raw = df_raw[~df_raw.iloc[:, 0].str.strip().str.lower().isin(['leer', 'platzhalter'])]
    df_raw.iloc[:, 0] = df_raw.iloc[:, 0].replace(['Männlich', 'männlich', 'MAN'], 'Male')
    spieler_namen = df_raw.iloc[:, 0].unique().tolist()

    st.markdown('<p class="main-title">💀 THE GANG: HQ FINAL</p>', unsafe_allow_html=True)

    # --- BEREICH 1: KARTEN-EINGABE ---
    st.markdown("### 📝 KARTEN AKTUALISIEREN")
    col1, col2 = st.columns(2)
    n_sel = col1.selectbox("Wer bist du?", ["Wählen..."] + spieler_namen, key="name_select")
    d_sel = col2.selectbox("Welches Deck?", list(range(1, 16)), key="deck_select")
    
    if n_sel != "Wählen...":
        # Initial-Werte laden, falls noch nicht geschehen oder User gewechselt hat
        s_zeile = df_raw[df_raw.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        db_vals = [safe_int(s_zeile.iloc[0, start_c + i]) for i in range(9)]
        
        # Spracheingabe-Logik
        st.markdown('<div class="voice-hint">🎙️ <b>Spracheingabe:</b> Zahlen sprechen und <b>Enter</b> drücken.</div>', unsafe_allow_html=True)
        
        def process_voice():
            v_input = st.session_state.voice_input_field
            if v_input:
                clean = text_to_numbers(v_input)
                nums = re.findall(r'\d+', clean)
                if len(nums) >= 9:
                    for i in range(9):
                        st.session_state[f"k_val_{i}"] = int(nums[i])
                    st.toast("✅ Karten verteilt!", icon="🎯")

        st.text_input("Hier reinsprechen...", key="voice_input_field", on_change=process_voice)

        # 3x3 Raster
        neue_werte = []
        cols = st.columns(3) + st.columns(3) + st.columns(3)
        for i in range(9):
            with cols[i]:
                # Wir nutzen die DB-Werte als Default, falls im State noch nichts steht
                val = st.number_input(f"K{i+1}", 0, 9, value=db_vals[i], key=f"k_val_{i}")
                neue_werte.append(val)
        
        if st.button("🚀 ÄNDERUNGEN SPEICHERN", use_container_width=True):
            werte_str = ",".join([str(int(v)) for v in neue_werte])
            requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": werte_str})
            st.balloons()
            st.success("Gespeichert!")
            time.sleep(1)
            st.rerun()

    # --- BEREICH 2: ANALYSE ---
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.text_input("Admin-Passwort", type="password") == ADMIN_PASSWORT:
        st.markdown("### 🕵️‍♂️ TAUSCH-CHECK")
        gebot, bedarf = [], []
        for _, row in df_raw.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                bz, dia = 0, 0
                for i in range(9):
                    cn = df_raw.columns[sc + i]
                    val = safe_int(row.iloc[sc + i])
                    if val > 0: bz += 1
                    if "(D)" in cn: dia += 1
                for i in range(9):
                    cn = df_raw.columns[sc + i]
                    val = safe_int(row.iloc[sc + i])
                    if val >= 2: gebot.append({"s": sp, "k": cn})
                    elif val == 0: bedarf.append({"s": sp, "k": cn, "f": bz, "d": dia, "did": f"{sp}_D{d}"})

        bedarf = sorted(bedarf, key=lambda x: (x['f'], x['d']), reverse=True)
        
        def get_matches(is_dia):
            res, weg = [], set()
            f_map = {b['did']: b['f'] for b in bedarf}
            for b in bedarf:
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            akt = f_map[b['did']]
                            l = "**🚨 FINISHER!**" if akt == 8 else f"({akt}/9)"
                            res.append(f"{l} {g['s']} ➔ {b['s']} ({g['k']})")
                            f_map[b['did']] += 1; weg.add(g["s"])
                            break
            return res

        t1, t2 = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        with t1:
            for m in get_matches(False): st.success(m)
        with t2:
            for m in get_matches(True): st.info(m)

except Exception as e:
    st.error(f"Fehler: {e}")
