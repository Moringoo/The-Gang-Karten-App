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
    .voice-hint { background-color: #262730; padding: 10px; border-radius: 5px; border-left: 5px solid #3b82f6; margin-bottom: 15px; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

try:
    # Daten laden
    df_raw = pd.read_csv(SHEET_URL, dtype={0: str})
    
    # FILTER: Leere Zeilen UND "Leer" / "Platzhalter" entfernen
    df_raw = df_raw[df_raw.iloc[:, 0].notna()]
    df_raw = df_raw[df_raw.iloc[:, 0].str.strip() != ""]
    df_raw = df_raw[~df_raw.iloc[:, 0].str.strip().str.lower().isin(['leer', 'platzhalter'])]
    
    # "Male" Fix
    df_raw.iloc[:, 0] = df_raw.iloc[:, 0].replace(['Männlich', 'männlich', 'MAN'], 'Male')
    
    # Namen in Original-Reihenfolge
    spieler_namen = df_raw.iloc[:, 0].unique().tolist()

    st.markdown('<p class="main-title">💀 THE GANG: HQ FINAL</p>', unsafe_allow_html=True)

    # --- BEREICH 1: KARTEN-EINGABE ---
    st.markdown("### 📝 KARTEN AKTUALISIEREN")
    col1, col2 = st.columns(2)
    n_sel = col1.selectbox("Wer bist du?", ["Wählen..."] + spieler_namen)
    d_sel = col2.selectbox("Welches Deck?", list(range(1, 16)))
    
    if n_sel != "Wählen...":
        s_zeile = df_raw[df_raw.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        vals = [safe_int(s_zeile.iloc[0, start_c + i]) for i in range(9)]
        
        # --- NEU: SPRACH- / SCHNELL-EINGABE ---
        st.markdown('<div class="voice-hint">🎙️ <b>Schnell-Eingabe:</b> Nutze das Mikrofon deiner Tastatur. Sprich 9 Zahlen (z.B. "1 0 2 0 1 1 0 0 2")</div>', unsafe_allow_html=True)
        voice_input = st.text_input("Sprich oder tippe alle 9 Werte hier rein...", key="voice_input")
        
        if voice_input:
            found_nums = re.findall(r'\d+', voice_input)
            if len(found_nums) >= 9:
                for i in range(9):
                    vals[i] = int(found_nums[i])
                st.success("💡 Die 9 Zahlen wurden unten in die Felder verteilt!")

        # 3x3 Raster - Streng K1 bis K9
        neue_werte = [0] * 9
        all_cols = st.columns(3) + st.columns(3) + st.columns(3)
        for i in range(9):
            with all_cols[i]:
                neue_werte[i] = st.number_input(f"K{i+1}", 0, 9, value=vals[i], key=f"inp_{n_sel}_{d_sel}_{i}")
        
        if st.button("🚀 ÄNDERUNGEN SPEICHERN", use_container_width=True):
            werte_str = ",".join([str(int(v)) for v in neue_werte])
            requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": werte_str})
            st.balloons()
            st.success(f"Check! Die Karten für {n_sel} wurden aktualisiert.")
            time.sleep(2)
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- BEREICH 2: AUTOMATISCHE TAUSCHANALYSE ---
    if st.text_input("Admin-Passwort", type="password") == ADMIN_PASSWORT:
        st.markdown("### 🕵️‍♂️ BESTE TAUSCH-OPTIONEN")
        
        gebot, bedarf = [], []
        for _, row in df_raw.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                bz, dia_count = 0, 0
                for i in range(9):
                    cn = df_raw.columns[sc + i]
                    val = safe_int(row.iloc[sc + i])
                    if val > 0: bz += 1
                    if "(D)" in cn: dia_count += 1
                
                for i in range(9):
                    cn = df_raw.columns[sc + i]
                    val = safe_int(row.iloc[sc + i])
                    if val >= 2:
                        gebot.append({"s": sp, "k": cn})
                    elif val == 0:
                        bedarf.append({
                            "s": sp, "k": cn, "f": bz, "d_val": dia_count, "did": f"{sp}_D{d}"
                        })

        # --- SORTIER-LOGIK: 8/9 vor 7/9 | Dann Diamanten ---
        bedarf = sorted(bedarf, key=lambda x: (x['f'], x['d_val']), reverse=True)
        
        def get_matches(is_dia_tab):
            res, weg = [], set()
            fort_map = {b['did']: b['f'] for b in bedarf}
            for b in bedarf:
                if (("(D)" in b["k"]) == is_dia_tab):
                    for g in gebot:
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            akt = fort_map[b['did']]
                            label = "**🚨 FINISHER!**" if akt == 8 else f"({akt}/9)"
                            res.append(f"{label} {g['s']} ➔ {b['s']} ({g['k']})")
                            fort_map[b['did']] += 1
                            weg.add(g["s"])
                            break
            return res

        t1, t2 = st.tabs(["🌕 GOLD-KARTEN", "💎 DIAMANT-KARTEN"])
        with t1:
            for m in get_matches(False): st.success(m)
        with t2:
            for m in get_matches(True): st.info(m)

except Exception as e:
    st.error(f"Daten-Fehler: {e}")
