import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="The Gang - Finaler Neustart", layout="wide")
st.title("🛡️ The Gang: Intelligenter Karten-Scanner")

# Cache-Umgehung
SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&v={int(time.time())}"

try:
    # Wir laden die gesamte Tabelle
    full_df = pd.read_csv(DATA_URL, header=None)
    
    # Zeile 4 (Index 3) enthält deine "K1, K2..." Marker
    header_row = full_df.iloc[3]
    # Daten ab Zeile 5 (Index 4) sind die Spieler
    player_data = full_df.iloc[4:]

    gebot = []
    bedarf = []

    for _, row in player_data.iterrows():
        spieler = str(row.iloc[0]).strip()
        if spieler.lower() in ["nan", "", "name"]: continue

        # Wir prüfen JEDE Spalte einzeln
        current_deck = 1
        k_count_in_deck = 0

        for col_idx in range(1, len(row)):
            col_label = str(header_row.iloc[col_idx]).strip()
            
            # Nur wenn in der Kopfzeile "K" vorkommt, ist es eine Karte
            if "K" in col_label:
                k_count_in_deck += 1
                if k_count_in_deck > 9:
                    current_deck += 1
                    k_count_in_deck = 1
                
                val = row.iloc[col_idx]
                try:
                    anzahl = int(float(str(val).strip()))
                    karte_name = f"D{current_deck}-{col_label}"
                    
                    if anzahl >= 2:
                        gebot.append({"spieler": spieler, "karte": karte_name})
                    elif anzahl == 0:
                        # Bedarf nur bei ECHTER Null
                        bedarf.append({"spieler": spieler, "karte": karte_name})
                except:
                    continue

    # Matching-Logik (Wer kann wem helfen?)
    st.header("📋 Optimierte Tausch-Vorschläge")
    final_deals = []
    geber_belegt = set()
    nehmer_belegt = set()

    # Wir sortieren nach Decks, um die Übersicht zu behalten
    for b in bedarf:
        if b["spieler"] in nehmer_belegt: continue
        for g in gebot:
            if g["spieler"] in geber_belegt: continue
            if b["karte"] == g["karte"] and b["spieler"] != g["spieler"]:
                final_deals.append(f"✅ **{g['spieler']}** ➔ **{b['spieler']}** ({g['karte']})")
                geber_belegt.add(g["spieler"])
                nehmer_belegt.add(b["spieler"])
                break

    if final_deals:
        for deal in sorted(final_deals, key=lambda x: x.split('(')[1]):
            st.success(deal)
    else:
        st.info("Keine Tausche gefunden. Stelle sicher, dass Nullen (brauche) und Zahlen >= 2 (doppelt) eingetragen sind!")

except Exception as e:
    st.error(f"Fehler: {e}")
