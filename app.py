import streamlit as st
import pandas as pd

# 1. Konfiguration
st.set_page_config(page_title="The Gang: Tauschbörse", layout="wide")
st.title("🛡️ The Gang: Tausch-Zentrale")

# WICHTIG: Prüfe, ob die GID noch stimmt (die Zahl am Ende der URL im Blatt 'App-Daten')
GID = "2025591169" 
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"

@st.cache_data(ttl=5) # Daten aktualisieren sich alle 5 Sekunden
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    
    # Listen für Tauschangebote und Wünsche
    gebot = []
    bedarf = []

    # Wir gehen durch jeden Spieler (Zeile 2 bis 21)
    for index, row in df.iterrows():
        spieler_name = str(row.iloc[0]).strip()
        if spieler_name in ["nan", "None", ""]: continue
        
        # Wir gehen durch jede Karte (Spalte B bis EF)
        for spalten_name in df.columns[1:]:
            try:
                wert = row[spalten_name]
                if pd.isna(wert): continue
                
                # Zahl sauber umwandeln
                anzahl = int(float(str(wert).replace(',', '.')))
                
                if anzahl >= 2:
                    gebot.append({"spieler": spieler_name, "karte": spalten_name})
                elif anzahl == 0:
                    bedarf.append({"spieler": spieler_name, "karte": spalten_name})
            except:
                continue

    # Matching-Logik: Wer braucht was, das ein anderer doppelt hat?
    def match_engine(diamant_modus):
        matches = []
        benutzte_spieler = set()
        
        for b in bedarf:
            ist_diamant = "(D)" in b["karte"]
            if ist_diamant != diamant_modus: continue
            if b["spieler"] in benutzte_spieler: continue
            
            for g in gebot:
                if g["spieler"] in benutzte_spieler or g["spieler"] == b["spieler"]: continue
                if g["karte"] == b["karte"]:
                    matches.append(f"🤝 **{g['spieler']}** gibt an **{b['spieler']}** ➔ {g['karte']}")
                    benutzte_spieler.add(g["spieler"])
                    benutzte_spieler.add(b["spieler"])
                    break
        return matches

    # Anzeige in Tabs
    tab1, tab2 = st.tabs(["🌕 Gold-Karten", "💎 Diamant-Karten"])
    
    with tab1:
        gold_ergebnisse = match_engine(False)
        if gold_ergebnisse:
            for m in gold_ergebnisse: st.success(m)
        else:
            st.info("Keine Gold-Matches gefunden.")
            
    with tab2:
        dia_ergebnisse = match_engine(True)
        if dia_ergebnisse:
            for m in dia_ergebnisse: st.info(m)
        else:
            st.warning("Keine Diamant-Matches gefunden. Prüfe die (D) Markierungen im Sheet!")

except Exception as e:
    st.error(f"Konnte Daten nicht laden. Fehler: {e}")
