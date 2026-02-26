import streamlit as st
import pandas as pd
import requests

# --- 1. SETUP ---
st.set_page_config(
    page_title="The Gang HQ", 
    page_icon="🛡️", 
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

st.title("🛡️ THE GANG: HAUPTQUARTIER")

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
    
    st.write(f"Werte für Deck {deck_sel}:")
    
    # 3x3 Raster
    r1, r2, r3 = st.columns(3), st.columns(3), st.columns(3)
    alle_grids = r1 + r2 + r3
    
    neue_werte = []
    for i in range(9):
        with alle_grids[i]:
            v = st.number_input(f"K{i+1}", 0, 9, key=f"k{i}", step=1)
            neue_werte.append(str(int(v)))
    
    if st.button("🚀 DATEN SPEICHERN"):
        if name_sel == "Bitte wählen...":
            st.warning("Bitte wähle zuerst deinen Namen!")
        else:
            with st.spinner("Sende Daten..."):
                try:
                    res = requests.get(f"{SCRIPT_URL}?name={name_sel}&deck={deck_sel}&werte={','.join(neue_werte)}", timeout=15)
                    if res.text == "Erfolg":
                        st.success("Erfolgreich gespeichert!")
                        st.balloons()
                    else:
                        st.error(f"Fehler: {res.text}")
                except:
                    st.error("Verbindung zum Sheet fehlgeschlagen.")
except Exception as e:
    st.error(f"Ladefehler: {e}")

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# --- BEREICH 2: ADMIN-TRESOR ---
st.markdown("### 🕵️‍♂️ ADMIN-BEREICH (TAUSCH-ANALYSE)")
pw_input = st.text_input("Sicherheits-Code", type="password")

if pw_input == ADMIN_PASSWORT:
    st.success("Zugriff gewährt.")
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
            for b in bedarf:
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            prio = "🔥 FIN!" if b['f'] == 8 else f"({b['f']}/9)"
                            results.append(f"{prio} | {g['s']} ➔ {b['s']} ({g['k']})")
                            weg.add(g["s"])
                            break
            return results

        t_g, t_d = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
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
