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

# --- 3. SESSION STATE FÜR RESERVIERUNGEN ---
if 'reserviert' not in st.session_state:
    st.session_state.reserviert = set()

# --- 4. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-title { text-align: center; color: #fbbf24; font-size: 2.2rem; font-weight: bold; }
    .prio-box { background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #fbbf24; margin-bottom: 10px; }
    .success-text { color: #10b981; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

try:
    df_raw = pd.read_csv(SHEET_URL)
    df_raw = df_raw[df_raw.iloc[:, 0].notna() & (df_raw.iloc[:, 0].str.strip() != "") & (df_raw.iloc[:, 0].str.strip() != "Männlich")]
    spieler_namen = sorted(df_raw.iloc[:, 0].unique().tolist())

    st.markdown('<p class="main-title">💀 GANG HQ: STRATEGIE-ZENTRALE</p>', unsafe_allow_html=True)

    # --- BEREICH 1: KARTEN-EINGABE ---
    with st.expander("📝 KARTEN AKTUALISIEREN"):
        col1, col2 = st.columns(2)
        n_sel = col1.selectbox("Name", ["Wählen..."] + spieler_namen)
        d_sel = col2.selectbox("Deck", list(range(1, 16)))
        if n_sel != "Wählen...":
            s_zeile = df_raw[df_raw.iloc[:, 0] == n_sel]
            start_c = 1 + ((d_sel - 1) * 9)
            vals = [safe_int(s_zeile.iloc[0, start_c + i]) for i in range(9)]
            cols = st.columns(3); cols2 = st.columns(3); cols3 = st.columns(3)
            all_c = cols + cols2 + cols3
            neue = [str(int(all_c[i].number_input(f"K{i+1}", 0, 9, value=vals[i], key=f"upd_{i}"))) for i in range(9)]
            if st.button("🚀 SPEICHERN"):
                requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": ",".join(neue)})
                st.success("Gespeichert!"); st.rerun()

    # --- BEREICH 2: GEZIELTE SUCHE (PRIO 7/9 & 8/9) ---
    st.markdown("### 🎯 GEZIELTE FINISHER-SUCHE")
    search_name = st.selectbox("Wer soll gefördert werden?", ["Wählen..."] + spieler_namen)
    
    if search_name != "Wählen...":
        s_row = df_raw[df_raw.iloc[:, 0] == search_name]
        alle_gebot = []
        for _, row in df_raw.iterrows():
            g_n = str(row.iloc[0]).strip()
            if g_n == search_name: continue
            for col in df_raw.columns[1:]:
                if safe_int(row[col]) >= 2:
                    alle_gebot.append({"name": g_n, "karte": col})

        found = False
        for d in range(1, 16):
            start_c = 1 + ((d - 1) * 9)
            besitz = sum(1 for i in range(9) if safe_int(s_row.iloc[0, start_c + i]) > 0)
            
            # NUR 7/9 oder 8/9 vorschlagen
            if 7 <= besitz < 9:
                found = True
                st.markdown(f'<div class="prio-box"><b>Deck {d} ({besitz}/9)</b>', unsafe_allow_html=True)
                for i in range(9):
                    c_n = df_raw.columns[start_c + i]
                    if safe_int(s_row.iloc[0, start_c + i]) == 0:
                        moegliche_geber = [g['name'] for g in alle_gebot if g['karte'] == c_n]
                        if moegliche_geber:
                            for geber in moegliche_geber:
                                res_key = f"{geber}_{c_n}"
                                if st.checkbox(f"✅ {geber} gibt `{c_n}` an {search_name}", key=f"res_{res_key}"):
                                    st.session_state.reserviert.add(res_key)
                                else:
                                    st.session_state.reserviert.discard(res_key)
                        else:
                            st.write(f"❌ `{c_n}`: Kein Spender gefunden.")
                st.markdown('</div>', unsafe_allow_html=True)
        if not found: st.info("Keine Decks bei 7/9 oder 8/9 gefunden.")

    # --- BEREICH 3: RESTLICHE ANALYSE ---
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.text_input("Admin-Code", type="password") == ADMIN_PASSWORT:
        if st.button("Reservierungen löschen"):
            st.session_state.reserviert = set(); st.rerun()
            
        st.write(f"Aktiv reservierte Geber: {len(st.session_state.reserviert)}")
        
        gebot, bedarf = [], []
        for _, row in df_raw.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                bz = sum(1 for i in range(9) if safe_int(row.iloc[sc+i]) > 0)
                for i in range(9):
                    cn = df_raw.columns[sc+i]
                    if safe_int(row.iloc[sc+i]) >= 2:
                        # NUR wenn nicht oben reserviert!
                        if f"{sp}_{cn}" not in st.session_state.reserviert:
                            gebot.append({"s": sp, "k": cn})
                    elif safe_int(row.iloc[sc+i]) == 0:
                        bedarf.append({"s": sp, "k": cn, "f": bz, "did": f"{sp}_D{d}"})

        bedarf = sorted(bedarf, key=lambda x: (x['f'], x['did']), reverse=True)
        
        def get_matches(is_dia):
            res, weg = [], set()
            fort = {b['did']: b['f'] for b in bedarf}
            for b in bedarf:
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            if fort[b['did']] < 9:
                                res.append(f"**({fort[b['did']]}/9)** {g['s']} ➔ {b['s']} ({b['k']})")
                                fort[b['did']] += 1; weg.add(g["s"])
                                break
            return res

        t1, t2 = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        with t1:
            for m in get_matches(False): st.success(m)
        with t2:
            for m in get_matches(True): st.info(m)

except Exception as e: st.error(f"Fehler: {e}")
