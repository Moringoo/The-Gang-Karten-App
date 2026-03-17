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

# --- 3. SESSION STATE ---
if 'reserviert' not in st.session_state:
    st.session_state.reserviert = {} 

# --- 4. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-title { text-align: center; color: #fbbf24; font-size: 2.2rem; font-weight: bold; }
    .prio-box { background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #fbbf24; margin-bottom: 10px; border: 1px solid #334155; }
    .finisher-badge { background-color: #ef4444; color: white; padding: 4px 8px; border-radius: 5px; font-weight: bold; font-size: 0.9rem; }
    .blink { animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.4; } }
    </style>
    """, unsafe_allow_html=True)

try:
    # Daten laden
    df_raw = pd.read_csv(SHEET_URL)
    df_raw = df_raw[df_raw.iloc[:, 0].notna() & (df_raw.iloc[:, 0].str.strip() != "")]
    spieler_namen = sorted(df_raw.iloc[:, 0].unique().tolist())

    st.markdown('<p class="main-title">💀 GANG HQ: FINISHER-STRATEGIE</p>', unsafe_allow_html=True)

    # --- BEREICH 1: KARTEN-EINGABE ---
    with st.expander("📝 KARTEN AKTUALISIEREN"):
        c1, c2 = st.columns(2)
        n_sel = c1.selectbox("Wer bist du?", ["Wählen..."] + spieler_namen)
        d_sel = c2.selectbox("Welches Deck?", list(range(1, 16)))
        if n_sel != "Wählen...":
            s_zeile = df_raw[df_raw.iloc[:, 0] == n_sel]
            start_c = 1 + ((d_sel - 1) * 9)
            vals = [safe_int(s_zeile.iloc[0, start_c + i]) for i in range(9)]
            r1, r2, r3 = st.columns(3), st.columns(3), st.columns(3)
            all_c = r1 + r2 + r3
            neue = [str(int(all_c[i].number_input(f"K{i+1}", 0, 9, value=vals[i], key=f"u_{i}"))) for i in range(9)]
            if st.button("🚀 SPEICHERN"):
                requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": ",".join(neue)})
                st.success("Gespeichert!"); st.rerun()

    # --- BEREICH 2: GEZIELTE FINISHER-SUCHE ---
    st.markdown("### 🎯 GEZIELTE SUCHE (7/9 & 8/9)")
    search_name = st.selectbox("Wer soll heute Decks vollmachen?", ["Wählen..."] + spieler_namen)
    
    # Vor-Berechnung Gebote
    alle_gebot_dict = {}
    for _, row in df_raw.iterrows():
        g_n = str(row.iloc[0]).strip()
        for col in df_raw.columns[1:]:
            if safe_int(row[col]) >= 2:
                if col not in alle_gebot_dict: alle_gebot_dict[col] = []
                alle_gebot_dict[col].append(g_n)

    if search_name != "Wählen...":
        s_row = df_raw[df_raw.iloc[:, 0] == search_name]
        found_prio = False
        for d in range(1, 16):
            start_c = 1 + ((d - 1) * 9)
            besitz = sum(1 for i in range(9) if safe_int(s_row.iloc[0, start_c + i]) > 0)
            
            if 7 <= besitz < 9:
                found_prio = True
                status = "🚨 FINISHER!" if besitz == 8 else "⭐ FAST VOLL"
                st.markdown(f'<div class="prio-box"><span class="finisher-badge {"blink" if besitz==8 else ""}">{status}</span> &nbsp; <b>Deck {d} ({besitz}/9)</b></div>', unsafe_allow_html=True)
                
                for i in range(9):
                    c_n = df_raw.columns[start_c + i]
                    if safe_int(s_row.iloc[0, start_c + i]) == 0:
                        moegliche = [m for m in alle_gebot_dict.get(c_n, []) if m != search_name]
                        if moegliche:
                            for geber in moegliche:
                                r_key = f"{geber}_{c_n}"
                                # Callback Funktion für sofortiges Update
                                def on_change_res(k=r_key, n=search_name):
                                    if st.session_state[f"chk_{k}"]:
                                        st.session_state.reserviert[k] = n
                                    else:
                                        st.session_state.reserviert.pop(k, None)

                                st.checkbox(f"✅ {geber} hat `{c_n}`", 
                                            key=f"chk_{r_key}", 
                                            value=(r_key in st.session_state.reserviert),
                                            on_change=on_change_res)
                        else:
                            st.write(f"❌ Karte `{c_n}` fehlt (Kein Spender).")
        if not found_prio: st.info("Keine Decks bei 7/9 oder 8/9 gefunden.")

    # --- BEREICH 3: ADMIN ---
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.text_input("Admin-Code", type="password") == ADMIN_PASSWORT:
        if st.button("Alle Reservierungen löschen"):
            st.session_state.reserviert = {}; st.rerun()
        
        # Berechnung der restlichen Vorschläge unter Berücksichtigung der Reservierten
        gebot, bedarf = [], []
        for _, row in df_raw.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                bz = sum(1 for i in range(9) if safe_int(row.iloc[sc + i]) > 0)
                for i in range(9):
                    cn = df_raw.columns[sc + i]
                    # Filter: Ist dieser Geber für diese Karte gerade reserviert?
                    if safe_int(row.iloc[sc + i]) >= 2:
                        if f"{sp}_{cn}" not in st.session_state.reserviert:
                            gebot.append({"s": sp, "k": cn})
                    elif safe_int(row.iloc[sc + i]) == 0:
                        bedarf.append({"s": sp, "k": cn, "f": bz, "did": f"{sp}_D{d}"})

        # Sortieren: Finisher (8/9) nach oben
        bedarf = sorted(bedarf, key=lambda x: (x['f'], x['did']), reverse=True)
        
        def get_matches(is_dia):
            res, weg = [], set()
            fort = {b['did']: b['f'] for b in bedarf}
            for b in bedarf:
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        # Geber darf nicht reserviert sein UND darf in diesem Durchlauf noch nichts gegeben haben
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            akt = fort[b['did']]
                            if akt < 9:
                                label = "🚨 FINISHER!" if akt == 8 else f"({akt}/9)"
                                res.append(f"**{label}** {g['s']} ➔ {b['s']} ({b['k']})")
                                fort[b['did']] += 1; weg.add(g["s"])
                                break
            return res

        t1, t2 = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        with t1:
            m_g = get_matches(False)
            if m_g:
                for m in m_g: st.success(m)
            else: st.write("Keine weiteren Gold-Tausche möglich.")
        with t2:
            m_d = get_matches(True)
            if m_d:
                for m in m_d: st.info(m)
            else: st.write("Keine weiteren Diamant-Tausche möglich.")

except Exception as e: st.error(f"Fehler: {e}")
