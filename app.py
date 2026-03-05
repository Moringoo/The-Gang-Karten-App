import streamlit as st
import pandas as pd
import requests

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaIWcjmJ5Nn5MsRR66ptz97MBjJ-S0O-B7TVp1Y4pq81Xc1Q0VLNzDFWDn6c9NcB4/exec" 
GID = "2025591169"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}"
ADMIN_PASSWORT = "gang2026" 

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #1f2937; color: #fbbf24; border: 1px solid #fbbf24; font-weight: bold; width: 100%; border-radius: 10px; }
    .main-title { text-align: center; color: #fbbf24; font-size: 2.5rem; font-weight: bold; margin-bottom: 0; }
    .sub-title { text-align: center; color: #9ca3af; font-size: 1.2rem; margin-top: 0; margin-bottom: 2rem; }
    .card-label { color: #fbbf24; font-weight: bold; margin-bottom: -10px; }
    .finisher-box { background-color: #1e3a8a; border: 2px solid #3b82f6; padding: 10px; border-radius: 10px; margin-bottom: 5px; }
    hr { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">THE GANG: HAUPTQUARTIER</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">💀 TOTENKOPFGANG 💀</p>', unsafe_allow_html=True)

# --- BEREICH 1: KARTEN-EINGABE ---
# (Dieser Teil bleibt für die Spieler wie gehabt, lädt die Daten vor)
try:
    df_raw = pd.read_csv(SHEET_URL)
    spieler_namen = df_raw.iloc[:, 0].dropna().unique().tolist()
    
    col_a, col_b = st.columns(2)
    with col_a:
        name_sel = st.selectbox("Wer bist du?", ["Bitte wählen..."] + spieler_namen)
    with col_b:
        deck_sel = st.selectbox("Welches Deck?", list(range(1, 16)))

    if name_sel != "Bitte wählen...":
        aktuelle_werte = [0] * 9
        spieler_zeile = df_raw[df_raw.iloc[:, 0] == name_sel]
        if not spieler_zeile.empty:
            start_col = 1 + ((deck_sel - 1) * 9)
            for i in range(9):
                try:
                    val = spieler_zeile.iloc[0, start_col + i]
                    aktuelle_werte[i] = int(float(str(val).replace(',', '.')))
                except: aktuelle_werte[i] = 0
        
        st.info(f"Karten für **{name_sel}** (Deck {deck_sel}) geladen.")
        rows = [st.columns(3) for _ in range(3)]
        alle_grids = [col for row in rows for col in row]
        neue_werte = []
        for i in range(9):
            with alle_grids[i]:
                st.markdown(f'<p class="card-label">K{i+1}</p>', unsafe_allow_html=True)
                v = st.number_input(f"K{i+1}", 0, 9, value=aktuelle_werte[i], step=1, key=f"in_{name_sel}_{deck_sel}_{i}", label_visibility="collapsed")
                neue_werte.append(str(int(v)))
        
        if st.button("🚀 ÄNDERUNGEN SPEICHERN"):
            with st.spinner("Speichere..."):
                res = requests.get(SCRIPT_URL, params={"name": name_sel, "deck": deck_sel, "werte": ",".join(neue_werte)}, timeout=15)
                if res.text == "Erfolg": st.success("Gespeichert!"); st.balloons()
except Exception as e: st.error(f"Fehler: {e}")

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# --- BEREICH 2: ADMIN-TRESOR (OPTIMIERTE ANALYSE) ---
st.markdown("### 🕵️‍♂️ ADMIN-BEREICH (PRIORISIERTE TAUSCH-ANALYSE)")
pw_input = st.text_input("Sicherheits-Code eingeben", type="password")

if pw_input == ADMIN_PASSWORT:
    st.success("Priorisierungs-Modus aktiv: Spieler mit 7+ Karten werden bevorzugt!")
    try:
        df = pd.read_csv(SHEET_URL)
        karten_cols = df.columns[1:]
        
        decks = {}
        for col in karten_cols:
            d_name = col.split('-')[0]
            if d_name not in decks: decks[d_name] = []
            decks[d_name].append(col)

        gebot, bedarf = [], []
        for _, row in df.iterrows():
            spieler = str(row.iloc[0]).strip()
            if spieler in ["nan", "None", ""]: continue
            for d_name, d_cols in decks.items():
                # Wie viele Karten hat der Spieler in DIESEM Deck bereits?
                besitz_count = sum(1 for c in d_cols if pd.notna(row[c]) and int(float(str(row[c]).replace(',','.'))) > 0)
                for c in d_cols:
                    try:
                        anz = int(float(str(row[c]).replace(',', '.')))
                        if anz >= 2: 
                            gebot.append({"s": spieler, "k": c})
                        elif anz == 0: 
                            # Wir speichern den besitz_count für die Sortierung
                            bedarf.append({"s": spieler, "k": c, "f": besitz_count})
                    except: continue

        # --- SORTIER-LOGIK: Spieler mit höchstem Fortschritt (f) zuerst ---
        bedarf = sorted(bedarf, key=lambda x: x['f'], reverse=True)

        def get_matches(is_dia):
            results = []
            weg = set() # Verhindert, dass ein Geber doppelt verplant wird
            temp_progress = {b['s'] + b['k'].split('-')[0]: b['f'] for b in bedarf}

            for b in bedarf:
                deck_id = b['s'] + b['k'].split('-')[0]
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        # Partner finden: Geber hat Karte, ist nicht der Nehmer, Karte passt
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            aktuell = temp_progress.get(deck_id, b['f'])
                            
                            # Prioritäts-Label
                            if aktuell == 8:
                                label = "🚨 FINISHER! (Letzte Karte)"
                                color = "blue"
                            elif aktuell == 7:
                                label = "⭐ TOP PRIO (Noch 2 Karten)"
                                color = "green"
                            else:
                                label = f"({aktuell}/9)"
                                color = "gray"

                            results.append({
                                "prio": aktuell,
                                "text": f"**{label}** | {g['s']} ➔ {b['s']} ({g['k']})",
                                "color": color
                            })
                            temp_progress[deck_id] = aktuell + 1
                            weg.add(g["s"])
                            break
            return results

        t1, t2 = st.tabs(["🌕 GOLD DEALS", "💎 DIAMANT DEALS"])
        
        for tab, is_dia in zip([t1, t2], [False, True]):
            with tab:
                matches = get_matches(is_dia)
                if matches:
                    for m in matches:
                        if m["prio"] >= 7:
                            st.info(m["text"]) # Hervorgehoben für Prio-Spieler
                        else:
                            st.write(m["text"])
                else:
                    st.write("Keine Tauschmöglichkeiten gefunden.")

    except Exception as e:
        st.error(f"Analyse-Fehler: {e}")
