import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang - Fair Trade", layout="wide")
st.title("⚖️ The Gang: Fairer 1-Karten-Tausch")

SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    df = pd.read_csv(DATA_URL)
    st.header("📋 Deine finale Tausch-Liste für heute")
    
    decks = {"Deck 1": 1, "Deck 2": 11, "Deck 3": 21}
    gebot = []
    bedarf = []

    for d_name, start_col in decks.items():
        for idx, row in df.iterrows():
            spieler = str(row.iloc[0]).strip()
            if pd.isna(row.iloc[0]) or spieler in ["Name", "nan", ""]: continue
            
            for i in range(9):
                try:
                    anzahl = int(float(row.iloc[start_col + i])) if pd.notna(row.iloc[start_col + i]) else 0
                except: anzahl = 0
                
                label = f"{d_name}-K{i+1}"
                if anzahl > 1:
                    gebot.append({"von": spieler, "karte": label})
                elif anzahl == 0:
                    bedarf.append({"an": spieler, "karte": label})

    # Die faire Logik: Jeder darf nur 1x geben und 1x nehmen
    final_deals = []
    hat_gegeben = set()
    hat_bekommen = set()

    for b in bedarf:
        if b["an"] in hat_bekommen: continue
        for g in gebot:
            if g["von"] in hat_gegeben: continue
            
            # Wenn Karte passt und beide noch "frei" sind
            if b["karte"] == g["karte"] and b["an"] != g["von"]:
                final_deals.append(f"🤝 **{g['von']}** gibt **{g['karte']}** an **{b['an']}**")
                hat_gegeben.add(g["von"])
                hat_bekommen.add(b["an"])
                break # Nächster Bedarfsfall

    if final_deals:
        for deal in final_deals:
            st.success(deal)
        st.info(f"Insgesamt {len(final_deals)} faire Täusche gefunden.")
    else:
        st.warning("Keine passenden Tausch-Paare gefunden, bei denen jeder nur eine Karte bewegt.")

except Exception as e:
    st.error(f"Fehler: {e}")
