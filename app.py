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

def safe_int(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan": return 0
        return int(float(str(val).replace(',', '.')))
    except: return 0

# --- 3. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-title { text-align: center; color: #fbbf24; font-size: 2.5rem; font-weight: bold; margin-bottom: 20px; }
    .card-label { color: #fbbf24; font-weight: bold; margin-bottom: -10px; }
    .stat-card { background-color: #1f2937; padding: 10px; border-radius: 10px; border-top: 3px solid #fbbf24; text-align: center; }
    .match-found { background-color: #064e3b; padding: 5px; border-radius: 5px; border: 1px solid #10b981; }
    hr { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">THE GANG: HAUPTQUARTIER</p>', unsafe_allow_html=True)

try:
    # Daten laden und bereinigen
    df_raw = pd.read_csv(SHEET_URL)
    df_raw = df_raw[df_raw.iloc[:, 0].notna()]
    df_raw = df_raw[df_raw.iloc[:, 0].str.strip() != ""]
    df_raw = df_raw[df_raw.iloc[:, 0].str.strip() != "Männlich"]
    spieler_namen = sorted(df_raw.iloc[:, 0].unique().tolist())

    # --- BEREICH 1: KARTEN-EINGABE (Wieder da!) ---
    st.markdown("### 📝 MEINE KARTEN AKTUALISIEREN")
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
                aktuelle_werte[i] = safe_int(spieler_zeile.iloc[0, start_col + i])
        
        # 3x3 Eingabe-Raster
        r1, r2, r3 = st.columns(3), st.columns(3), st.columns(3)
        grids = r1 + r2 + r3
        neue_werte = []
        for i in range(9):
            with grids[i]:
                v = st.number_input(f"K{i+1}", 0, 9, value=aktuelle_werte[i], key=f"e_{name_sel}_{deck_sel}_{i}")
                neue_werte.append(str(int(v)))
        
        if st.button("🚀 ÄNDERUNGEN SPEICHERN"):
            with st.spinner("Speichere im Sheet..."):
                res = requests.get(SCRIPT_URL, params={"name": name_sel, "deck": deck_sel, "werte": ",".join(neue_werte)}, timeout=15)
                if res.text == "Erfolg":
                    st.success("Erfolgreich gespeichert!"); st.balloons()
                else: st.error(f"Fehler: {res.text}")

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- BEREICH 2: GEZIELTE KARTENSUCHE (Wer hat was Gabri88 braucht?) ---
    st.markdown("### 🔍 GEZIELTE SUCHE & GEBER-FINDER")
    search_name = st.selectbox("Für wen suchen wir Karten? (z.B. Gabri88)", ["Bitte wählen..."] + spieler_namen, key="search_box")
    
    if search_name != "Bitte wählen...":
        s_row = df_raw[df_raw.iloc[:, 0] == search_name]
        
        # Alle Doppelten in der Gang finden
        alle_doppelten = {}
        for _, row in df_raw.iterrows():
            g_name = str(row.iloc[0]).strip()
            if g_name == search_name: continue
            for col in df_raw.columns[1:]:
                if safe_int(row[col]) >= 2:
                    if col not in alle_doppelten: alle_doppelten[col] = []
                    alle_doppelten[col].append(g_name)

        # Fehlende Karten für den gewählten Spieler prüfen
        found_any = False
        for d in range(1, 16):
            start_c = 1 + ((d - 1) * 9)
            besitz = sum(1 for i in range(9) if safe_int(s_row.iloc[0, start_c + i]) > 0)
            
            if 6 <= besitz < 9: # Nur fast volle Decks anzeigen
                st.markdown(f"**Deck {d} ({besitz}/9):**")
                for i in range(9):
                    c_name = df_raw.columns[start_c + i]
                    val = safe_int(s_row.iloc[0, start_c + i])
                    if val == 0:
                        geber_liste = alle_doppelten.get(c_name, [])
                        if geber_liste:
                            st.markdown(f"✅ Karte `{c_name}` fehlt -> **VERFÜGBAR BEI:** {', '.join(geber_liste)}", unsafe_allow_html=True)
                        else:
                            st.markdown(f"❌ Karte `{c_name}` fehlt -> *Niemand hat diese Karte doppelt.*")
                found_any = True
        
        if not found_any:
            st.info("Dieser Spieler hat momentan keine Decks mit 6, 7 oder 8 Karten.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- BEREICH 3: ADMIN TAUSCH ANALYSE ---
    with st.expander("🕵️‍♂️ VOLLSTÄNDIGE ADMIN-ANALYSE"):
        if st.text_input("Code", type="password") == ADMIN_PASSWORT:
            # (Die komplexe Tausch-Logik von vorher...)
            gebot, bedarf = [], []
            for _, row in df_raw.iterrows():
                spieler = str(row.iloc[0]).strip()
                for d in range(1, 16):
                    start_c = 1 + ((d - 1) * 9)
                    besitz = sum(1 for i in range(9) if safe_int(row.iloc[start_c + i]) > 0)
                    for i in range(9):
                        c_name = df_raw.columns[start_c + i]
                        if safe_int(row.iloc[start_c + i]) >= 2: gebot.append({"s": spieler, "k": c_name})
                        elif safe_int(row.iloc[start_c + i]) == 0: bedarf.append({"s": spieler, "k": c_name, "f": besitz, "d_id": f"{spieler}_D{d}"})

            bedarf = sorted(bedarf, key=lambda x: (x['f'], x['d_id']), reverse=True)
            
            def get_matches(is_dia):
                results, weg_geber = [], set()
                fortschritt = {b['d_id']: b['f'] for b in bedarf}
                for b in bedarf:
                    if (("(D)" in b["k"]) == is_dia):
                        for g in gebot:
                            if g["s"] not in weg_geber and g["s"] != b["s"] and g["k"] == b["k"]:
                                label = "🚨 FINISHER!" if fortschritt[b['d_id']] == 8 else f"({fortschritt[b['d_id']]}/9)"
                                results.append(f"**{label}** {g['s']} ➔ {b['s']} ({b['k']})")
                                fortschritt[b['d_id']] += 1
                                weg_geber.add(g["s"])
                                break
                return results

            t1, t2 = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
            with t1:
                for m in get_matches(False): st.success(m)
            with t2:
                for m in get_matches(True): st.info(m)
            
except Exception as e:
    st.error(f"Fehler: {e}")
