import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang: Multi-Match", layout="wide")
st.title("🛡️ The Gang: Maximum Tausch-Power")

GID = "2025591169" 
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"

@st.cache_data(ttl=5)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    
    # 1. Decks organisieren
    decks = {}
    for col in df.columns[1:]:
        deck_name = col.split('-')[0]
        if deck_name not in decks: decks[deck_name] = []
        decks[deck_name].append(col)

    gebot = []
    bedarf_mit_prio = []

    for _, row in df.iterrows():
        name = str(row.iloc[0]).strip()
        if name in ["nan", "None", ""]: continue
        
        for d_name, d_cols in decks.items():
            # Wie viele Karten hat er in diesem Deck (Zahl > 0)
            besitz_count = sum(1 for c in d_cols if pd.notna(row[c]) and int(float(str(row[c]).replace(',','.'))) > 0)
            
            for c in d_cols:
                try:
                    val = row[c]
                    if pd.isna(val): continue
                    anz = int(float(str(val).replace(',', '.')))
                    
                    if anz >= 2:
                        gebot.append({"spieler": name, "karte": c})
                    elif anz == 0:
                        # Bedarf nur speichern, wenn Deck-Fortschritt > 1 (Schutz-Regel)
                        if besitz_count > 1:
                            bedarf_mit_prio.append({
                                "spieler": name, 
                                "karte": c, 
                                "prio": besitz_count
                            })
                except: continue

    # Sortieren: Fast fertige Decks zuerst
    bedarf_mit_prio = sorted(bedarf_mit_prio, key=lambda x: x['prio'], reverse=True)

    def match_engine(dia_mode):
        matches = []
        sender_gesperrt = set() # Nur wer GESENDET hat, wird für weiteres Senden gesperrt
        # Empfänger werden NICHT gesperrt -> können mehrere Karten bekommen
        
        for b in bedarf_mit_prio:
            ist_dia = "(D)" in b["karte"]
            if ist_dia != dia_mode: continue
            
            for g in gebot:
                # Regel 1: Sender darf noch nicht gesendet haben
                # Regel 2: Man schickt sich keine Karten selbst
                if g["spieler"] not in sender_gesperrt and g["spieler"] != b["spieler"]:
                    if g["karte"] == b["karte"]:
                        matches.append(f"📦 **{g['spieler']}** ➔ **{b['spieler']}** | {g['karte']} (Fortschritt: {b['prio']}/9)")
                        sender_gesperrt.add(g["spieler"]) # Sender ist für diesen Scan fertig
                        break # Nächsten Bedarf prüfen
        return matches

    t1, t2 = st.tabs(["🌕 Gold-Deals (Maximal)", "💎 Diamant-Deals (Maximal)"])
    with t1:
        res_g = match_engine(False)
        for m in res_g: st.success(m)
        if not res_g: st.info("Keine Gold-Matches.")
            
    with t2:
        res_d = match_engine(True)
        for m in res_d: st.info(m)
        if not res_d: st.warning("Keine Diamant-Matches.")

except Exception as e:
    st.error(f"Fehler: {e}")
