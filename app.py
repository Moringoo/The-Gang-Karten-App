import streamlit as st
import pandas as pd
import requests

# --- 1. SETUP (ICON & TITEL FÜR DEN BROWSER-TAB) ---
st.set_page_config(
    page_title="The Gang HQ", 
    page_icon="🛡️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. KONFIGURATION (DEINE LINKS & PASSWORT) ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaIWcjmJ5Nn5MsRR66ptz97MBjJ-S0O-B7TVp1Y4pq81Xc1Q0VLNzDFWDn6c9NcB4/exec" 
GID = "2025591169"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"
ADMIN_PASSWORT = "gang2026" 

# --- 3. THE GANG DESIGN (DARK MODE & GOLD) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #1f2937; color: #fbbf24; border: 1px solid #fbbf24; font-weight: bold; width: 100%; border-radius: 10px; }
    .stNumberInput input { background-color: #1f2937 !important; color: white !important; border-radius: 5px; }
    .stSelectbox div[data-baseweb="select"] > div { background-color: #1f2937; color: white; }
    hr { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ THE GANG: HAUPTQUARTIER")

# --- BEREICH 1: KARTEN-EINGABE (FÜR ALLE SPIELER) ---
st.markdown("### 📝 MEINE KARTEN AKTUALISIEREN")
st.caption("Wähle deinen Namen und das Deck. Gib für jede Karte die Anzahl ein: 0 (Suche), 1 (Besitze), 2 (Doppelt).")

try:
    # Lade die Namen live aus dem Google Sheet
    df_raw = pd.read_csv(SHEET_URL)
    spieler_namen = df_raw.iloc[:, 0].dropna().unique().tolist()
    
    # Layout für Name und Deck (2 Spalten)
    col_name, col_deck = st.columns(2)
    with col_name:
        name_sel = st.selectbox("Wer bist du?", ["Bitte wählen..."] + spieler_namen)
    with col_deck
