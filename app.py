import streamlit as st
import pandas as pd
import requests

# --- 1. SETUP ---
st.set_page_config(
    page_title="The Gang HQ", 
    page_icon="🛡️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. KONFIGURATION ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaIWcjmJ5Nn5MsRR66ptz97MBjJ-S0O-B7TVp1Y4pq81Xc1Q0VLNzDFWDn6c9NcB4/exec" 
GID = "2025591169"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"
ADMIN_PASSWORT = "gang2026" 

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #1f2937; color: #fbbf24; border: 1px solid #fbbf24; font-weight: bold; width: 100%; border-radius: 10px; }
    .stNumberInput input { background-color: #1f2937 !important; color: white !important; border-radius: 5px; }
    hr { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ THE GANG: HAUPTQUARTIER")

# --- BEREICH 1: KARTEN-EINGABE ---
st.markdown("### 📝 MEINE KARTEN AKTUALISIEREN")

try:
    df_raw = pd.read_csv(SHEET_URL)
    spieler_namen = df_raw.iloc[:, 0].dropna().unique().tolist()
    
    col_a, col_b = st.columns(2)
    with col_a:
        name_sel = st.selectbox("Wer bist du?", ["Bitte wählen..."] + spieler_namen)
    with col_b:
        deck_sel = st.selectbox("Welches Deck?", list(range(1, 16)))
    
    # Das 3x3 Raster
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
                try:
                    res = requests.get(f"{SCRIPT_URL}?name={name_sel}&deck={deck_sel}&werte={','.join(neue_werte)}", timeout=15)
                    if res.text == "Erfolg":
                        st.success(f"Check! {name_sel}, Deck {deck_sel} wurde aktualisiert.")
                        st.balloons()
                    else:
                        st.error(f"Fehler: {res.text}")
                except:
                    st.error("Verbindungsfehler zum Google Sheet.")
except Exception as e:
    st.error(f"Fehler beim Laden der Daten: {e}")

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# --- BEREICH 2: ADMIN-TRESOR ---
st.markdown("### 🕵️‍♂️ ADMIN-BEREICH (TAUSCH-ANALYSE)")
pw_input = st.text_input("Sicherheits-Code für Tauschvorschläge", type="password", placeholder="Nur für den Administrator...")

if pw_input == ADMIN_PASSWORT:
    st.success("Admin-Zugriff bestätigt.")
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

        bedarf_prio = sorted(bedarf_prio, key=lambda x: x['f'], reverse=True)

        def get_matches(is_dia):
            matches_list, weg = [], set()
            for b in bedarf_prio:
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            label = "🔥 FINISHER!" if b['f'] == 8 else f"({b['f']}/9)"
                            matches_list.append(f"{label} | **{g['s']}** ➔ **{b['s']}** ({g['k']})")
                            weg.add(g["s"])
                            break
            return matches_list

        t_gold, t_dia = st.tabs(["🌕 GOLD DEALS", "💎 DIAMANT DEALS"])
        with t_gold:
            m_g = get_matches(False)
            if m_g:
                for match_item in m_g:
                    st.success(match_item)
            else:
                st.write("Keine Gold-Matches.")
        with t_dia:
            m_d = get_matches(True)
