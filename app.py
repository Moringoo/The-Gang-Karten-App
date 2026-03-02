import streamlit as st
import pandas as pd
import requests

# --- 1. SETUP ---
st.set_page_config(
    page_title="The Gang HQ", 
    page_icon="💀", 
    layout="wide"
)

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
    hr { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO & TITEL ---
col_logo, col_titel = st.columns([1, 4])
with col_logo:
    # Dein Totenkopf-Logo
    st.image("https://raw.githubusercontent.com/fabiomatthews/the-gang-karten-app/main/image_fd0274.jpg", width=120)

with col_titel:
    st.title("THE GANG: HAUPTQUARTIER")
    st.subheader("💀 TOTENKOPFGANG")

# --- BEREICH 1: KARTEN-EINGABE ---
st.markdown("### 📝 MEINE KARTEN AKTUALISIEREN")

try:
    df_raw = pd.read_csv(SHEET_URL)
    spieler_namen = df_raw.iloc[:, 0].dropna().unique().tolist()
    
    col_a, col_b = st.columns(2)
    with col_a:
        name_sel = st.selectbox("Wer bist du?", ["Bitte wählen..."] + spieler_namen)
    with col_b:
        deck_sel = st.selectbox("Welches Deck?", list(range(1, 16)))
    
    st.info(f"Eingabe für: **{name_sel}** | **Deck {deck_sel}**")
    
    r1, r2, r3 = st.columns(3), st.columns(3), st.columns(3)
    alle_grids = r1 + r2 + r3
    
    neue_werte = []
    for i in range(9):
        with alle_grids[i]:
            v = st.number_input(
                f"K{i+1}", 0, 9, value=0, step=1, 
                key=f"user_{name_sel}_deck_{deck_sel}_k{i}"
            )
            neue_werte.append(str(int(v)))
    
    if st.button("🚀 DATEN SPEICHERN"):
        if name_sel == "Bitte wählen...":
            st.warning("Bitte Namen wählen!")
        else:
            with st.spinner("Speichere..."):
                try:
                    payload = {"name": name_sel, "deck": deck_sel, "werte": ",".join(neue_werte)}
                    res = requests.get(SCRIPT_URL, params=payload, timeout=15)
                    if res.text == "Erfolg":
                        st.success("Gespeichert!")
                        st.balloons()
                    else:
                        st.error(f"Fehler: {res.text}")
                except:
                    st.error("Verbindung zum Sheet fehlgeschlagen.")
except Exception as e:
    st.error(f"Ladefehler (Prüfe die SHEET_URL): {e}")

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# --- BEREICH 2: ADMIN-TRESOR ---
st.markdown("### 🕵️‍♂️ ADMIN-BEREICH (TAUSCH-ANALYSE)")
pw_input = st.text_input("Sicherheits-Code", type="password")

if pw_input == ADMIN_PASSWORT:
    st.success("Admin-Zugriff bestätigt.")
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
                besitz = sum(1 for c in d_cols if pd.notna(row[c]) and int(float(str(row[c]).replace(',','.'))) > 0)
                for c in d_cols:
                    try:
                        anz = int(float(str(row[c]).replace(',', '.')))
                        if anz >= 2: gebot.append({"s": spieler, "k": c})
                        elif anz == 0: bedarf.append({"s": spieler, "k": c, "f": besitz})
                    except: continue

        bedarf = sorted(bedarf, key=lambda x: x['f'], reverse=True)

        def get_matches(is_dia):
            results, weg = [], set()
            temp_progress = {b['s'] + b['k'].split('-')[0]: b['f'] for b in bedarf}

            for b in bedarf:
                deck_id = b['s'] + b['k'].split('-')[0]
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            aktuell = temp_progress.get(deck_id, b['f'])
                            label = "🔥 FINISHER!" if aktuell >= 8 else f"({aktuell}/9)"
                            results.append(f"{label} | **{g['s']}** ➔ **{b['s']}** ({g['k']})")
                            temp_progress[deck_id] = aktuell + 1
                            weg.add(g["s"])
                            break
            return results

        t_g, t_d = st.tabs(["🌕 GOLD DEALS", "💎 DIAMANT DEALS"])
        with t_g:
            m_g = get_matches(False)
            if m_g:
                for match in m_g: st.success(match)
            else: st.write("Keine Gold-Matches.")
        with t_d:
            m_d = get_matches(True)
            if m_d:
                for match in m_d: st.info(match)
            else: st.write("Keine Diamant-Matches.")
    except Exception as e:
        st.error(f"Analyse-Fehler: {e}")
elif pw_input != "":
    st.error("Falscher Code!")
