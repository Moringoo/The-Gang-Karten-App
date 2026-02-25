import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd 

# --- KONFIGURATION ---
st.set_page_config(page_title="The Gang - Karten Manager", layout="wide")
st.title("🃏 The Gang Karten-Verwaltung")

URL = "https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/edit?gid=0#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Wir lesen das erste Tabellenblatt
    df = conn.read(spreadsheet=URL)
    
    # Wir räumen die Spaltennamen auf (Leerzeichen weg, alles Kleinbuchstaben zum Vergleich)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Suche nach einer Spalte, die "Name" enthält
    name_col = next((c for c in df.columns if c.lower() == "name"), None)

    if name_col:
        namen_liste = df[name_col].dropna().unique().tolist()
        
        st.header("📝 Karten aktualisieren")
        col_a, col_b = st.columns(2)
        with col_a:
            auswahl_name = st.selectbox("Wähle deinen Namen:", namen_liste)
        with col_b:
            auswahl_deck = st.selectbox("Wähle das Deck:", [f"Deck {i}" for i in range(1, 16)])

        # Den Spieler-Index finden
        spieler_index = df[df[name_col] == auswahl_name].index[0]
        
        # Einfache Anzeige der ersten verfügbaren Slots
        st.write(f"### Karten für {auswahl_name}")
        st.info("Hier kannst du gleich deine Karten eintragen, sobald die Tabelle geladen ist.")
        
    else:
        st.error("Konnte die Spalte 'Name' nicht finden. Bitte prüfe, ob in Zelle A1 deiner Google Tabelle 'Name' steht.")
        st.write("Verfügbare Spalten in deiner Tabelle:", list(df.columns))

except Exception as e:
    st.error(f"Fehler beim Laden: {e}")
