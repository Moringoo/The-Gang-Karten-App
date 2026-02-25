import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang - Fixed", layout="wide")
st.title("🏆 The Gang: Master-Tausch-Rechner")

SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # Wir laden die Tabelle und ignorieren die ersten 4 Zeilen (Header)
    df = pd.read_csv(DATA_URL, header=None).iloc[4:]
    
    gebot = []
    bedarf = []

    # Wir definieren die Decks hart: Deck 1 = Spalte 1-9, Deck 2 = Spalte 10-18...
    for _, row in df.iterrows():
        spieler = str(row.iloc[0]).strip()
        if spieler.lower() in ["nan", "", "name"]: continue

        # Wir gehen durch 15 Decks
        for d_nr in range(1, 16):
            # Da keine "Name"-Spalten mehr da sind, liegen die Karten so:
            # Deck 1: Index 1 bis 9
            # Deck 2: Index 10 bis 18
            # Deck 3: Index 19 bis 27
            start_index = 1 + (d_nr - 1) * 9
            
            for k_nr in range(1, 10):
                current_col = start_index + k_nr - 1
                if current_col < len(row):
                    val = row.iloc[current_col]
                    
                    # Nur wenn das Feld nicht leer ist und eine Zahl enthält
                    try:
                        anzahl = int(float(str(val).strip()))
                        label = f"Deck {d_nr}-K{k_nr}"
                        
                        if anzahl >= 2:
                            gebot.append({"von": spieler, "karte": label})
                        elif anzahl == 0:
                            # EXTREM WICHTIG: Nur bei echter 0
                            bedarf.append({"an": spieler, "karte": label})
                    except:
                        continue

    # Matching (Jeder Spieler darf nur 1x geben)
    final_deals = []
    hat_gegeben = set()
    hat_bekommen = set()

    for b in bedarf:
        if b["an"] in hat_bekommen: continue
        for g in gebot:
            if g["von"] in hat_gegeben: continue
            
            # Match-Bedingung: Gleiche Karte, verschiedene Personen
            if b["karte"] == g["karte"] and b["an"] != g["von"]:
                final_deals.append(f"✅ {g['von']} ➔ {b['an']} ({g['karte']})")
                hat_gegeben.add(g["von"])
                hat_bekommen.add(b["an"])
                break

    if final_deals:
        st.header(f"📋 {len(final_deals)} Korrekte Tausch-Vorschläge")
        # Sortierung nach Deck und Karte
        for deal in sorted(final_deals, key=lambda x: x.split('(')[1]):
            st.success(deal)
    else:
        st.info("Keine Übereinstimmungen gefunden. Prüfe die 0er in der Tabelle!")

except Exception as e:
    st.error(f"Fehler im System: {e}")
