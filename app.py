import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang - Finaler Fix", layout="wide")
st.title("🛡️ The Gang: Präzisions-Tausch")

SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # Wir laden die Tabelle komplett ohne Header-Logik
    df = pd.read_csv(DATA_URL, header=None)
    
    gebot = []
    bedarf = []

    # Wir scannen exakt ab Zeile 5 (Index 4 in Python)
    # Das ist die Zeile, in der 'Troy' steht
    for idx in range(4, len(df)):
        row = df.iloc[idx]
        spieler = str(row.iloc[0]).strip()
        
        # Sicherheits-Check für den Namen
        if spieler.lower() in ["nan", "", "name", "unnamed: 0"]: continue

        # Wir gehen durch 15 Decks
        for d_nr in range(1, 16):
            # Start-Spalte: B=1, L=11, V=21...
            start_col = 1 + (d_nr - 1) * 10
            
            for k_idx in range(9):
                col_idx = start_col + k_idx
                if col_idx < len(row):
                    val = row.iloc[col_idx]
                    
                    # Nur verarbeiten, wenn es eine echte Zahl ist
                    try:
                        # Wir wandeln in Float und dann Int um, um Fehler zu vermeiden
                        anzahl = int(float(str(val).replace(',', '.')))
                        karte_label = f"D{d_nr}-K{k_idx+1}"
                        
                        # Johny-Schutz: Nur bei ECHTER Null ist Bedarf
                        if anzahl == 0:
                            bedarf.append({"an": spieler, "karte": karte_label})
                        elif anzahl >= 2:
                            gebot.append({"von": spieler, "karte": karte_label})
                    except:
                        # Wenn hier Text wie "K1" oder "Deck 1" steht, wird es ignoriert
                        continue

    # Matching: Jeder darf nur 1x geben und 1x nehmen
    final_deals = []
    hat_gegeben = set()
    hat_bekommen = set()

    for b in bedarf:
        if b["an"] in hat_bekommen: continue
        for g in gebot:
            if g["von"] in hat_gegeben: continue
            
            # Match finden (darf sich nicht selbst beschenken)
            if b["karte"] == g["karte"] and b["an"] != g["von"]:
                final_deals.append(f"✅ {g['von']} ➔ {b['an']} ({g['karte']})")
                hat_gegeben.add(g["von"])
                hat_bekommen.add(b["an"])
                break

    if final_deals:
        st.header(f"📋 {len(final_deals)} Korrekte Tausch-Vorschläge")
        # Sortierung nach Deck-Nummer für bessere Übersicht
        for deal in sorted(final_deals, key=lambda x: x.split('(')[1]):
            st.success(deal)
    else:
        st.warning("Keine eindeutigen Täusche gefunden. Bitte prüfe, ob die 0er und 2er korrekt eingetragen sind.")

except Exception as e:
    st.error(f"Fehler: {e}")
