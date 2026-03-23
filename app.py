import streamlit as st
import pandas as pd
import requests

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

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

# --- 3. STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-title { text-align: center; color: #fbbf24; font-size: 2.2rem; font-weight: bold; margin-bottom: 25px; }
    .prio-card { background-color: #1e293b; border-left: 5px solid #ef4444; padding: 10px; border-radius: 8px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

try:
    # Daten laden und Namen-Fix (Male/Männlich)
    df_raw = pd.read_csv(SHEET_URL, dtype={0: str})
    df_raw = df_raw[df_raw.iloc[:, 0].notna() & (df_raw.iloc[:, 0].str.strip() != "")]
    df_raw.iloc[:, 0] = df_raw.iloc[:, 0].replace(['Männlich', 'männlich', 'MAN'], 'Male')
    
    spieler_namen = sorted(df_raw.iloc[:, 0].unique().tolist())

    st.markdown('<p class="main-title">💀 THE GANG: HQ</p>', unsafe_allow_html=True)

    # --- BEREICH 1: SCHNELLE EINGABE ---
    with st.container():
        st.markdown("### 📝 KARTEN-UPDATE")
        c1, c2 = st.columns(2)
        n_sel = c1.selectbox("Spieler wählen", ["Wählen..."] + spieler_namen)
        d_sel = c2.selectbox("Deck wählen", list(range(1, 16)))
        
        if n_sel != "Wählen...":
            s_zeile = df_raw[df_raw.iloc[:, 0] == n_sel]
            start_c = 1 + ((d_sel - 1) * 9)
            
            # Aktuelle Werte aus dem Sheet laden
            aktuelle_werte = [safe_int(s_zeile.iloc[0, start_c + i]) for i in range(9)]
            
            # 3x3 Raster für die Eingabe
            neue_werte = []
            cols = st.columns(3)
            for i in range(9):
                with cols[i % 3]:
                    v = st.number_input(f"Karte {i+1}", 0, 9, value=aktuelle_werte[i], key=f"k_{i}")
                    neue_werte.append(str(int(v)))
            
            if st.button("🚀 JETZT SPEICHERN", use_container_width=True):
                with st.spinner("Wird übertragen..."):
                    requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": ",".join(neue_werte)})
                    st.success(f"Check! Deck {d_sel} für {n_sel} ist aktuell.")
                    st.rerun()

    st.markdown("---")

    # --- BEREICH 2: AUTOMATISCHE ANALYSE ---
    pw = st.text_input("Admin-Passwort", type="password")
    if pw == ADMIN_PASSWORT:
        st.markdown("### 🎯 EMPFOHLENE TAUSCHE")
        
        gebot, bedarf = [], []
        for _, row in df_raw.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                # Fortschritt berechnen
                besitz = sum(1 for i in range(9) if safe_int(row.iloc[sc + i]) > 0)
                
                for i in range(9):
                    cn = df_raw.columns[sc + i]
                    val = safe_int(row.iloc[sc + i])
                    if val >= 2:
                        gebot.append({"s": sp, "k": cn})
                    elif val == 0:
                        bedarf.append({"s": sp, "k": cn, "f": besitz, "did": f"{sp}_D{d}"})

        # Finisher (8/9) zuerst
        bedarf = sorted(bedarf, key=lambda x: (x['f'], x['did']), reverse=True)
        
        def get_matches(is_dia):
            res, weg = [], set()
            fort_map = {b['did']: b['f'] for b in bedarf}
            for b in bedarf:
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            akt = fort_map[b['did']]
                            # Optische Hervorhebung für Finisher
                            prefix = "🚨 **FINISHER!**" if akt == 8 else f"({akt}/9)"
                            res.append(f"{prefix} {g['s']} ➔ {b['s']} ({b['k']})")
                            fort_map[b['did']] += 1
                            weg.add(g["s"])
                            break
            return res

        t1, t2 = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        with t1:
            for m in get_matches(False): st.success(m)
        with t2:
            for m in get_matches(True): st.info(m)

except Exception as e:
    st.error(f"Hinweis: {e}")
