import streamlit as st
import re

st.set_page_config(page_title="The Gang - Final", layout="wide")
st.title("🏆 The Gang: Blitz-Tausch")

st.info("Kopiere einfach alle Zeilen aus deiner Google-Tabelle hier rein.")

# Das große Textfeld für alles
raw_input = st.text_area("Daten hier einfügen (Namen und Zahlen):", height=400)

if raw_input:
    lines = raw_input.strip().split('\n')
    gebot = []
    bedarf = []

    for line in lines:
        # 1. Wir holen uns den Namen (das erste Wort der Zeile)
        parts = line.split()
        if len(parts) < 2: continue
        spieler = parts[0]

        # 2. Wir suchen alle Zahlen in dieser Zeile
        # Das ignoriert Buchstaben, Lücken und Sonderzeichen
        zahlen = re.findall(r'\b\d+\b', line)
        
        # 3. Wir ordnen die Zahlen den Karten zu
        for i, wert in enumerate(zahlen):
            try:
                anzahl = int(wert)
                # Karten-Logik: 9 Karten pro Deck
                deck_nr = (i // 9) + 1
                karte_nr = (i % 9) + 1
                label = f"Deck {deck_nr}-K{karte_nr}"

                if anzahl >= 2:
                    gebot.append({"name": spieler, "karte": label})
                elif anzahl == 0:
                    bedarf.append({"name": spieler, "karte": label})
            except:
                continue

    # Matching (Wer kann wem helfen?)
    st.subheader("✅ Tausch-Vorschläge")
    final_matches = []
    beschaeftigt = set()

    for b in bedarf:
        if b["name"] in beschaeftigt: continue
        for g in gebot:
            if g["name"] in beschaeftigt: continue
            
            if b["karte"] == g["karte"] and b["name"] != g["name"]:
                final_matches.append(f"🤝 **{g['name']}** gibt **{b['karte']}** an **{b['name']}**")
                beschaeftigt.add(g["name"])
                beschaeftigt.add(b["name"])
                break

    if final_matches:
        for m in sorted(final_matches):
            st.success(m)
    else:
        st.warning("Keine Treffer gefunden. Prüfe, ob du die Nullen (Bedarf) mitkopiert hast!")
else:
    st.write("Warte auf Daten aus der Zwischenablage...")
