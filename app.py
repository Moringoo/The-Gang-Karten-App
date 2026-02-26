import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang: Strategy Mode", layout="wide")
st.title("🛡️ The Gang: Strategie-Scanner")

GID = "2025591169" 
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"

@st.cache_data(ttl=5)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    
    # 1. Wir organisieren die Spalten nach Decks (D1, D2...)
    decks = {}
    for col in df.columns[1:]:
        deck_name = col.split('-')[0] # Extrahiert "D1", "D2" etc.
        if deck_name not in decks:
            decks[deck_name] = []
        decks[deck_name].append(col)

    # 2. Wir analysieren den Fortschritt jedes Spielers pro Deck
    # Wer hat wie viele Karten in einem Deck?
    bedarf_mit_prio = []
    gebot = []

    for _, row in df.iterrows():
        name = str(row.iloc[0]).strip()
        if name in ["nan", "None", ""]: continue
        
        for d_name, d_cols in decks.items():
            # Wie viele Karten besitzt der Spieler in DIESEM Deck bereits? (Anzahl > 0)
            besitz_count = sum(1 for c in d_cols if pd.notna(row[c]) and int(float(str(row[c]).replace(',','.'))) > 0)
            
            for c in d_cols:
                try:
                    val = row[c]
                    if pd.isna(val): continue
                    anz = int(float(str(val).replace(',', '.')))
                    
                    if anz >= 2:
                        gebot.append({"spieler": name, "karte": c})
                    elif anz == 0:
                        # STRATEGIE: Nur wenn er schon mehr als 1 Karte im Deck hat, 
                        # oder wenn es keine andere Option gibt.
                        # Wir speichern den Fortschritt (besitz_count) als Priorität.
                        if besitz_count > 1:
                            bedarf_mit_prio.append({
                                "spieler": name, 
                                "karte": c, 
                                "prio": besitz_count # Höherer Wert = Fast fertig
                            })
                except: continue

    # Sortiere Bedarf: Höchste Priorität (fast fertige Decks) zuerst
    bedarf_mit_prio = sorted(bedarf_mit_prio, key=lambda x: x['prio'], reverse=True)

    def match_engine(dia_mode):
        matches = []
        benutzte = set()
        
        for b in bedarf_mit_prio:
            ist_dia = "(D)" in b["karte"]
            if ist_dia != dia_mode or b["spieler"] in benutzte: continue
            
            for g in gebot:
                if g["spieler"] in benutzte or g["spieler"] == b["spieler"]: continue
                if g["karte"] == b["karte"]:
                    prio_text = f"(Fortschritt: {b['prio']}/9)"
                    matches.append(f"🎯 **{g['spieler']}** ➔ **{b['spieler']}** | {g['karte']} {prio_text}")
                    benutzte.update([g["spieler"], b["spieler"]])
                    break
        return matches

    t1, t2 = st.tabs(["🌕 Gold-Abschluss", "💎 Diamant-Abschluss"])
    with t1:
        for m in match_engine(False): st.success(m)
    with t2:
        for m in match_engine(True): st.info(m)

except Exception as e:
    st.error(f"Fehler in der Strategie-Berechnung: {e}")
