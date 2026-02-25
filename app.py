import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang - Final Fix", layout="wide")
st.title("🛡️ The Gang: Fehlerfreier Tausch-Rechner")

SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # Wir laden diesmal MIT Header ab Zeile 4 (wo K1, K2 steht)
    df = pd.read_csv(DATA_URL, header=3) 
    
    gebot = []
    bedarf = []

    # Wir gehen durch alle Spieler (Troy bis Paul)
    for idx, row in df.iterrows():
        spieler = str(row.iloc[0]).strip()
        # Abbruch wenn wir am Ende der Liste sind
        if spieler.lower() in ["nan", "", "name", "unnamed"]: continue
        
        # Scan durch 15 Decks
        for d_nr in range(1, 16):
            # Start-Spalte: Deck 1 = 1, Deck 2 = 11, Deck 3 = 21...
            start_idx = 1 + (d_nr - 1) * 10
            
            for k_idx in range(9):
                col = start_idx + k_idx
                if col < len(row):
                    val = row.iloc[col]
                    
                    # STRENGE PRÜFUNG:
                    # Nur wenn eine ECHTE 0 drinsteht, wird Bedarf angemeldet
                    # Nur wenn eine ECHTE Zahl >= 2 drinsteht, wird Gebot angemeldet
                    try:
                        anzahl = int(float(val))
                        karte_name = f"Deck {d_nr}-K{k_idx+1}"
                        
                        if anzahl >= 2:
                            gebot.append({"von": spieler, "karte": karte_name})
                        elif anzahl == 0:
                            # Wir prüfen hier nochmal, ob das Feld nicht einfach leer war
                            if pd.notna(val):
                                bedarf.append({"an": spieler, "karte": karte_name})
                    except:
                        continue # Text oder leere Felder ignorieren

    # Fair-Trade Matching (Jeder nur 1x geben)
    final_deals = []
    hat_gegeben = set()
    hat_bekommen = set()

    for b in bedarf:
        if b["an"] in hat_bekommen: continue
        for g in gebot:
            if g["von"] in hat_gegeben: continue
            
            if b["karte"] == g["karte"] and b["an"] != g["von"]:
                final_deals.append(f"✅ {g['von']} ➔ {b['an']} ({g['karte']})")
                hat_gegeben.add(g["von"])
                hat_bekommen.add(b["an"])
                break

    if final_deals:
        st.header(f"📋 Bestätigte Täusche ({len(final_deals)})")
        for deal in sorted(final_deals, key=lambda x: x.split('(')[1]):
            st.success(deal)
    else:
        st.warning("Keine sicheren Tausch-Paare gefunden. Bitte prüfe, ob die Nullen in der Tabelle richtig gesetzt sind.")

except Exception as e:
    st.error(f"Technischer Fehler: {e}")
