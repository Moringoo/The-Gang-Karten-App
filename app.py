import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang - Blitz Tausch", layout="wide")
st.title("⚡ The Gang: Gold-Tausch-Rechner")

SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # Daten laden und Spalten aufräumen
    df = pd.read_csv(DATA_URL)
    
    deck_wahl = st.selectbox("Für welches Deck brauchst du Vorschläge?", [1, 2, 3])
    
    # Startspalte für das Deck finden (Deck 1=Spalte 2, Deck 2=Spalte 12 etc. laut deiner Tabelle)
    # Spalte A=Name, B-J=Deck 1, K=Name, L-T=Deck 2...
    if deck_wahl == 1: start_col = 1
    elif deck_wahl == 2: start_col = 11
    else: start_col = 21

    st.header(f"🔍 Tausch-Vorschläge für Deck {deck_wahl}")
    
    gebot = []
    bedarf = []
    
    # Wer hat was doppelt (>1) und wer braucht was (0)?
    for idx, row in df.iterrows():
        spieler = row.iloc[0]
        if pd.isna(spieler): continue
        
        for i in range(9):
            anzahl = row.iloc[start_col + i]
            # Wir behandeln alle als "Gold", da sie im Spiel wertvoll sind
            karte_nr = i + 1
            if anzahl > 1:
                gebot.append({"Spieler": spieler, "Karte": f"K{karte_nr}", "Überschuss": int(anzahl-1)})
            elif anzahl == 0:
                bedarf.append({"Spieler": spieler, "Karte": f"K{karte_nr}"})

    # Abgleich
    vorschlaege = []
    for b in bedarf:
        for g in gebot:
            if b["Karte"] == g["Karte"]:
                vorschlaege.append(f"✅ **{g['Spieler']}** hat **{b['Karte']}** übrig → **{b['Spieler']}** braucht sie!")

    if vorschlaege:
        for v in vorschlaege:
            st.write(v)
    else:
        st.warning("Keine direkten Matches gefunden. Prüfe, ob alle Kartenmengen stimmen!")

except Exception as e:
    st.error(f"Fehler: {e}. Prüfe die Tabelle!")
