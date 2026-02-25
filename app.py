import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="The Gang - Karten Manager", layout="wide")
st.title("🃏 The Gang Karten-Verwaltung")

# Link zu deiner Tabelle
URL = "https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/edit?gid=0#gid=0"

# Verbindung zu Google Sheets herstellen
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Wir lesen jetzt einfach das ganze Blatt ohne feste Spaltenzahl
    df = conn.read(spreadsheet=URL) 
except Exception as e:
    st.error(f"Verbindung fehlgeschlagen: {e}")
    st.stop()

# Namen aus deiner Tabelle holen
if 'Name' in df.columns:
    namen_liste = df['Name'].dropna().unique().tolist()
else:
    st.error("Die Spalte 'Name' wurde in der Tabelle nicht gefunden!")
    st.stop()

# --- EINGABE-BEREICH ---
st.header("📝 Karten aktualisieren")
col_a, col_b = st.columns(2)

with col_a:
    auswahl_name = st.selectbox("Wähle deinen Namen:", namen_liste)
with col_b:
    auswahl_deck = st.selectbox("Wähle das Deck:", [f"Deck {i}" for i in range(1, 16)])

# Deck-Logik
deck_num = int(auswahl_deck.split()[1])
start_col_idx = 1 + (deck_num - 1) * 9

if start_col_idx + 8 < len(df.columns):
    st.write(f"### Einträge für {auswahl_deck}")
    neue_werte = []
    cols = st.columns(3)
    spieler_index = df[df['Name'] == auswahl_name].index[0]

    for i in range(9):
        spalten_name = df.columns[start_col_idx + i]
        aktueller_wert = df.iloc[spieler_index, start_col_idx + i]
        # Falls das Feld leer ist (NaN), machen wir eine 0 draus
        if pd.isna(aktueller_wert): aktueller_wert = 0
        
        with cols[i % 3]:
            wert = st.number_input(f"Slot {i+1} ({spalten_name})", min_value=0, value=int(aktueller_wert), key=f"input_{i}")
            neue_werte.append(wert)

    if st.button("💾 Speichern"):
        for i in range(9):
            df.iloc[spieler_index, start_col_idx + i] = neue_werte[i]
        conn.update(spreadsheet=URL, data=df)
        st.success(f"Daten für {auswahl_name} gespeichert!")
else:
    st.warning(f"Das {auswahl_deck} scheint in der Tabelle noch nicht angelegt zu sein (Spalten fehlen).")
