import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="The Gang - Karten Manager", layout="wide")
st.title("🃏 The Gang Karten-Verwaltung")

URL = "https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/edit?gid=0#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Wir laden die Daten und sagen ihm, dass er die erste Zeile als Namen nehmen soll
    df = conn.read(spreadsheet=URL, header=0)
    
    # Falls die Namen immer noch "Unnamed" sind, nehmen wir Spalte 0 manuell
    if "Unnamed: 0" in df.columns or df.columns[0].startswith("Unnamed"):
        # Wir geben den ersten Spalten feste Namen für die App
        neue_spalten = list(df.columns)
        neue_spalten[0] = "Name"
        df.columns = neue_spalten

    # Namen-Liste erstellen
    namen_liste = df["Name"].dropna().unique().tolist()
    
    if namen_liste:
        st.header("📝 Karten aktualisieren")
        col_a, col_b = st.columns(2)
        with col_a:
            auswahl_name = st.selectbox("Wähle deinen Namen:", namen_liste)
        with col_b:
            auswahl_deck = st.selectbox("Wähle das Deck:", [f"Deck {i}" for i in range(1, 16)])

        # Den Spieler-Index finden
        spieler_index = df[df["Name"] == auswahl_name].index[0]
        
        # Deck-Berechnung (9 Slots pro Deck)
        deck_num = int(auswahl_deck.split()[1])
        start_col = 1 + (deck_num - 1) * 9
        
        st.write(f"### {auswahl_deck} von {auswahl_name}")
        neue_werte = []
        cols = st.columns(3)
        
        for i in range(9):
            col_idx = start_col + i
            # Sicherheitscheck, ob die Spalte existiert
            if col_idx < len(df.columns):
                aktueller_wert = df.iloc[spieler_index, col_idx]
                if pd.isna(aktueller_wert): aktueller_wert = 0
                
                with cols[i % 3]:
                    wert = st.number_input(f"Karte {i+1}", min_value=0, value=int(aktueller_wert), key=f"k_{deck_num}_{i}")
                    neue_werte.append(wert)
            else:
                neue_werte.append(0)

        if st.button("💾 Speichern"):
            for i in range(9):
                col_idx = start_col + i
                if col_idx < len(df.columns):
                    df.iloc[spieler_index, col_idx] = neue_werte[i]
            
            conn.update(spreadsheet=URL, data=df)
            st.success("Erfolgreich in Google Sheets gespeichert!")
            st.balloons()

    else:
        st.error("Keine Namen in der ersten Spalte gefunden!")

except Exception as e:
    st.error(f"Verbindung steht, aber Fehler beim Verarbeiten: {e}")
