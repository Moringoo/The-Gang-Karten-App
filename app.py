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

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-title { text-align: center; color: #fbbf24; font-size: 2.2rem; font-weight: bold; margin-bottom: 20px; }
    .finisher-badge { background-color: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; }
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.4; } }
    </style>
    """, unsafe_allow_html=True)

try:
    # Daten laden
    df_raw = pd.read_csv(SHEET_URL)
    df_raw = df_raw[df_raw.iloc[:, 0].notna() & (df_raw.iloc[:, 0].str.strip() != "")]
    spieler_namen = sorted(df_raw.iloc[:, 0].unique().tolist())

    st.markdown('<p class="main-title">💀 THE GANG: TAUSCH-ZENTRALE</p>', unsafe_allow_html=True)

    # --- BEREICH 1: KARTEN-EINGABE ---
    st.markdown("### 📝 KARTEN AKTUALISIEREN")
    col1, col2 = st.columns(2)
    n_sel = col1.selectbox("Wer bist du?", ["Wählen..."] + spieler_namen)
    d_sel = col2.selectbox("Welches Deck?", list(range(1, 16)))
    
    if n_sel != "Wählen...":
        s_zeile = df_raw[df_raw.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        vals = [safe_int(s_zeile.iloc[0, start_c + i]) for i in range(9)]
        
        # 3x3 Raster für die 9 Karten des Decks
        r1, r2, r3 = st.columns(3), st.columns(3), st.columns(3)
        all_cols = r1 + r2 + r3
        neue_werte = []
        for i in range(9):
            with all_cols[i]:
                v = st.number_input(f"K{i+1}", 0, 9, value=vals[i], key=f"inp_{n_sel}_{d_sel}_{i}")
                neue_werte.append(str(int(v)))
        
        if st.button("🚀 ÄNDERUNGEN SPEICHERN"):
            with st.spinner("Übertrage Daten..."):
                res = requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": ",".join(neue_werte)})
                if res.status_code == 200:
                    st.success("Erfolgreich im Sheet gespeichert!"); st.rerun()
                else:
                    st.error("Fehler beim Speichern.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- BEREICH 2: AUTOMATISCHE TAUSCHANALYSE ---
    st.markdown("### 🕵️‍♂️ BESTE TAUSCH-OPTIONEN")
    
    if st.text_input("Admin-Passwort", type="password") == ADMIN_PASSWORT:
        gebot, bedarf = [], []
        
        # Daten für Analyse aufbereiten
        for _, row in df_raw.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                # Wie viele Karten hat der Spieler in diesem Deck bereits?
                bz = sum(1 for i in range(9) if safe_int(row.iloc[sc + i]) > 0)
                
                for i in range(9):
                    cn = df_raw.columns[sc + i]
                    val = safe_int(row.iloc[sc + i])
                    
                    if val >= 2: # Karte ist doppelt (Gebot)
                        gebot.append({"s": sp, "k": cn})
                    elif val == 0: # Karte fehlt (Bedarf)
                        bedarf.append({"s": sp, "k": cn, "f": bz, "did": f"{sp}_D{d}"})

        # Sortierung: Decks mit hohem Fortschritt (Finisher) zuerst
        bedarf = sorted(bedarf, key=lambda x: (x['f'], x['did']), reverse=True)
        
        def get_matches(is_dia):
            res, weg = [], set()
            # Fortschritt pro Deck tracken
            fortschritt_map = {b['did']: b['f'] for b in bedarf}
            
            for b in bedarf:
                # Prüfen ob Gold oder Diamant gesucht wird
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        # Geber hat noch nichts abgegeben & ist nicht der Nehmer & hat die Karte
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            akt = fortschritt_map[b['did']]
                            if akt < 9:
                                label = "🚨 FINISHER!" if akt == 8 else f"({akt}/9)"
                                res.append(f"**{label}** {g['s']} ➔ {b['s']} ({b['k']})")
                                fortschritt_map[b['did']] += 1
                                weg.add(g["s"]) # Geber für diesen Durchgang sperren
                                break
            return res

        t1, t2 = st.tabs(["🌕 GOLD-KARTEN", "💎 DIAMANT-KARTEN"])
        with t1:
            matches_g = get_matches(False)
            if matches_g:
                for m in matches_g: st.success(m)
            else: st.info("Keine passenden Gold-Tausche gefunden.")
            
        with t2:
            matches_d = get_matches(True)
            if matches_d:
                for m in matches_d: st.info(m)
            else: st.info("Keine passenden Diamant-Tausche gefunden.")

except Exception as e:
    st.error(f"Fehler: {e}")
