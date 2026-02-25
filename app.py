import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang - 15 Deck Scan", layout="wide")
st.title("🏆 The Gang: Master-Tausch-Rechner (Alle Decks)")

SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

try:
    # Wir laden die Tabelle ab Zeile 5 (wo Troy steht)
    # header=None sorgt dafür, dass wir die Spalten stur als Zahlen (0, 1, 2...) ansprechen
    df = pd.read_csv(DATA_URL, header=None).iloc[4:]
    
    gebot = []
    bedarf = []

    for _, row in df.iterrows():
        spieler = str(row.iloc[0]).strip()
        if spieler.lower() in ["nan", "", "name", "unnamed"]: continue

        # Wir scannen Karten von Spalte 1 (B) bis 135 (Ende von Deck 15)
        for total_idx in range(1, 136):
            if total_idx < len(row):
                val = row.iloc[total_idx]
                
                # Nur verarbeiten, wenn das Feld nicht leer ist
                if pd.notna(val) and str(val).strip() != "":
                    try:
                        anzahl = int(float(str(val).strip()))
                        
                        # Berechnung: Welches Deck und welche Karte ist das?
                        deck_nr = (total_idx - 1) // 9 + 1
                        karte_nr = (total_idx - 1) % 9 + 1
                        label = f"Deck {deck_nr}-K{karte_nr}"
                        
                        if anzahl >= 2:
                            gebot.append({"von": spieler, "karte": label})
                        elif anzahl == 0:
                            # Bedarf nur, wenn wirklich eine 0 drinsteht
                            bedarf.append({"an": spieler, "karte": label})
                    except:
                        continue

    # Matching Logik
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
        st.header(f"📋 {len(final_deals)} Tausch-Vorschläge")
        # Sortiert nach Deck-Nummer anzeigen
        for deal in sorted(final_deals, key=lambda x: x.split('(')[1]):
            st.success(deal)
        
        st.divider()
        st.subheader("📲 WhatsApp Text")
        wa_text = "*Heutige Gang-Tauschliste:*\n\n" + "\n".join(final_deals)
        st.code(wa_text)
    else:
        st.info("Keine passenden Täusche gefunden. Stell sicher, dass Nullen für fehlende Karten eingetragen sind!")

except Exception as e:
    st.error(f"Fehler: {e}")
