import streamlit as st
import pandas as pd
import requests

# --- 1. SETUP ---
st.set_page_config(
    page_title="The Gang HQ", 
    page_icon="💀", 
    layout="wide"
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
    .main-title { text-align: center; color: #fbbf24; font-size: 2.5rem; font-weight: bold; margin-bottom: 0; }
    .sub-title { text-align: center; color: #9ca3af; font-size: 1.2rem; margin-top: 0; margin-bottom: 2rem; }
    hr { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER (Text-basiert für maximale Stabilität) ---
st.markdown('<p class="main-title">THE GANG: HAUPTQUARTIER</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">💀 TOTENKOPFGANG 💀</p>', unsafe_allow_html=True)

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
    
    st.info(f"Eingabe für: **{name_sel}** | **Deck {deck_sel}**")
    
    r1, r2, r3 = st.columns(3), st.columns(3), st.columns(3)
    alle_grids = r1 + r2 + r3
    
    neue_werte = []
    for i in range(9):
        with alle_grids[i]:
            v = st.number_input(
                f"K{i+1}", 0, 9, value=0, step=1, 
                key=f"user_{name_sel}_deck_{deck_sel}_k{i}"
            )
            neue_werte.append(str(int(v)))
    
    if st.button("🚀 DATEN SPEICHERN"):
        if name_sel == "Bitte wählen...":
            st.warning("Bitte Namen wählen!")
        else:
            with st.spinner("Speichere..."):
                try:
                    payload = {"name": name_sel, "deck": deck_sel, "werte": ",".join(neue_werte)}
                    res = requests.get(SCRIPT_URL, params=payload, timeout=15)
                    if res.text == "Erfolg":
                        st.success("Gespeichert!")
                        st.balloons()
                    else:
                        st.error(f"Fehler: {res.text}")
                except Exception:
                    st.error("Verbindung zum Sheet fehlgeschlagen.")
except Exception as e:
    st.error(f"Fehler beim Laden: {e}")

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# --- BEREICH 2: ADMIN-TRESOR (TAUSCH-ANALYSE) ---
st.markdown("### 🕵️‍♂️ ADMIN-BEREICH (TAUSCH-ANALYSE)")
pw_input = st.text_input("Sicherheits-Code", type="password")

if pw_input == ADMIN_PASSWORT:
    st.success("Admin-Zugriff bestätigt.")
    try:
        df = pd.read_csv(SHEET_URL)
        karten_cols = df.columns[1:]
        
        decks = {}
        for col in karten_cols:
            d_name = col.split('-')[0]
            if d_
