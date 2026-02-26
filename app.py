import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang: Priority Scan", layout="wide")
st.title("🛡️ The Gang: Tausch-Zentrale")

GID = "2025591169" 
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"

@st.cache_data(ttl=5)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    
    # REGEL: Decks mit den meisten Karten zuerst (Deck 15 -> Deck 1)
    # Wir drehen die Spalten-Reihenfolge um, damit die App von hinten nach vorne sucht
    cols = list(df.columns)
    karten_spalten = cols[1:] # Alles außer Name
    karten_spalten_priorisiert = karten_spalten[::-1] # Liste umdrehen

    gebot = []
    bedarf = []

    for _, row in df.iterrows():
        name = str(row.iloc[0]).strip()
        if name in ["nan", "None", ""]: continue
        
        # Wir scannen in der priorisierten Reihenfolge
        for col in karten_spalten_priorisiert:
            try:
                val = row[col]
                if pd.isna(val): continue
                anz = int(float(str(val).replace(',', '.')))
                
                if anz >= 2:
                    gebot.append({"spieler": name, "karte": col})
                elif anz == 0:
                    bedarf.append({"spieler": name, "karte": col})
            except: continue

    def match_engine(dia_mode):
        matches = []
        # REGEL: Jeder darf nur eine Karte versenden/empfangen pro Scan
        benutzte_leute = set()
        
        # Da gebot und bedarf schon nach Decks sortiert sind (15 bis 1),
        # findet die Schleife automatisch zuerst die hohen Decks.
        for b in bedarf:
            ist_dia = "(D)" in b["karte"]
            if ist_dia != dia_mode: continue
            if b["spieler"] in benutzte_leute: continue
            
            for g in gebot:
                if g["spieler"] in benutzte_leute or g["spieler"] == b["spieler"]: continue
                if g["karte"] == b["karte"]:
                    # Treffer!
                    matches.append(f"🤝 **{g['spieler']}** ➔ **{b['spieler']}** ({g['karte']})")
                    # REGEL: Beide für weitere Matches in diesem Durchgang sperren
                    benutzte_leute.add(g["spieler"])
                    benutzte_leute.add(b["spieler"])
                    break
        return matches

    tab1, tab2 = st.tabs(["🌕 Gold (Prio: Hohe Decks zuerst)", "💎 Diamant (Prio: Hohe Decks zuerst)"])
    
    with tab1:
        res_g = match_engine(False)
        for m in res_g: st.success(m)
        if not res_g: st.info("Keine Gold-Matches.")
            
    with tab2:
        res_d = match_engine(True)
        for m in res_d: st.info(m)
        if not res_d: st.warning("Keine Diamant-Matches.")

except Exception as e:
    st.error(f"Fehler: {e}")
