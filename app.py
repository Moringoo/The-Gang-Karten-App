import streamlit as st
import pandas as pd
import requests

# --- 1. DEIN KONFIGURIERTER LINK ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaIWcjmJ5Nn5MsRR66ptz97MBjJ-S0O-B7TVp1Y4pq81Xc1Q0VLNzDFWDn6c9NcB4/exec" 

# --- 2. DATEN-QUELLE (Google Sheet) ---
GID = "2025591169"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"

st.set_page_config(page_title="The Gang: Tausch & Update", layout="wide")

# Navigation in der Seitenleiste
st.sidebar.title("Menü")
page = st.sidebar.radio("Navigation", ["🛡️ Tausch-Zentrale", "📝 Karten eingeben"])

if page == "📝 Karten eingeben":
    st.header("📝 Deine Karten aktualisieren")
    st.info("Wähle deinen Namen und das Deck. Gib für jede Karte ein: 0 (Suche), 1 (Habe), 2 (Doppelt).")
    
    try:
        # Lade die aktuellen Namen aus deinem Google Sheet für das Dropdown
        df_raw = pd.read_csv(SHEET_URL)
        # Wir nehmen die Namen aus der ersten Spalte
        spieler_namen = df_raw.iloc[:, 0].dropna().unique().tolist()
        
        with st.form("input_form"):
            name = st.selectbox("Wer bist du?", spieler_namen)
            deck = st.selectbox("Welches Deck möchtest du aktualisieren?", list(range(1, 16)))
            
            st.write(f"### Werte für Deck {deck}")
            cols = st.columns(9)
            neue_werte = []
            for i in range(9):
                with cols[i]:
                    val = st.number_input(f"K{i+1}", 0, 9, key=f"k{i}", help="0=Suche, 1=Besitze, 2+=Doppelt")
                    neue_werte.append(str(int(val)))
            
            submit = st.form_submit_button("💾 Im Google Sheet speichern")
            
            if submit:
                werte_str = ",".join(neue_werte)
                # Sende Daten an dein Google Apps Script
                with st.spinner("Speichere Daten in Google Sheets..."):
                    try:
                        response = requests.get(f"{SCRIPT_URL}?name={name}&deck={deck}&werte={werte_str}", timeout=10)
                        if response.text == "Erfolg":
                            st.success(f"Wunderbar, {name}! Deine Daten für Deck {deck} wurden direkt im Sheet aktualisiert.")
                            st.balloons()
                        else:
                            st.error(f"Fehler vom Server: {response.text}")
                    except Exception as e:
                        st.error(f"Verbindungsfehler: {e}")
    except Exception as e:
        st.error(f"Konnte Spielerliste nicht laden: {e}")

else:
    st.header("🛡️ Strategische Tausch-Vorschläge")
    st.caption("Priorität: Decks, die kurz vor dem Abschluss stehen (8/9), werden zuerst bedient.")
    
    try:
        df = pd.read_csv(SHEET_URL)
        
        # Decks organisieren (9 Spalten pro Deck nach dem Namen)
        karten_cols = df.columns[1:]
        decks = {}
        for col in karten_cols:
            d_name = col.split('-')[0]
            if d_name not in decks: decks[d_name] = []
            decks[d_name].append(col)

        gebot, bedarf_prio = [], []

        for _, row in df.iterrows():
            spieler = str(row.iloc[0]).strip()
            if spieler in ["nan", "None", ""]: continue
            
            for d_name, d_cols in decks.items():
                # Fortschritt berechnen: Wie viele Karten hat der Spieler in diesem Deck?
                besitz = sum(1 for c in d_cols if pd.notna(row[c]) and int(float(str(row[c]).replace(',','.'))) > 0)
                
                for c in d_cols:
                    try:
                        val = row[c]
                        if pd.isna(val): continue
                        anz = int(float(str(val).replace(',', '.')))
                        
                        if anz >= 2: 
                            gebot.append({"s": spieler, "k": c})
                        elif anz == 0: 
                            bedarf_prio.append({"s": spieler, "k": c, "f": besitz})
                    except: continue

        # Strategische Sortierung: Höchster Fortschritt (Closer) zuerst
        bedarf_prio = sorted(bedarf_prio, key=lambda x: x['f'], reverse=True)

        def match(is_dia):
            res, sender_weg = [], set()
            for b in bedarf_prio:
                # Prüfe ob Gold oder Diamant
                ist_karten_dia = "(D)" in b["k"]
                if ist_karten_dia == is_dia:
                    for g in gebot:
                        # Regeln: Sender frei, nicht an sich selbst, gleiche Karte
                        if g["s"] not in sender_weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            label = "🔥 **FINISHER!**" if b['f'] == 8 else f"({b['f']}/9)"
                            res.append(f"{label} | **{g['s']}** ➔ **{b['s']}** ({g['k']})")
                            sender_weg.add(g["s"])
                            break
            return res

        tab1, tab2 = st.tabs(["🌕 Gold-Karten", "💎 Diamant-Karten"])
        with tab1:
            gold_matches = match(False)
            if gold_matches:
                for m in gold_matches: st.success(m)
            else: st.info("Aktuell keine Gold-Matches möglich.")
            
        with tab2:
            dia_matches = match(True)
            if dia_matches:
                for m in dia_matches: st.info(m)
            else: st.warning("Aktuell keine Diamant-Matches möglich.")

    except Exception as e:
        st.error(f"Fehler beim Laden der Tauschdaten: {e}")
