import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang: Komplett-Scan", layout="wide")

# Design
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stSuccess { background-color: #052e16; color: #4ade80; border: 1px solid #22c55e; }
    .stInfo { background-color: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ The Gang: Vollautomatischer Tausch-Scanner")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid=0"

@st.cache_data(ttl=20)
def load_data():
    # Wir laden alles ab Zeile 5 (wo Troy steht)
    return pd.read_csv(SHEET_URL, header=None).iloc[4:]

try:
    df = load_data()
    
    # Wir trennen Gold und Diamant nach deiner Struktur
    # Gold: Decks 1-15 (Spalte 1 bis 135)
    # Diamant: Ab Deck 16 (Spalte 136+)
    
    tab1, tab2 = st.tabs(["🌕 Alle Gold-Decks", "💎 Alle Diamant-Decks"])

    def find_matches_global(start_col, end_col, prefix):
        gebot, bedarf = [], []
        
        for _, row in df.iterrows():
            spieler = str(row.iloc[0]).strip()
            if spieler in ["nan", "", "None"]: continue
            
            # Wir prüfen den Bereich von start_col bis end_col
            # Falls die Tabelle kürzer ist als end_col, nehmen wir das tatsächliche Ende
            max_col = min(end_col, len(row) - 1)
            
            for i in range(start_col, max_col + 1):
                try:
                    val_raw = str(row.iloc[i]).strip()
                    if val_raw in ["nan", ""]: continue
                    
                    anzahl = int(float(val_raw.replace(',', '.')))
                    
                    # Berechnung Deck/Karte relativ zum Start des Bereichs
                    rel_idx = i - start_col
                    deck_nr = (rel_idx // 9) + 1
                    karte_nr = (rel_idx % 9) + 1
                    label = f"{prefix} D{deck_nr}-K{karte_nr}"
                    
                    if anzahl >= 2:
                        gebot.append({"name": spieler, "karte": label})
                    elif anzahl == 0:
                        bedarf.append({"name": spieler, "karte": label})
                except:
                    continue
        
        # Matching-Logik
        results = []
        used_pairs = set()
        
        for b in bedarf:
            for g in gebot:
                # Paar-Check: Selbe Karte, andere Spieler, noch nicht vermittelt
                pair_id = f"{g['name']}-{b['name']}-{g['karte']}"
                if b['karte'] == g['karte'] and b['name'] != g['name'] and pair_id not in used_pairs:
                    results.append(f"✅ **{g['name']}** ➔ **{b['name']}** ({g['karte']})")
                    used_pairs.add(pair_id)
        return results

    with tab1:
        # Scannt Spalte 1 bis 135 (Deck 1 bis 15)
        res_gold = find_matches_global(1, 135, "Gold")
        if res_gold:
            for r in res_gold: st.success(r)
        else:
            st.info("Keine Gold-Matches in allen Decks gefunden.")

    with tab2:
        # Scannt ab Spalte 136 bis zum bitteren Ende der Tabelle (Diamant)
        res_dia = find_matches_global(136, 500, "Diamant")
        if res_dia:
            for r in res_dia: st.info(r)
        else:
            st.warning("Keine Diamant-Matches gefunden. Prüfe die Spalten ab Deck 16!")

except Exception as e:
    st.error(f"Fehler: {e}")
