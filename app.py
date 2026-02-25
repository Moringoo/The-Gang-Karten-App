import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="The Gang - Manual Sync", layout="wide")

st.title("🃏 The Gang: Manueller Daten-Abgleich")
st.info("Kopiere deine Tabelle in Google Sheets (von Troy bis zum letzten Spieler) und füge sie unten ein.")

# Das Textfeld für deine Daten
raw_data = st.text_area("Hier die Tabellen-Daten einfügen (Strg+V):", height=300)

if raw_data:
    try:
        # Wir lesen die Daten direkt aus dem Textfeld (Tab-getrennt beim Kopieren aus Excel/Sheets)
        df = pd.read_csv(io.StringIO(raw_data), sep='\t', header=None)
        
        gebot = []
        bedarf = []

        for _, row in df.iterrows():
            # Spalte 0 ist der Name
            spieler = str(row.iloc[0]).strip()
            if spieler.lower() in ["nan", ""]: continue

            # Wir scannen die Karten-Spalten (1 bis 9 für Deck 1, 10 bis 18 für Deck 2...)
            # Wir gehen davon aus, dass beim Kopieren keine leeren Spalten mitkommen
            for i in range(1, len(row)):
                val = row.iloc[i]
                if pd.isna(val) or str(val).strip() == "":
                    continue
                
                try:
                    anzahl = int(float(str(val).replace(',', '.')))
                    deck_nr = (i - 1) // 9 + 1
                    karten_nr = (i - 1) % 9 + 1
                    label = f"Deck {deck_nr}-K{karten_nr}"
                    
                    if anzahl >= 2:
                        gebot.append({"spieler": spieler, "karte": label})
                    elif anzahl == 0:
                        # Echte Null = Sucht Karte
                        bedarf.append({"spieler": spieler, "karte": label})
                except:
                    continue

        # Matching Logik
        st.subheader("📋 Deine persönlichen Tausch-Vorschläge")
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
            st.warning("Keine Übereinstimmungen gefunden. Prüfe, ob die Nullen und 2er korrekt kopiert wurden.")

    except Exception as e:
        st.error(f"Fehler beim Verarbeiten der Daten: {e}")
else:
    st.write("Warte auf Daten... Markiere in Google Sheets einfach den Bereich mit den Namen und Zahlen und füge ihn hier ein.")
