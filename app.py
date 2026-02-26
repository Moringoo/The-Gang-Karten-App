import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang: Kartell-Tausch", layout="wide")

st.title("🛡️ The Gang: Tauschbörse (1 Karte pro Person)")

# Verbindung zum Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid=0"

@st.cache_data(ttl=20)
def load_data():
    return pd.read_csv(SHEET_URL, header=None).iloc[4:]

try:
    df = load_data()
    
    # EINSTELLUNG: Ab welcher Spalte fangen die Diamanten an?
    # In Google Sheets: Spalte A=0, B=1, C=2... 
    # Wenn Deck 4 ab Spalte L (11) Diamanten hat, kannst du das hier anpassen.
    st.sidebar.header("Einstellungen")
    dia_start = st.sidebar.number_input("Diamanten starten ab Spalte:", value=11, help="Spalte A=0, B=1...")

    gebot, bedarf = [], []

    # Scan aller Zeilen (bis 119+)
    for _, row in df.iterrows():
        spieler = str(row.iloc[0]).strip()
        if spieler in ["nan", ""]: continue
        
        for i in range(1, len(row)):
            try:
                val = str(row.iloc[i]).strip()
                if val in ["nan", ""]: continue
                anzahl = int(float(val.replace(',', '.')))
                
                # Deck-Berechnung
                deck_nr = ((i - 1) // 10) + 1
                karte_nr = ((i - 1) % 10) + 1
                if karte_nr > 9: continue 
                
                # Diamant-Erkennung basierend auf deiner Eingabe
                prefix = "💎 Diamant" if i >= dia_start else "🌕 Gold"
                label = f"{prefix} D{deck_nr}-K{karte_nr}"
                
                if anzahl >= 2:
                    gebot.append({"name": spieler, "karte": label})
                elif anzahl == 0:
                    bedarf.append({"name": spieler, "karte": label})
            except: continue

    # Matching mit Sperre: Nur 1 Karte pro Spieler
    tab1, tab2 = st.tabs(["🌕 Gold-Tausch", "💎 Diamant-Tausch"])
    
    def get_fair_matches(all_bedarf, all_gebot, filter_word):
        matches = []
        beschaeftigte_spieler = set()
        
        # Nur Karten des jeweiligen Typs (Gold oder Diamant)
        filtered_bedarf = [b for b in all_bedarf if filter_word in b["karte"]]
        filtered_gebot = [g for g in all_gebot if filter_word in g["karte"]]

        for b in filtered_bedarf:
            if b["name"] in beschaeftigte_spieler: continue
            
            for g in filtered_gebot:
                if g["name"] in beschaeftigte_spieler: continue
                if b["name"] == g["name"]: continue
                
                if b["karte"] == g["karte"]:
                    matches.append(f"✅ **{g['name']}** ➔ **{b['name']}** ({g['karte']})")
                    # Beide Spieler für weitere Täusche sperren
                    beschaeftigte_spieler.add(g["name"])
                    beschaeftigte_spieler.add(b["name"])
                    break
        return matches

    with tab1:
        gold_deals = get_fair_matches(bedarf, gebot, "Gold")
        if gold_deals:
            for d in gold_deals: st.success(d)
        else: st.info("Keine Gold-Täusche möglich.")

    with tab2:
        # Hier werden jetzt gezielt die Diamanten gesucht
        dia_deals = get_fair_matches(bedarf, gebot, "Diamant")
        if dia_deals:
            for d in dia_deals: st.info(d)
        else:
            st.warning("Keine Diamant-Täusche gefunden. Pass die 'Start-Spalte' in der Sidebar an!")

except Exception as e:
    st.error(f"Fehler: {e}")
