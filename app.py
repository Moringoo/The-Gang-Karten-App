import streamlit as st
import pandas as pd
import requests

# --- KONFIGURATION ---
st.set_page_config(page_title="The Gang Manager", layout="wide")
st.title("🃏 The Gang Karten-Verwaltung")

# Deine Tabellen-ID (aus deinem Link)
SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
# CSV-Export Link zum Lesen
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=10) # Lädt alle 10 Sekunden neu
def load_data():
    return pd.read_csv(DATA_URL)

try:
    df = load_data()
    # Spalte 0 ist immer Name
    namen_liste = df.iloc[:, 0].dropna().unique().tolist()
    
    st.header("📝 Karten aktualisieren")
    col_a, col_b = st.columns(2)
    with col_a:
        name = st.selectbox("Wer bist du?", namen_liste)
    with col_b:
        deck_num = st.selectbox("Welches Deck?", range(1, 16))

    # Zeile des Spielers finden
    row_idx = df[df.iloc[:, 0] == name].index[0]
    start_col = 1 + (deck_num - 1) * 9
    
    st.write(f"### Deck {deck_num} von {name}")
    neue_werte = []
    cols = st.columns(3)
    
    for i in range(9):
        val = df.iloc[row_idx, start_col + i]
        if pd.isna(val): val = 0
        with cols[i % 3]:
            v = st.number_input(f"Karte {i+1}", min_value=0, value=int(val), key=f"k{i}")
            neue_werte.append(v)

    if st.button("💾 Speichern & Tabelle öffnen"):
        # Da direktes Schreiben gesperrt ist, öffnen wir die Tabelle zum Abgleich
        st.success("Werte gemerkt! Bitte trage sie kurz in der Tabelle ein.")
        st.link_button("👉 Hier zur Google Tabelle & Werte eintragen", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
        st.info("Hinweis: Da Google das automatische Speichern blockiert, ist dies der sicherste Weg für dein Team.")

except Exception as e:
    st.error("Bitte stelle sicher, dass die Google Tabelle für 'Jeden mit dem Link' freigegeben ist!")
