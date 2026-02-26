import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang: Kartell-Börse", layout="wide")
st.title("🛡️ The Gang: Kartell-Börse (Fokus: 20 Spieler)")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid=0"

@st.cache_data(ttl=10)
def load_data():
    return pd.read_csv(SHEET_URL, header=None)

try:
    df_raw = load_data()
    spieler_daten = {}

    # Wir scannen alle Spaltenblöcke (A, L, V, AF...)
    # Blöcke starten alle 11 Spalten (1 Name, 9 Karten, 1 Leer)
    for block_start in range(0, len(df_raw.columns), 11):
        # Scan der 20 Spielerzeilen (ab Zeile 5 / Index 4)
        for row_idx in range(4, 25):
            if row_idx >= len(df_raw): break
            
            name = str(df_raw.iloc[row_idx, block_start]).strip()
            if name in ["nan", "", "None", "Name"]: continue
            
            if name not in spieler_daten:
                spieler_daten[name] = {}
            
            # Die 9 Karten nach dem Namen einsammeln
            for k_offset in range(1, 10):
                col_idx = block_start + k_offset
                if col_idx >= len(df_raw.columns): break
                
                # Deck-Name aus Kopfzeile extrahieren
                deck_label = ""
                for r in range(4):
                    v = str(df_raw.iloc[r, col_idx]).strip()
                    if "Deck" in v:
                        deck_label = v
                        break
                
                if not deck_label: continue # Falls kein Deck gefunden
                
                karte_label = str(df_raw.iloc[3, col_idx]).strip()
                full_card = f"{deck_label}-{karte_label}"
                
                try:
                    wert = str(df_raw.iloc[row_idx, col_idx]).strip()
                    if wert not in ["nan", ""]:
                        anzahl = int(float(wert.replace(',', '.')))
                        # Wir speichern den Wert (bzw. addieren, falls er doppelt auftaucht)
                        spieler_daten[name][full_card] = anzahl
                except: continue

    # Hier definieren wir, was als Diamant zählt (graue Felder)
    DIAMANT_LISTE = [
        "Deck 4-K6", "Deck 4-K7", "Deck 4-K8", "Deck 4-K9",
        "Deck 5-K9", "Deck 6-K8", "Deck 6-K9",
        "Deck 13-K8", "Deck 13-K9", "Deck 14-K8", "Deck 14-K9"
    ]

    gebot, bedarf = [], []
    for name, karten in spieler_daten.items():
        for k_name, anzahl in karten.items():
            if anzahl >= 2:
                gebot.append({"name": name, "karte": k_name})
            elif anzahl == 0:
                bedarf.append({"name": name, "karte": k_name})

    def match_engine(mode):
        matches = []
        used = set()
        for b in bedarf:
            is_dia = any(d in b["karte"] for d in DIAMANT_LISTE)
            if (mode == "dia" and not is_dia) or (mode == "gold" and is_dia): continue
            if b["name"] in used: continue
            
            for g in gebot:
                if g["name"] in used or g["name"] == b["name"]: continue
                if g["karte"] == b["karte"]:
                    matches.append(f"🤝 **{g['name']}** ➔ **{b['name']}** ({g['karte']})")
                    used.add(g["name"])
                    used.add(b["name"])
                    break
        return matches

    t1, t2 = st.tabs(["🌕 Gold-Deals", "💎 Diamant-Deals"])
    with t1:
        g_res = match_engine("gold")
        if g_res:
            for m in g_res: st.success(m)
        else: st.info("Keine Gold-Matches gefunden.")
    with t2:
        d_res = match_engine("dia")
        if d_res:
            for m in d_res: st.info(m)
        else: st.warning("Keine Diamant-Matches. Trag '0' und '2' in die grauen Felder ein!")

except Exception as e:
    st.error(f"Fehler im System: {e}")
