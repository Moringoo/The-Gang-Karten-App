import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang: Deck Closer", layout="wide")
st.title("🛡️ The Gang: Zielgeraden-Scanner")

GID = "2025591169" 
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"

@st.cache_data(ttl=5)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    
    # 1. Decks identifizieren
    decks = {}
    for col in df.columns[1:]:
        d_name = col.split('-')[0]
        if d_name not in decks: decks[d_name] = []
        decks[d_name].append(col)

    gebot = []
    bedarf_mit_prio = []

    for _, row in df.iterrows():
        name = str(row.iloc[0]).strip()
        if name in ["nan", "None", ""]: continue
        
        for d_name, d_cols in decks.items():
            # Wie viele Karten hat der Spieler in diesem Deck (Zahl > 0)
            besitz_count = sum(1 for c in d_cols if pd.notna(row[c]) and int(float(str(row[c]).replace(',','.'))) > 0)
            
            for c in d_cols:
                try:
                    val = row[c]
                    if pd.isna(val): continue
                    anz = int(float(str(val).replace(',', '.')))
                    
                    if anz >= 2:
                        gebot.append({"spieler": name, "karte": c})
                    elif anz == 0:
                        # WICHTIG: Wir speichern JEDEN Bedarf, aber geben ihm den besitz_count mit
                        # damit wir später nach "kurz vor Ende" sortieren können.
                        bedarf_mit_prio.append({
                            "spieler": name, 
                            "karte": c, 
                            "fortschritt": besitz_count
                        })
                except: continue

    # STRATEGIE-SORTIERUNG: Wer 8 Karten hat (8/9), kommt ganz nach oben!
    # Danach 7/9, 6/9... wer nur 1 Karte hat, kommt ganz nach unten.
    bedarf_mit_prio = sorted(bedarf_mit_prio, key=lambda x: x['fortschritt'], reverse=True)

    def match_engine(dia_mode):
        matches = []
        sender_gesperrt = set() # Jeder verschickt nur 1 Karte
        
        for b in bedarf_mit_prio:
            ist_dia = "(D)" in b["karte"]
            if ist_dia != dia_mode: continue
            
            for g in gebot:
                # Prüfen: Sender noch frei? Nicht an sich selbst schicken? Karte identisch?
                if g["spieler"] not in sender_gesperrt and g["spieler"] != b["spieler"] and g["karte"] == b["karte"]:
                    
                    prio_info = f"🔥 **FINISHER!** ({b['fortschritt']}/9)" if b['fortschritt'] == 8 else f"({b['fortschritt']}/9)"
                    
                    matches.append(f"{prio_info} | **{g['spieler']}** ➔ **{b['spieler']}** ({g['karte']})")
                    
                    # Sender sperren, Empfänger bleibt offen für weitere Karten
                    sender_gesperrt.add(g["spieler"]) 
                    break # Nächsten Bedarf in der Prio-Liste prüfen
        return matches

    t1, t2 = st.tabs(["🌕 Gold-Abschlüsse", "💎 Diamant-Abschlüsse"])
    with t1:
        res_g = match_engine(False)
        for m in res_g: st.success(m)
            
    with t2:
        res_d = match_engine(True)
        for m in res_d: st.info(m)

except Exception as e:
    st.error(f"Fehler: {e}")
