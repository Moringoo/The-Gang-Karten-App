import streamlit as st

st.set_page_config(page_title="The Gang - Tausch-Check", layout="wide")
st.title("🃏 The Gang: Manueller Karten-Check")

# Wir definieren die Kartennamen aus deinem Set (Beispiel)
karten_liste = ["K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9"]

st.write("Wähle aus, wer welche Karte doppelt hat (2+) und wer sie sucht (0).")

# Datenbank im Hintergrund (simuliert)
gebot = []
bedarf = []

# Wir erstellen Spalten für die wichtigsten Spieler
spieler_namen = ["Troy", "Jens", "GABRI88", "Loppi", "Caine", "Johnny"]
cols = st.columns(len(spieler_namen))

for i, name in enumerate(spieler_namen):
    with cols[i]:
        st.subheader(name)
        for karte in karten_liste:
            # Eingabefeld für jeden Spieler und jede Karte
            anzahl = st.number_input(f"{name}: {karte}", min_value=0, max_value=10, value=1, key=f"{name}_{karte}")
            
            if anzahl >= 2:
                gebot.append({"spieler": name, "karte": karte})
            elif anzahl == 0:
                bedarf.append({"spieler": name, "karte": karte})

st.divider()

# Matching Logik
st.header("📋 Tausch-Ergebnis")
matches = []
belegt = set()

for b in bedarf:
    if b["spieler"] in belegt: continue
    for g in gebot:
        if g["spieler"] in belegt: continue
        if b["karte"] == g["karte"] and b["spieler"] != g["spieler"]:
            matches.append(f"✅ **{g['spieler']}** gibt **{b['karte']}** an **{b['spieler']}**")
            belegt.add(g["spieler"])
            belegt.add(b["spieler"])
            break

if matches:
    for m in matches:
        st.success(m)
else:
    st.info("Noch keine Täusche möglich. Ändere die Zahlen oben auf 0 (suche) oder 2 (habe doppelt).")
