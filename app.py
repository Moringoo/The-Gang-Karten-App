import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang - Präzisions-Scan", layout="wide")
st.title("🚀 The Gang: Alle Decks (Präzisions-Scan)")

SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_clean_val(val):
    try:
        if pd.isna(val) or str(val).strip() == "": return 0
        return int(float(str(val).strip()))
    except:
        return 0

try:
    # Wir laden die Tabelle ohne automatische Überschriften
    df = pd.read_csv(DATA_URL, header=None)
    
    gebot = []
    bedarf = []

    # Wir scannen alle Spieler ab Zeile 5 (Index 4) bis Zeile 24 (Paul)
    for idx in range(4, len(df)):
        row = df.iloc[idx]
        spieler = str(row.iloc[0]).strip()
        if spieler.lower() in ["nan", "", "name"]: continue

        # Wir gehen durch alle 15 Decks
        # Jedes Deck-Paket ist 10 Spalten breit (9 Karten + 1 Name)
        for d_nr in range(1, 16):
            # Start-Spalte berechnen: Deck 1 = 1 (B), Deck 2 = 11 (L), Deck 3 = 21 (V)
            start_col = 1 + (d_nr - 1) * 10
            
            for i in range(9): # Die 9 Karten pro Deck
                col_idx = start_col + i
                if col_idx < len(row):
                    anzahl = get_clean_val(row.iloc[col_idx])
                    label = f"Deck {d_nr}-K{i+1}"
                    
                    if anzahl >= 2:
                        gebot.append({"von": spieler, "karte": label})
                    elif anzahl == 0:
                        bedarf.append({"an": spieler, "karte": label})

    # Matching (Jeder Spieler darf nur 1x geben)
    final_deals = []
    hat_gegeben = set()
    hat_bekommen = set()

    for b in bedarf:
        if b["an"] in hat_bekommen: continue
        for g in gebot:
            if g["von"] in hat_gegeben: continue
            
            if b["karte"] == g["karte"] and b["an"] != g["von"]:
                final_deals.append(f"✅ {g['von']} ➔ {b['an']} ({g['karte']})")
                hat_gegeben.add(g["von"])
                hat_bekommen.add(b["an"])
                break

    if final_deals:
        st.header(f"📋 {len(final_deals)} Tausch-Vorschläge gefunden")
        # Sortiert anzeigen (Deck 1, dann Deck 2...)
        for deal in sorted(final_deals, key=lambda x: x.split('(')[1]):
            st.success(deal)
    else:
        st.warning("Keine Übereinstimmungen gefunden. Prüfe, ob in Deck 2 oder 3 irgendwo eine '2' und eine '0' bei der gleichen Karte stehen!")

except Exception as e:
    st.error(f"Fehler: {e}")
