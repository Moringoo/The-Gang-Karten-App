import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang: Live-Terminal", layout="wide")

st.title("🛡️ The Gang: Live-Tausch & Diamanten-Check")

# Direkte Verbindung zu deinem Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid=0"

@st.cache_data(ttl=30)
def load_data():
    # Wir laden die gesamte Tabelle ab Zeile 5
    return pd.read_csv(SHEET_URL, header=None).iloc[4:]

try:
    df = load_data()
    
    tab1, tab2 = st.tabs(["🌕 Gold-Karten", "💎 Diamant-Karten"])

    def find_matches_extended(start_col, num_cards, prefix):
        gebot, bedarf = [], []
        
        # Geht alle Zeilen durch (bis 119 und weiter)
        for _, row in df.iterrows():
            spieler = str(row.iloc[0]).strip()
            if spieler in ["nan", ""]: continue
            
            # Scannt die Karten-Spalten für diesen Spieler
            for i in range(start_col, start_col + num_cards):
                try:
                    val = str(row.iloc[i]).strip()
                    if val in ["nan", ""]: continue
                    anzahl = int(float(val.replace(',', '.')))
                    
                    deck_nr = ((i - start_col) // 9) + 1
                    karte_nr = ((i - start_col) % 9) + 1
                    label = f"{prefix} D{deck_nr}-K{karte_nr}"
                    
                    if anzahl >= 2:
                        gebot.append({"name": spieler, "karte": label})
                    elif anzahl == 0:
                        bedarf.append({"name": spieler, "karte": label})
                except:
                    continue
        
        # Matching-Logik
        matches = []
        used = set()
        for b in bedarf:
            for g in gebot:
                if b["karte"] == g["karte"] and b["name"] != g["name"]:
                    match_id = f"{g['name']}-{b['name']}-{g['karte']}"
                    if match_id not in used:
                        matches.append(f"✅ **{g['name']}** ➔ **{b['name']}** ({g['karte']})")
                        used.add(match_id)
        return matches

    with tab1:
        # Scannt Gold-Karten (Decks 1-15, Spalte 1-135)
        results_gold = find_matches_extended(1, 135, "Gold")
        if results_gold:
            for m in results_gold: st.success(m)
        else:
            st.info("Keine Gold-Matches gefunden.")

    with tab2:
        # Scannt Diamant-Karten (Ab Spalte 136)
        results_dia = find_matches_extended(136, 100, "Diamant")
        if results_dia:
            for m in results_dia: st.info(m)
        else:
            st.warning("Keine Diamant-Matches. Prüfe, ob Diamanten ab Spalte 136 stehen!")

except Exception as e:
    st.error(f"Fehler: {e}")
