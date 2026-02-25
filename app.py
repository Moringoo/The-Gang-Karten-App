import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="The Gang - Final Fix", layout="wide")
st.title("🏆 The Gang: Echtzeit-Tausch (Cache-Safe)")

# Wir hängen einen Zeitstempel an die URL, damit Google/Streamlit nicht schummeln können
SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&v={int(time.time())}"

try:
    # Wir laden die Daten OHNE Cache
    df = pd.read_csv(DATA_URL, header=None).iloc[4:]
    
    gebot = []
    bedarf = []

    for _, row in df.iterrows():
        spieler = str(row.iloc[0]).strip()
        if spieler.lower() in ["nan", "", "name"]: continue

        # SCAN-LOGIK: 9 Spalten pro Deck, Name nur in Spalte A
        for d_nr in range(1, 16):
            start_index = 1 + (d_nr - 1) * 9
            
            for k_nr in range(1, 10):
                current_col = start_index + k_nr - 1
                if current_col < len(row):
                    val = row.iloc[current_col]
                    try:
                        anzahl = int(float(str(val).strip()))
                        label = f"D{d_nr}-K{k_nr}"
                        
                        if anzahl >= 2:
                            gebot.append({"von": spieler, "karte": label})
                        elif anzahl == 0:
                            # Wir prüfen, ob der Spieler wirklich 0 hat
                            bedarf.append({"an": spieler, "karte": label})
                    except:
                        continue

    # Matching
    final_deals = []
    hat_gegeben = set()
    hat_bekommen = set()

    for b in bedarf:
        if b["an"] in hat_bekommen: continue
        for g in gebot:
            if g["von"] in hat_gegeben: continue
            if b["karte"] == g["karte"] and b["an"] != g["von"]:
                final_deals.append(f"🤝 {g['von']} gibt {g['karte']} an {b['an']}")
                hat_gegeben.add(g["von"])
                hat_bekommen.add(b["an"])
                break

    if final_deals:
        st.header(f"📋 {len(final_deals)} Aktuelle Tausch-Deals")
        for deal in sorted(final_deals):
            st.success(deal)
    else:
        st.info("Keine Tausche gefunden. Stelle sicher, dass in deiner Tabelle Nullen für fehlende Karten stehen!")

except Exception as e:
    st.error(f"Fehler: {e}")
