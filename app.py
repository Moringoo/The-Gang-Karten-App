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
    df_raw = pd.read_csv(SHEET_URL)
    spieler_namen = df_raw.iloc[:, 0].dropna().unique().tolist()
    
    # --- DASHBOARD ---
    st.markdown("### 🏆 DECK-FINISHER (PRIORITÄT)")
    decks_prio = []
    for _, row in df_raw.iterrows():
        spieler = str(row.iloc[0]).strip()
        if spieler in ["nan", "None", ""]: continue
        for d in range(1, 16):
            start_col = 1 + ((d - 1) * 9)
            if start_col + 8 < len(df_raw.columns):
                count = sum(1 for i in range(9) if pd.notna(row.iloc[start_col + i]) and int(float(str(row.iloc[start_col + i]).replace(',', '.'))) > 0)
                if count >= 7 and count < 9:
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
                    try: aktuelle_werte[i] = int(float(str(spieler_zeile.iloc[0, start_col + i]).replace(',', '.')))
                    except: pass
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
            for d in range(1, 16):
                start_c = 1 + ((d - 1) * 9)
                besitz = sum(1 for i in range(9) if int(float(str(row.iloc[start_c + i]).replace(',', '.'))) > 0)
                for i in range(9):
                    c_name = df_raw.columns[start_c + i]
                    anz = int(float(str(row.iloc[start_c + i]).replace(',', '.')))
                    if anz >= 2: gebot.append({"s": spieler, "k": c_name})
                    elif anz == 0: bedarf.append({"s": spieler, "k": c_name, "f": besitz, "d_id": f"{spieler}_D{d}"})

        # SORTIERUNG: Erst nach Fortschritt (f), dann nach Deck-ID
        # Das sorgt dafür, dass alle Karten eines Decks nacheinander abgearbeitet werden.
        bedarf = sorted(bedarf, key=lambda x: (x['f'], x['d_id']), reverse=True)

        def get_matches(is_dia):
            results, weg_geber = [], set()
            fortschritt_tracker = {b['d_id']: b['f'] for b in bedarf}

            for b in bedarf:
                if (("(D)" in b["k"]) == is_dia):
                    # NEU: Wir prüfen, ob dieser Spieler in DIESEM Deck schon eine Karte bekommen hat
                    # und bevorzugen ihn weiter, bis das Deck voll ist (max 9).
                    for g in gebot:
                        if g["s"] not in weg_geber and g["s"] != b["s"] and g["k"] == b["k"]:
                            aktuell = fortschritt_tracker[b['d_id']]
                            if aktuell >= 9: continue # Deck ist durch diese Runde schon voll
                            
                            label = "🚨 FINISHER!" if aktuell == 8 else f"({aktuell}/9)"
                            results.append(f"**{label}** {g['s']} ➔ {b['s']} ({b['k']})")
                            
                            fortschritt_tracker[b['d_id']] += 1
                            weg_geber.add(g["s"])
                            break
            return results

        t1, t2 = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        with t1:
            m_g = get_matches(False)
            for m in m_g: st.success(m)
        with t2:
            m_d = get_matches(True)
            for m in m_d: st.info(m)
            
except Exception as e: st.error(f"Fehler: {e}")
