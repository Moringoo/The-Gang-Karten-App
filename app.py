import streamlit as st
import re

# Design-Anpassung: Dark Mode für "The Gang"
st.set_page_config(page_title="The Gang: Kartell-Börse", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stRadio > div { background-color: #1a1c23; padding: 10px; border-radius: 10px; }
    .stTextArea textarea { background-color: #1a1c23 !important; color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ The Gang: Kartell-Tauschbörse")
st.write("---")

# Auswahl oben: Gold oder Diamant
modus = st.radio("Was willst du heute tauschen?", ["🌕 Gold-Karten", "💎 Diamant-Karten"], horizontal=True)

st.subheader("📋 Daten aus Google Sheets einfügen")
all_data = st.text_area("Kopiere hier alle Spieler-Zeilen rein:", height=250, placeholder="Troy 1 2 0 1...\nJens 2 0 1 1...")

if all_data:
    lines = all_data.strip().split('\n')
    gebot = []
    bedarf = []
    
    prefix = "Gold" if "Gold" in modus else "Diamant"

    for line in lines:
        parts = line.split()
        if len(parts) < 2: continue
        spieler = parts[0]
        # Wir fischen alle reinen Zahlen aus der Zeile
        zahlen = re.findall(r'\b\d+\b', line)
        
        for i, wert in enumerate(zahlen):
            try:
                anzahl = int(wert)
                deck_nr = (i // 9) + 1
                karte_nr = (i % 9) + 1
                label = f"{prefix} D{deck_nr}-K{karte_nr}"
                
                if anzahl >= 2:
                    gebot.append({"name": spieler, "karte": label})
                elif anzahl == 0:
                    # Echte 0 = Sucht die Karte
                    bedarf.append({"name": spieler, "karte": label})
            except:
                continue

    # Matching Logik
    st.divider()
    st.subheader(f"🔄 Aktuelle {modus} Deals")
    
    matches = []
    used = set()

    for b in bedarf:
        if b["name"] in used: continue
        for g in gebot:
            if g["name"] in used: continue
            if b["karte"] == g["karte"] and b["name"] != g["name"]:
                matches.append(f"🤝 *{g['name']}* ➔ *{b['name']}* ({g['karte']})")
                used.add(g["name"])
                used.add(b["name"])
                break

    if matches:
        wa_text = f"*Heutige Tauschliste ({modus})*:\n\n" + "\n".join(matches)
        for m in matches:
            st.success(m)
        
        st.divider()
        st.subheader("📲 Text für WhatsApp")
        st.code(wa_text) # Einfach klicken zum Kopieren
    else:
        st.info(f"Keine {modus} Matches gefunden. Prüfe, ob du die richtigen Spalten kopiert hast!")

st.markdown("---")
st.caption("Totenkopfgang XxL | Strategie-Tool v3.0")
