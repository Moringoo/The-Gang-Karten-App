import streamlit as st
import pandas as pd
import requests

# --- 1. SETUP ---
st.set_page_config(
    page_title="The Gang HQ", 
    page_icon="🛡️", 
    layout="wide"
)

# --- 2. KONFIGURATION ---
# Nutze hier unbedingt die NEUE SCRIPTURL, falls du das Apps Script im Google Sheet angepasst hast!
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaIWcjmJ5Nn5MsRR66ptz97MBjJ-S0O-B7TVp1Y4pq81Xc1Q0VLNzDFWDn6c9NcB4/exec" 
GID = "2025591169"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"
ADMIN_PASSWORT = "gang2026" 

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #1f2937; color: #fbbf24; border: 1px solid #fbbf24; font-weight: bold; width: 100%; border-radius: 10px; }
    hr { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ THE GANG: HAUPTQUARTIER")

# --- BEREICH 1: KARTEN-EINGABE ---
st.markdown("### 📝 MEINE KARTEN AKTUALISIEREN")

# --- DER TRY-BLOCK AUS BILD 4 ---
try:
    # Lade die Namen live aus dem Google Sheet
    df_raw = pd.read_csv(SHEET_URL)
    spieler_namen = df_raw.iloc[:, 0].dropna().unique().tolist()
    
    col_a, col_b = st.columns(2)
    with col_a:
        name_sel = st.selectbox("Wer bist du?", ["Bitte wählen..."] + spieler_namen)
    with col_b:
        deck_sel = st.selectbox("Welches Deck?", list(range(1, 16)))
    
    st.info(f"Eingabe für: **{name_sel}** | **Deck {deck_sel}**")
    
    # 3x3 Raster für Handy
    r1 = st.columns(3)
    r2 = st.columns(3)
    r3 = st.columns(3)
    alle_grids = r1 + r2 + r3
    
    neue_werte = []
    for i in range(9):
        with alle_grids[i]:
            # DER TRICK (GEGEN DECK-VERMISCHUNG): Eindeutige IDs
            v = st.number_input(
                f"K{i+1}", 
                min_value=0, 
                max_value=9, 
                value=0, 
                step=1, 
                key=f"user_{name_sel}_deck_{deck_sel}_k{i}"
            )
            neue_werte.append(str(int(v)))
    
    if st.button("🚀 DATEN SPEICHERN"):
        if name_sel == "Bitte wählen...":
            st.warning("Bitte wähle zuerst deinen Namen aus!")
        else:
            with st.spinner(f"Speichere Deck {deck_sel} für {name_sel}..."):
                try:
                    # Sende Name, Deck und die 9 Werte (Das Apps Script muss dies verarbeiten!)
                    payload = {
                        "name": name_sel,
                        "deck": deck_sel,
                        "werte": ",".join(neue_werte)
                    }
                    res = requests.get(SCRIPT_URL, params=payload, timeout=15)
                    if res.text == "Erfolg":
                        st.success(f"Check! Deck {deck_sel} wurde im Sheet gespeichert.")
                        st.balloons()
                    else:
                        st.error(f"Fehler vom Server: {res.text}")
                except:
                    st.error("Verbindung zum Google Sheet fehlgeschlagen.")
                    
except Exception as e:
    # Falls die Liste nicht lädt, wird hier der Fehler ausgegeben
    st.error(f"Fehler beim Laden der Spielerliste: {e}")

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# --- BEREICH 2: ADMIN-TRESOR ---
# (Hier bleibt dein Admin-Code mit Passwort-Abfrage und Tausch-Analyse...)
