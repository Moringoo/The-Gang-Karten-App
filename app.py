import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="The Gang - Karten Manager", layout="wide")
st.title("🃏 The Gang Karten-Verwaltung")

# Link zu deiner Tabelle
URL = "https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/edit?gid=0#gid=0"

# Verbindung zu Google Sheets herstellen
conn = st.connection("gsheets", type=GSheetsConnection)

# Daten laden
df = conn.read(spreadsheet=URL, usecols=list(range(137))) # Liest alle Spalten bis Deck 15

# Namen aus deiner Tabelle holen (Spalte 'Name')
namen_liste = df['Name'].dropna().unique().tolist()

# --- EINGABE-BEREICH ---
st.header("📝 Karten aktualisieren")
col_a, col_b = st.columns(2)

with col_a:
    auswahl_name = st.selectbox("Wähle deinen Namen:", namen_liste)
with col_b:
    auswahl_deck = st.selectbox("Wähle das Deck:", [f"Deck {i}" for i in range(1, 16)])

# Berechnung der Spaltennamen (K1 bis K9 für das jeweilige Deck)
# In deiner Tabelle sind Decks nebeneinander (K1-K9, dann K1-K9...)
deck_num = int(auswahl_deck.split()[1])
start_col_idx = 1 + (deck_num - 1) * 9  # Startindex für K1 des gewählten Decks

st.write(f"### Einträge für {auswahl_deck}")
neue_werte = []
cols = st.columns(3)

# Aktuelle Werte aus der Tabelle ziehen
spieler_index = df[df['Name'] == auswahl_name].index[0]

for i in range(9):
    spalten_name = df.columns[start_col_idx + i]
    aktueller_wert = df.iloc[spieler_index, start_col_idx + i]
    
    with cols[i % 3]:
        wert = st.number_input(f"Slot {i+1} ({spalten_name})", min_value=0, value=int(aktueller_wert), key=f"input_{i}")
        neue_werte.append(wert)

if st.button("💾 Speichern"):
    # Daten im DataFrame aktualisieren
    for i in range(9):
        df.iloc[spieler_index, start_col_idx + i] = neue_werte[i]
    
    # Zurück in Google Sheets schreiben
    conn.update(spreadsheet=URL, data=df)
    st.success(f"Daten für {auswahl_name} im {auswahl_deck} wurden gespeichert!")

st.divider()
st.info("Tipp: Die Tausch-Vorschläge berechnet der Chef am Wochenende über den geschützten Bereich.")
