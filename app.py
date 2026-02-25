import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang - 15 Deck Scan", layout="wide")
st.title("🚀 The Gang: Full Analysis (Alle 15 Decks)")

SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_clean_val(val):
    try:
        return int(float(val)) if pd.notna(val) else 0
    except:
        return 0

try:
    df = pd.read_csv(DATA_URL)
    st.info("📊 Analysiere gerade alle 15 Decks für alle 20+ Spieler...")

    gebot = []
    bedarf = []

    # Dynamische Berechnung für alle 15 Decks
    # Deck 1 startet bei Index 1, Deck 2 bei 11, Deck 3 bei 21...
    for d_nr in range(1, 16):
        start_col = 1 + (d_nr - 1) * 10
        
        for idx, row in df.iterrows():
            spieler = str(row.iloc[0]).strip()
            # Validierung des Spielernamens
            if spieler.lower() in ["name", "nan", "", "unnamed: 0"]: continue
            
            # Die 9 Karten-Slots pro Deck prüfen
            for i in range(9):
                col_idx = start_col + i
                if col_idx >= len(row): continue
                
                anzahl = get_clean_val(row.iloc[col_idx])
                karte_label = f"D{d_nr}-K{i+1}"
                
                if anzahl >= 2:
                    gebot.append({"von": spieler, "karte": karte_label})
                elif anzahl == 0:
                    bedarf.append({"an": spieler, "karte": karte_label})

    # Fairer Abgleich: Jeder Spieler darf insgesamt nur 1x geben (heutige Regel)
    final_deals = []
    geber_belegt = set()
    nehmer_belegt = set()

    # Wir mischen die Bedarfe, damit nicht nur Deck 1 zuerst bedient wird
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
        st.header(f"📋 Top {len(final_deals)} Tausch-Vorschläge")
        whatsapp_text = "*The Gang - Alle Decks Tauschliste:*\n\n" + "\n".join(final_deals)
        
        for deal in final_deals:
            st.success(deal)
            
        st.divider()
        st.subheader("📲 WhatsApp Export")
        st.code(whatsapp_text)
    else:
        st.warning("Keine Matches über alle 15 Decks gefunden. Haben alle Spieler ihre Daten eingetragen?")

except Exception as e:
    st.error(f"Fehler beim Groß-Scan: {e}")
