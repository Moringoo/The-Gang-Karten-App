import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang - 15 Decks", layout="wide")
st.title("🚀 The Gang: Alle 15 Decks Analyse")

SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_clean_val(val):
    try:
        if pd.isna(val): return 0
        return int(float(str(val).strip()))
    except:
        return 0

try:
    df = pd.read_csv(DATA_URL)
    
    gebot = []
    bedarf = []

    # KORREKTUR: Jedes Deck in deiner Tabelle belegt 11 Spalten (1 Name + 9 Karten + 1 Name als Trenner)
    # Deck 1: Start Spalte 1 (B)
    # Deck 2: Start Spalte 11 (L)
    # Deck 3: Start Spalte 21 (V)
    for d_nr in range(1, 16):
        start_col = 1 + (d_nr - 1) * 10
        # Wir korrigieren den Offset, da nach Deck 1 immer eine Spalte 'Name' dazukommt
        # Deine Tabelle: B-J (D1), L-T (D2), V-AD (D3)
        actual_start = 1 + (d_nr - 1) * 10 
        
        for idx, row in df.iterrows():
            spieler = str(row.iloc[0]).strip()
            if spieler.lower() in ["name", "nan", "", "unnamed: 0"]: continue
            
            for i in range(9):
                col_idx = actual_start + i
                if col_idx < len(row):
                    anzahl = get_clean_val(row.iloc[col_idx])
                    label = f"D{d_nr}-K{i+1}"
                    if anzahl >= 2:
                        gebot.append({"von": spieler, "karte": label})
                    elif anzahl == 0:
                        bedarf.append({"an": spieler, "karte": label})

    # Matching: Jeder darf nur 1x geben
    final_deals = []
    geber_belegt = set()
    nehmer_belegt = set()

    # Wir sortieren nach Decks, damit wir sehen ob D2/D3 auftauchen
    for b in bedarf:
        if b["an"] in nehmer_belegt: continue
        for g in gebot:
            if g["von"] in geber_belegt: continue
            if b["karte"] == g["karte"] and b["an"] != g["von"]:
                final_deals.append(f"✅ {g['von']} ➔ {b['an']} ({g['karte']})")
                geber_belegt.add(g["von"])
                nehmer_belegt.add(b["an"])
                break

    if final_deals:
        st.header(f"📋 Gefundene Täusche ({len(final_deals)})")
        for deal in sorted(final_deals): # Sortiert nach Namen oder Deck
            st.success(deal)
    else:
        st.warning("Keine Täusche gefunden. Prüfe, ob in der Tabelle bei Deck 2 & 3 auch Nullen und Zweier stehen!")

except Exception as e:
    st.error(f"Fehler: {e}")
