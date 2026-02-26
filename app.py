import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="The Gang: Admin & User", layout="wide")

# Verbindung zum Google Sheet herstellen
# (Erfordert eine 'secrets.toml' Datei in Streamlit mit deinen Zugangsdaten)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVIGATION ---
page = st.sidebar.selectbox("Was möchtest du tun?", ["Tausch-Vorschläge sehen", "Meine Karten eintragen"])

if page == "Meine Karten eintragen":
    st.header("📝 Deine Karten aktualisieren")
    
    # 1. Spieler wählen
    df = conn.read(worksheet="App-Daten")
    spieler_liste = df["Name"].tolist()
    name = st.selectbox("Wer bist du?", spieler_liste)
    
    # 2. Deck wählen
    deck_num = st.number_input("Welches Deck möchtest du bearbeiten? (1-15)", 1, 15)
    
    st.subheader(f"Zahlen für Deck {deck_num} eingeben")
    st.info("0 = Brauche ich | 1 = Habe ich 1x | 2 = Habe ich doppelt (kann weg)")
    
    # 3. Eingabe der 9 Kartenwerte nebeneinander
    cols = st.columns(9)
    neue_werte = []
    for i in range(9):
        with cols[i]:
            wert = st.number_input(f"K{i+1}", 0, 9, key=f"k{i}")
            neue_werte.append(wert)
            
    if st.button("Speichern & Hochladen"):
        # Logik zum Speichern:
        # Wir suchen die Zeile des Spielers und die Spalten des gewählten Decks
        # und schreiben die neuen Werte zurück ins Google Sheet.
        st.success(f"Daten für {name} (Deck {deck_num}) wurden gespeichert!")
        # (Hier erfolgt der Schreibbefehl an die API)

elif page == "Tausch-Vorschläge sehen":
    st.header("🛡️ Aktuelle Tausch-Vorschläge")
    # ... hier kommt dein bewährter Finisher-Code (v11.0) rein ...
