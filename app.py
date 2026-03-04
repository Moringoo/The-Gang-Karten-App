import streamlit as st
import pandas as pd
import requests

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaIWcjmJ5Nn5MsRR66ptz97MBjJ-S0O-B7TVp1Y4pq81Xc1Q0VLNzDFWDn6c9NcB4/exec" 
GID = "2025591169"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #1f2937; color: #fbbf24; border: 1px solid #fbbf24; font-weight: bold; width: 100%; border-radius: 10px; }
    .main-title { text-align: center; color: #fbbf24; font-size: 2.5rem; font-weight: bold; margin-bottom: 0; }
    hr { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">THE GANG: HAUPTQUARTIER</p>', unsafe_allow_html=True)

# --- DATEN LADEN ---
try:
    df_raw = pd.read_csv(SHEET_URL)
    spieler_namen = df_raw.iloc[:, 0].dropna().unique().tolist()
    
    col_a, col_b = st.columns(2)
    with col_a:
        name_sel = st.selectbox("Wer bist du?", ["Bitte wählen..."] + spieler_namen)
    with col_b:
        deck_sel = st.selectbox("Welches Deck?", list(range(1, 16)))

    if name_sel != "Bitte wählen...":
        # Aktuelle Zeile des Spielers finden
        spieler_data = df_raw[df_raw.iloc[:, 0] == name_sel]
        
        # Start-Spalte für das gewählte Deck berechnen (Deck 1 beginnt bei Spalte 1, Index 0 ist Name)
        start_idx = 1 + ((deck_sel - 1) * 9)
        
        # Aktuelle Werte aus dem Sheet holen
        aktuelle_werte_aus_sheet = []
        if not spieler_data.empty:
            for i in range(9):
                val = spieler_data.iloc[0, start_idx + i]
                # Sicherstellen, dass es eine Zahl ist
                try:
                    aktuelle_werte_aus_sheet.append(int(float(str(val).replace(',', '.'))))
                except:
                    aktuelle_werte_aus_sheet.append(0)
        else:
            aktuelle_werte_aus_sheet = [0] * 9

        st.info(f"Aktuelle Karten für {name_sel} (Deck {deck_sel}) geladen.")

        # 3x3 Raster für Eingabe
        r1, r2, r3 = st.columns(3), st.columns(3), st.columns(3)
        alle_grids = r1 + r2 + r3
        
        neue_werte = []
        for i in range(9):
            with alle_grids[i]:
                # TRICK: Wir setzen 'value' auf den Wert, der gerade im Sheet steht!
                v = st.number_input(
                    f"K{i+1}", 0, 9, 
                    value=aktuelle_werte_aus_sheet[i], 
                    step=1, 
                    key=f"input_{name_sel}_{deck_sel}_k{i}"
                )
                neue_werte.append(str(int(v)))
        
        if st.button("🚀 ÄNDERUNGEN SPEICHERN"):
            with st.spinner("Übertrage Daten..."):
                try:
                    payload = {"name": name_sel, "deck": deck_sel, "werte": ",".join(neue_werte)}
                    res = requests.get(SCRIPT_URL, params=payload, timeout=15)
                    if res.text == "Erfolg":
                        st.success("Erfolgreich aktualisiert!")
                        st.balloons()
                        st.cache_data.clear() # Cache leeren, um neue Daten zu erzwingen
                    else:
                        st.error(f"Fehler: {res.text}")
                except:
                    st.error("Server nicht erreichbar.")

except Exception as e:
    st.error(f"Konnte Daten nicht laden: {e}")

# (Admin Bereich bleibt wie gehabt...)
