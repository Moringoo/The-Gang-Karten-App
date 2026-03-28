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

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-title { text-align: center; color: #fbbf24; font-size: 2.2rem; font-weight: bold; margin-bottom: 20px; }
    .voice-area { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 2px solid #3b82f6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Callback-Funktion zum Leeren des Voice-Feldes bei Deck/Namenswechsel
def reset_voice_field():
    if "voice_box" in st.session_state:
        st.session_state.voice_box = ""

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
    # Bei Änderung des Namens oder Decks wird das Sprachfeld geleert
    n_sel = col1.selectbox("Wer bist du?", ["Wählen..."] + spieler_namen, on_change=reset_voice_field)
    d_sel = col2.selectbox("Welches Deck?", list(range(1, 16)), on_change=reset_voice_field)
    
    if n_sel != "Wählen...":
        s_zeile = df_raw[df_raw.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        db_vals = [safe_int(s_zeile.iloc[0, start_c + i]) for i in range(9)]

        # --- VOICE LOGIK ---
        st.markdown('<div class="voice-area">', unsafe_allow_html=True)
        st.write("🎙️ **SCHNELL-EINGABE (ZAHLENKETTE)**")
        v_in = st.text_input("Spreche 9 Zahlen (z.B. 101131102) und drücke ENTER:", key="voice_box")
        
        if v_in:
            all_digits = re.findall(r'\d', v_in) 
            if len(all_digits) >= 9:
                for i in range(9):
                    st.session_state[f"k_val_{i}"] = int(all_digits[i])
                st.success(f"✅ Kette erkannt: {' | '.join(all_digits[:9])}")
            else:
                st.warning(f"⚠️ Kette zu kurz! Nur {len(all_digits)} von 9 Zahlen erkannt.")
        st.markdown('</div>', unsafe_allow_html=True)

        # 3x3 Raster
        neue_werte = []
        c = st.columns(3) + st.columns(3) + st.columns(3)
        for i in range(9):
            with c[i]:
                val = st.number_input(f"K{i+1}", 0, 9, value=db_vals[i], key=f"k_val_{i}")
                neue_werte.append(val)
        
        if st.button("🚀 ÄNDERUNGEN SPEICHERN", use_container_width=True):
            werte_str = ",".join([str(int(v)) for v in neue_werte])
            requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": werte_str})
            st.balloons()
            st.success("Erfolgreich gespeichert!")
            reset_voice_field() # Feld nach dem Speichern leeren
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
            for b in bedarf:
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            l = "**🚨 FINISHER!**" if b['f'] == 8 else f"({b['f']}/9)"
                            res.append(f"{l} {g['s']} ➔ {b['s']} ({g['k']})")
                            weg.add(g["s"])
                            break
            return res

        t1, t2 = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        with t1:
            for m in get_matches(False): st.success(m)
        with t2:
            for m in get_matches(True): st.info(m)

except Exception as e:
    st.error(f"Fehler: {e}")
