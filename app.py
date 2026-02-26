import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang: 20-Spieler-Scan", layout="wide")
st.title("🛡️ The Gang: Kartell-Börse (Fokus: 20 Spieler)")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid=0"

@st.cache_data(ttl=10)
def load_data():
    return pd.read_csv(SHEET_URL, header=None)

try:
    df_raw = load_data()
    
    # Hier speichern wir ALLES für jeden der 20 Spieler
    # Struktur: { "Troy": {"Deck 1-K1": 2, "Deck 4-K6": 0}, "Mogli": ... }
    spieler_daten = {}

    # Wir scannen die Blöcke (Jeder Block startet mit einer Namens-Spalte)
    # Blöcke starten bei Spalte 0 (A), 11 (L), 21 (V), 31 (AF) usw.
    namens_spalten = [i for i in range(0, len(df_raw.columns), 10 if i == 0 else 10)] 
    
    for start_col in range(0, len(df_raw.columns), 10):
        # In dieser Spalte stehen die Namen für diesen Block
        for row_idx in range(4, len(df_raw)):
            name = str(df_raw.iloc[row_idx, start_col]).strip()
            if name in ["nan", "", "None"] or "Deck" in name: continue
            
            if name not in spieler_daten:
                spieler_daten[name] = {}
            
            # Jetzt die 9 Karten-Spalten nach dem Namen scannen
            for k_offset in range(1, 10):
                col_idx = start_col + k_offset
                if col_idx >= len(df_raw.columns): break
                
                # Deck-Name finden (steht in Zeile 1-3)
                deck_label = ""
                for r in range(3):
                    val = str(df_raw.iloc[r, col_idx]).strip()
                    if "Deck" in val:
                        deck_label = val
                        break
                
                # Falls Deck-Label leer, nehmen wir das von der Spalte davor
                if deck_label == "":
                    # Suche links nach dem nächsten Deck-Namen
                    for b in range(col_idx, 0, -1):
                        for r in range(3):
                            check_v = str(df_raw.iloc[r, b]).strip()
                            if "Deck" in check_v:
                                deck_label = check_v
                                break
                        if deck_label != "": break

                karte_label = str(df_raw.iloc[3, col_idx]).strip()
                
                try:
                    wert_raw = str(df_raw.iloc[row_idx, col_idx]).strip()
                    if wert_raw not in ["nan", ""]:
                        anzahl = int(float(wert_raw.replace(',', '.')))
                        full_key = f"{deck_label}-{karte_label}"
                        spieler_daten[name][full_key] = anzahl
                except: continue

    # Matching Logik
    gebot, bedarf = [], []
    # Liste der grauen Diamant-Karten (bitte ergänzen!)
    DIAMANT_LISTE = ["Deck 4-K6", "Deck 4-K7", "Deck 4-K8", "Deck 4-K9", "Deck 5-K9", "Deck 6-K8", "Deck 6-K9"]

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
        for m in match_engine("gold"): st.success(m)
    with t2:
        d_res = match_engine("dia")
        if d_res:
            for m in d_res: st.info(m)
        else: st.warning("Keine Diamant-Matches. Check die 'DIAMANT_LISTE' im Code!")

except Exception as e:
    st.error(f"Fehler: {e}")
