import streamlit as st
import pandas as pd

# --- DEINE NAMEN-LISTE ---
# Hier kannst du die echten Namen deiner 20 Freunde eintragen
NAMEN = [f"Spieler {i+1}" for i in range(20)]
PASSWORT_CHEF = "Gang2026" # Dein Passwort für die Vorschläge

st.title("🃏 The Gang Karten App")

# Bereich 1: Eingabe für alle
st.header("📝 Karten eintragen")
name_wahl = st.selectbox("Wer bist du?", NAMEN)
deck_wahl = st.selectbox("Welches Deck?", [f"Deck {i+1}" for i in range(15)])

# Einfache 3x3 Matrix für die 9 Karten
st.write("Wie viele Karten hast du in diesem Deck?")
cols = st.columns(3)
for i in range(9):
    with cols[i % 3]:
        st.number_input(f"Karte {i+1}", min_value=0, max_value=99, key=f"s{i}")

if st.button("Speichern"):
    st.success("Daten wurden gemerkt!")

st.divider()

# Bereich 2: Dein Chef-Bereich
st.header("🔒 Chef-Bereich")
pw = st.text_input("Passwort eingeben für Vorschläge:", type="password")

if pw == PASSWORT_CHEF:
    if st.button("Vorschläge jetzt generieren"):
        st.info("Suche nach Decks, die fast voll sind (z.B. 8/9)...")
        # Hier erscheint später die Analyse deiner Google Tabelle
else:
    st.write("Gib das Passwort ein, um die Tausch-Vorschläge zu sehen.")
