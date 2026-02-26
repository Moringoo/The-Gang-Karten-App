import streamlit as st
import pandas as pd
import requests

# --- 1. SETUP ---
# Dein Google Apps Script Link
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaIWcjmJ5Nn5MsRR66ptz97MBjJ-S0O-B7TVp1Y4pq81Xc1Q0VLNzDFWDn6c9NcB4/exec" 
# Deine Google Sheet Daten
GID = "2025591169"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"

# --- DEIN PRIVATES PASSWORT ---
ADMIN_PASSWORT = "gang2026" # <--- Ändere dies in dein geheimes Passwort

st.set_page_config(page_title="The Gang HQ", layout="wide", initial_sidebar_state="collapsed")

# --- DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #1f2937; color: #fbbf24; border: 1px solid #fbbf24; font-weight: bold; width: 100%; }
    .stNumberInput input { background-color: #1f2937 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ THE GANG: HAUPTQUARTIER")

# --- BEREICH 1: KARTEN-EINGABE (FÜR ALLE SPIELER) ---
st.markdown("### 📝 MEINE KARTEN AKTUALISIEREN")
st.caption("Trage hier deine aktuellen Bestände ein. 0=Suche, 1=Besitze, 2=Doppelt.")

try:
    df_raw = pd.read_csv(SHEET_URL)
    spieler_namen = df_raw.iloc[:, 0].dropna().unique().tolist()
    
    # Eingabe-Felder
    col_a, col_b = st.columns(2)
    with col_a:
        name_sel = st.selectbox("Wer bist du?", ["Bitte wählen..."] + spieler_namen)
    with col_b:
        deck_sel = st.selectbox("Welches Deck?", list(range(1, 16)))
    
    # 3x3 Raster für Handy-Optimierung
    r1 = st.columns(3)
    r2 = st.columns(3)
    r3 = st.columns(3)
    alle_grids = r1 + r2 + r3
    
    neue_werte = []
    for i in range(9):
        with alle_grids[i]:
            v = st.number_input(f"K{i+1}", 0, 9, key=f"k{i}", step=1)
            neue_werte.append(str(int(v)))
    
    if st.button("🚀 DATEN SPEICHERN"):
        if name_sel == "Bitte wählen...":
            st.warning("Bitte wähle zuerst deinen Namen aus!")
        else:
            with st.spinner("Sende Daten..."):
                res = requests.get(f"{SCRIPT_URL}?name={name_sel}&deck={deck_sel}&werte={','.join(neue_werte)}")
                if res.text == "Erfolg":
                    st.success(f"Check! {name_sel}, Deck {deck_sel} wurde aktualisiert.")
                    st.balloons()
                else:
                    st.error(f"Fehler: {res.text}")
except Exception as e:
    st.error(f"Verbindung zum Sheet fehlgeschlagen: {e}")

st.markdown("---")

# --- BEREICH 2: ADMIN-TRESOR (NUR FÜR DICH) ---
st.markdown("### 🕵️‍♂️ ADMIN-BEREICH (TAUSCH-ANALYSE)")
pw_input = st.text_input("Sicherheits-Code für Tauschvorschläge", type="password", placeholder="Nur für den Administrator...")

if pw_input == ADMIN_PASSWORT:
    st.success("Admin-Zugriff bestätigt. Lade Tausch-Strategie...")
    
    try:
        df = pd.read_csv(SHEET_URL)
        karten_cols = df.columns[1:]
        
        decks = {}
        for col in karten_cols:
            d_name = col.split('-')[0]
            if d_name not in decks: decks[d_name] = []
            decks[d_name].append(col)

        gebot, bedarf_prio = [], []
        for _, row in df.iterrows():
            spieler = str(row.iloc[0]).strip()
            if spieler in ["nan", "None", ""]: continue
            
            for d_name, d_cols in decks.items():
                besitz = sum(1 for c in d_cols if pd.notna(row[c]) and int(float(str(row[c]).replace(',','.'))) > 0)
                for c in d_cols:
                    try:
                        anz = int(float(str(row[c]).replace(',', '.')))
                        if anz >= 2: gebot.append({"s": spieler, "k": c})
                        elif anz == 0: bedarf_prio.append({"s": spieler, "k": c, "f": besitz})
                    except: continue

        # 8/9 Fortschritt (Finisher) zuerst
        bedarf_prio = sorted(bedarf_prio, key=lambda x: x['f'], reverse=True)

        def get_matches(is_dia):
            res, weg = [], set()
            for b in bedarf_prio:
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            label = "🔥 FINISHER!" if b['f'] == 8 else f"({b['f']}/9)"
                            res.append(f"{label} | **{g['s']}** ➔ **{b['s']}** ({g['k']})")
                            weg.add(g["s"])
                            break
            return res

        t_gold, t_dia = st.tabs(["🌕 GOLD DEALS", "💎 DIAMANT DEALS"])
        with t_gold:
            m_g = get_matches(False)
            if m_g:
                for m in m_g: st.success(m)
            else: st.write("Keine Gold-Matches gefunden.")
        with t_dia:
            m_d = get_matches(True)
            if m_d:
                for m in m_d: st.info(m)
            else: st.write("Keine Diamant-Matches gefunden.")

    except Exception as e:
        st.error(f"Fehler bei der Analyse: {e}")
elif pw_input != "":
    st.error("Zugriff verweigert. Dieser Bereich ist dem Admin vorbehalten.")
