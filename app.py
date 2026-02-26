import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang: Kartell-Scanner", layout="wide")

st.title("🛡️ The Gang: Kartell-Scanner (Alle Decks)")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid=0"

@st.cache_data(ttl=20)
def load_data():
    # Lädt alles ab Zeile 5 (Spieler Troy)
    return pd.read_csv(SHEET_URL, header=None).iloc[4:]

def is_diamond(deck_nr, karte_nr):
    """
    Diese Funktion markiert genau die Karten als Diamant, 
    die in deinen Screenshots grau hinterlegt sind.
    """
    # Beispiel-Logik basierend auf Screenshot Deck 4-6:
    if deck_nr == 4 and karte_nr >= 6: return True
    if deck_nr == 5 and karte_nr == 9: return True
    if deck_nr == 6 and karte_nr >= 8: return True
    # Decks 1-3 haben laut Screenshot keine grauen Felder
    if deck_nr <= 3: return False
    # Standardmäßig: Höhere Decks haben oft Diamanten am Ende
    if deck_nr >= 7 and karte_nr >= 7: return True
    return False

try:
    df = load_data()
    st.caption(f"Scanner aktiv für {len(df)} Mitglieder (bis Zeile 119+)")

    gebot, bedarf = [], []

    # Wir scannen alle Spalten (B bis AD und weiter)
    for _, row in df.iterrows():
        spieler = str(row.iloc[0]).strip()
        if spieler in ["nan", ""]: continue
        
        for i in range(1, len(row)):
            try:
                val = str(row.iloc[i]).strip()
                if val in ["nan", ""]: continue
                anzahl = int(float(val.replace(',', '.')))
                
                # Berechnung welches Deck und welche Karte (1-9)
                # Deine Tabelle hat Lücken zwischen den 3er Blöcken, 
                # der Code überspringt diese dank 'try-except'
                deck_nr = ((i - 1) // 10) + 1 # Berücksichtigt die Leerspalten grob
                karte_nr = ((i - 1) % 10) + 1
                if karte_nr > 9: continue # Leerspalte überspringen
                
                prefix = "💎 Diamant" if is_diamond(deck_nr, karte_nr) else "🌕 Gold"
                label = f"{prefix} D{deck_nr}-K{karte_nr}"
                
                if anzahl >= 2:
                    gebot.append({"name": spieler, "karte": label})
                elif anzahl == 0:
                    bedarf.append({"name": spieler, "karte": label})
            except: continue

    # Matching & Anzeige
    tab1, tab2 = st.tabs(["🌕 Gold-Deals", "💎 Diamant-Deals"])
    
    matches = []
    used = set()
    for b in bedarf:
        for g in gebot:
            if b["karte"] == g["karte"] and b["name"] != g["name"]:
                m_id = f"{g['name']}-{b['name']}-{g['karte']}"
                if m_id not in used:
                    matches.append(f"🤝 **{g['name']}** ➔ **{b['name']}** ({g['karte']})")
                    used.add(m_id)

    with tab1:
        g_matches = [m for m in matches if "Gold" in m]
        if g_matches:
            for m in g_matches: st.success(m)
        else: st.info("Keine Gold-Täusche.")

    with tab2:
        d_matches = [m for m in matches if "Diamant" in m]
        if d_matches:
            for m in d_matches: st.info(m)
        else: st.warning("Keine Diamant-Täusche gefunden. Prüfe die grauen Felder im Sheet!")

except Exception as e:
    st.error(f"Scan-Fehler: {e}")
