import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang - TOTAL SCAN", layout="wide")
st.title("⚡ The Gang: Alle Decks Tausch-Scan")

SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(DATA_URL)
    st.header("🚀 Sofort-Vorschläge (Alle Decks)")
    
    # Definition der Decks basierend auf deiner Tabelle (Spalten B-J, L-T, V-AD)
    decks = {
        "Deck 1": 1,
        "Deck 2": 11,
        "Deck 3": 21
    }

    gebot = []
    bedarf = []

    # Wir scannen alle 3 Decks in einem Rutsch
    for d_name, start_col in decks.items():
        for idx, row in df.iterrows():
            spieler = str(row.iloc[0]).strip()
            if pd.isna(row.iloc[0]) or spieler == "Name" or spieler == "nan": continue
            
            for i in range(9):
                raw_val = row.iloc[start_col + i]
                # Fehlervermeidung: Nur Zahlen verarbeiten
                try:
                    anzahl = int(float(raw_val)) if pd.notna(raw_val) else 0
                except:
                    anzahl = 0
                
                karte_label = f"{d_name} - K{i+1}"
                if anzahl > 1:
                    gebot.append({"Spieler": spieler, "Karte": karte_label})
                elif anzahl == 0:
                    bedarf.append({"Spieler": spieler, "Karte": karte_label})

    # Abgleich aller Decks
    vorschlaege = []
    for b in bedarf:
        for g in gebot:
            if b["Karte"] == g["Karte"]:
                vorschlaege.append(f"🔥 **{g['Spieler']}** kann **{b['Karte']}** an **{b['Spieler']}** geben.")

    if vorschlaege:
        # Dubletten entfernen und anzeigen
        for v in sorted(list(set(vorschlaege))):
            st.write(v)
    else:
        st.info("Keine Tauschmöglichkeiten gefunden. Überprüfe, ob die 0er und 2er in der Tabelle richtig eingetragen sind!")

except Exception as e:
    st.error(f"Fehler beim Schnell-Scan: {e}")
