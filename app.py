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

# --- HILFSFUNKTIONEN ---
def safe_int(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan":
            return 0
        return int(float(str(val).replace(',', '.')))
    except:
        return 0

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #1f2937; color: #fbbf24; border: 1px solid #fbbf24; font-weight: bold; border-radius: 10px; }
    .main-title { text-align: center; color: #fbbf24; font-size: 2.5rem; font-weight: bold; margin-bottom: 0; }
    .sub-title { text-align: center; color: #9ca3af; font-size: 1.2rem; margin-top: 0; margin-bottom: 2rem; }
    .stat-card { background-color: #1f2937; padding: 10px; border-radius: 10px; border-top: 3px solid #fbbf24; text-align: center; }
    hr { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">THE GANG: HAUPTQUARTIER</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">💀 TOTENKOPFGANG 💀</p>', unsafe_allow_html=True)

try:
    # Daten laden und direkt bereinigen
    df_raw = pd.read_csv(SHEET_URL)
    
    # FILTER: Entferne leere Zeilen und den Begriff "Männlich" aus der Namensliste
    # Wir löschen alle Zeilen, wo die erste Spalte leer ist oder "Männlich" heißt
    df_raw = df_raw[df_raw.iloc[:, 0].notna()]
    df_raw = df_raw[df_raw.iloc[:, 0].str.strip() != ""]
    df_raw = df_raw[df_raw.iloc[:, 0].str.strip() != "Männlich"]
    
    spieler_namen = df_raw.iloc[:, 0].unique().tolist()
    
    # --- DASHBOARD ---
    st.markdown("### 🏆 DECK-FINISHER (PRIORITÄT)")
    decks_prio = []
    for _, row in df_raw.iterrows():
        spieler = str(row.iloc[0]).strip()
        for d in range(1, 16):
            start_col = 1 + ((d - 1) * 9)
            if start_col + 8 < len(df_raw.columns):
                count = sum(1 for i in range(9) if safe_int(row.iloc[start_col + i]) > 0)
                if 7 <= count < 9:
                    decks_prio.append({"s": spieler, "d": d, "c": count})

    if decks_prio:
        top_decks = sorted(decks_prio, key=lambda x: x['c'], reverse=True)[:6]
        cols = st.columns(len(top_decks))
        for i, item in enumerate(top_decks):
            with cols[i]:
                st.markdown(f'<div class="stat-card"><small>DECK {item["d"]}</small><br><b>{item["s"]}</b><br>{item["c"]}/9</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- KARTEN EINGABE ---
    with st.expander("📝 MEINE KARTEN AKTUALISIEREN"):
        col_a, col_b = st.columns(2)
        with col_a: name_sel = st.selectbox("Wer bist du?", ["Bitte wählen..."] + spieler_namen)
        with col_b: deck_sel = st.selectbox("Welches Deck?", list(range(1, 16)))
        if name_sel != "Bitte wählen...":
            aktuelle_werte = [0] * 9
            spieler_zeile = df_raw[df_raw.iloc[:, 0] == name_sel]
            if not spieler_zeile.empty:
                start_col = 1 + ((deck_sel - 1) * 9)
                for i in range(9):
                    aktuelle_werte[i] = safe_int(spieler_zeile.iloc[0, start_col + i])
            
            r1, r2, r3 = st.columns(3), st.columns(3), st.columns(3)
            grids = r1 + r2 + r3
            neue_werte = [str(int(grids[i].number_input(f"K{i+1}", 0, 9, value=aktuelle_werte[i], key=f"e_{name_sel}_{deck_sel}_{i}"))) for i in range(9)]
            if st.button("🚀 SPEICHERN"):
                res = requests.get(SCRIPT_URL, params={"name": name_sel, "deck": deck_sel, "werte": ",".join(neue_werte)})
                if res.text == "Erfolg": st.success("Gespeichert!"); st.balloons()

    # --- ADMIN TAUSCH ANALYSE ---
    st.markdown("### 🕵️‍♂️ ADMIN-BEREICH")
    if st.text_input("Sicherheits-Code", type="password") == ADMIN_PASSWORT:
        
        gebot, bedarf = [], []
        for _, row in df_raw.iterrows():
            spieler = str(row.iloc[0]).strip()
            # Sicherheitscheck: Überspringe leere Namen oder Geister-Einträge
            if not spieler or spieler.lower() in ["nan", "männlich", "none"]: continue
            
            for d in range(1, 16):
                start_c = 1 + ((d - 1) * 9)
                besitz = sum(1 for i in range(9) if safe_int(row.iloc[start_c + i]) > 0)
                for i in range(9):
                    if start_c + i < len(df_raw.columns):
                        c_name = df_raw.columns[start_c + i]
                        anz = safe_int(row.iloc[start_c + i])
                        if anz >= 2: gebot.append({"s": spieler, "k": c_name})
                        elif anz == 0: bedarf.append({"s": spieler, "k": c_name, "f": besitz, "d_id": f"{spieler}_D{d}"})

        bedarf = sorted(bedarf, key=lambda x: (x['f'], x['d_id']), reverse=True)

        def get_matches(is_dia):
            results, weg_geber = [], set()
            fortschritt_tracker = {b['d_id']: b['f'] for b in bedarf}
            for b in bedarf:
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        if g["s"] not in weg_geber and g["s"] != b["s"] and g["k"] == b["k"]:
                            aktuell = fortschritt_tracker[b['d_id']]
                            if aktuell >= 9: continue
                            label = "🚨 FINISHER!" if aktuell == 8 else f"({aktuell}/9)"
                            results.append(f"**{label}** {g['s']} ➔ {b['s']} ({b['k']})")
                            fortschritt_tracker[b['d_id']] += 1
                            weg_geber.add(g["s"])
                            break
            return results

        t1, t2 = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        with t1:
            for m in get_matches(False): st.success(m)
        with t2:
            for m in get_matches(True): st.info(m)
            
except Exception as e:
    st.error(f"Kritischer Fehler: {e}")
