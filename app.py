import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="The Gang - Fix", layout="wide")
st.title("🃏 The Gang: Manueller Daten-Abgleich")

st.info("Markiere in Google Sheets deine Daten (Namen + Zahlen) und füge sie hier ein.")

# Textfeld für die Daten
raw_input = st.text_area("Hier Daten einfügen (Strg+V):", height=300)

if raw_input:
    try:
        lines = raw_input.strip().split('\n')
        processed_data = []
        
        for line in lines:
            # Wir splitten die Zeile bei jedem "Whitespace" (Tab oder mehrere Leerzeichen)
            parts = re.split(r'\t|\s{2,}', line.strip())
            # Falls nur einfache Leerzeichen da sind, versuchen wir es damit
            if len(parts) < 2:
                parts = line.split()
            
            if len(parts) > 1:
                processed_data.append(parts)

        if processed_data:
            # Wir erstellen eine Tabelle daraus
            df = pd.DataFrame(processed_data)
            
            gebot = []
            bedarf = []

            for _, row in df.iterrows():
                spieler = str(row.iloc[0]).strip()
                # Wir gehen alle Spalten nach dem Namen durch
                for i in range(1, len(row)):
                    val = str(row.iloc[i]).strip()
                    if val == "" or val.lower() == "none": continue
                    
                    try:
                        # Wir säubern die Zahl (entfernen Punkte/Kommata)
                        anzahl = int(float(val.replace(',', '.')))
                        
                        # Berechnung Deck/Karte basierend auf der Position
                        deck_nr = (i - 1) // 9 + 1
                        karten_nr = (i - 1) % 9 + 1
                        label = f"D{deck_nr}-K{karten_nr}"
                        
                        if anzahl >= 2:
                            gebot.append({"spieler": spieler, "karte": label})
                        elif anzahl == 0:
                            bedarf.append({"spieler": spieler, "karte": label})
                    except:
                        continue

            # Matching
            st.subheader("📋 Tausch-Vorschläge")
            final_matches = []
            beschaeftigt = set()

            for b in bedarf:
                if b["spieler"] in beschaeftigt: continue
                for g in gebot:
                    if g["spieler"] in beschaeftigt: continue
                    if b["karte"] == g["karte"] and b["spieler"] != g["spieler"]:
                        final_matches.append(f"✅ **{g['spieler']}** gibt **{g['karte']}** an **{b['spieler']}**")
                        beschaeftigt.add(g["spieler"])
                        beschaeftigt.add(b["spieler"])
                        break

            if final_matches:
                for m in sorted(final_matches):
                    st.success(m)
            else:
                st.warning("Keine Treffer. Prüfe, ob Nullen und Zahlen >= 2 korrekt eingefügt wurden.")
        
    except Exception as e:
        st.error(f"Fehler beim Lesen: {e}")
