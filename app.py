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

    # Wir definieren die Spalten, in denen die Namen stehen (A, L, V, AF, AP, AZ, BJ, BT, CD, CN, CX)
    # Das sind die Spalten 0, 11, 21, 31, 41, 51, 61, 71, 81, 91, 101...
    namens_spalten_indices = [idx for idx in range(0, len(df_raw.columns), 10 if idx == 0 else 10)]

    for col_idx in range(len(df_raw.columns)):
        # Überspringe Spalten, die Namen enthalten
        if col_idx % 10 == 0: continue
        
        # Finde den zugehörigen Namen aus der Namensspalte links von diesem Block
        start_name_col = (col_idx // 10) * 10
        
        # Deck-Label aus den ersten 3 Zeilen suchen
        deck_label = ""
        for r in range(3):
            val = str(df_raw.iloc[r, col_idx]).strip()
            if "Deck" in val:
                deck_label = val
                break
        
        # Falls Deck-Label in der Spalte fehlt, nimm das von links (für K2-K9)
        if not deck_label:
            for back in range(col_idx, start_name_col, -1):
                for r in range(3):
                    check_v = str(df_raw.iloc[r, back]).strip()
                    if "Deck" in check_v:
                        deck_label = check_v
                        break
                if deck_label: break

        karte_label = str(df_raw.iloc[3, col_idx]).strip()
        full_card_key = f"{deck_label}-{karte_label}"

        # Jetzt für jeden der 20 Spieler die Zahl in dieser Spalte holen
        for row_idx in range(4, 25): # Scannt die ersten 20 Spielerzeilen
            name = str(df_raw.iloc[row_idx, start_name_col]).strip()
            if name in ["nan", "", "None", "Name"]: continue
            
            if name not in spieler_daten: spieler_daten[name] = {}
            
            try:
                wert_raw = str(df_raw.iloc[row_idx, col_idx]).strip()
                if wert_raw not in ["nan", ""]:
                    anzahl = int(float(wert_raw.replace(',', '.')))
                    spieler_daten[name][full_card_key] = anzahl
            except: continue

    # Graue Karten (Diamanten) basierend auf deinen Screenshots
    DIAMANT_LISTE = [
        "Deck 4-K6", "Deck 4-K7", "Deck 4-K8", "Deck 4-K9",
        "Deck 5-K9", "Deck 6-K8", "Deck 6-K9",
        "Deck 13-K8", "Deck 13-K9", "Deck 14-K8", "Deck 14-K9" # Beispielhaft erweitert
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
        for m in match_engine("gold"): st.success(m)
    with t2:
        d_res = match_engine("dia")
        if d_res:
            for m in d_res: st.info(m)
        else: st.warning("Keine Diamant-Matches gefunden.")

except Exception as e:
    st.error(f"Fehler: {e}")
