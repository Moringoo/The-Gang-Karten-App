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
    .main-title { text-align: center; color: #fbbf24; font-size: 2.5rem; font-weight: bold; }
    .stat-card { background-color: #1f2937; padding: 10px; border-radius: 10px; border-top: 3px solid #fbbf24; text-align: center; }
    .missing-card { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

try:
    df_raw = pd.read_csv(SHEET_URL)
    df_raw = df_raw[df_raw.iloc[:, 0].notna()]
    df_raw = df_raw[df_raw.iloc[:, 0].str.strip() != ""]
    df_raw = df_raw[df_raw.iloc[:, 0].str.strip() != "Männlich"]
    spieler_namen = sorted(df_raw.iloc[:, 0].unique().tolist())

    st.markdown('<p class="main-title">THE GANG: HAUPTQUARTIER</p>', unsafe_allow_html=True)

    # --- NEU: EINZEL-ANALYSE (SUCHHILFE) ---
    st.markdown("### 🔍 GEZIELTE KARTENSUCHE")
    search_name = st.selectbox("Für wen suchen wir Karten?", ["Bitte wählen..."] + spieler_namen)
    
    if search_name != "Bitte wählen...":
        s_row = df_raw[df_raw.iloc[:, 0] == search_name]
        missing_list = []
        for d in range(1, 16):
            start_c = 1 + ((d - 1) * 9)
            current_deck_count = 0
            temp_missing = []
            for i in range(9):
                c_name = df_raw.columns[start_c + i]
                val = safe_int(s_row.iloc[0, start_c + i])
                if val > 0: current_deck_count += 1
                else: temp_missing.append(c_name)
            
            if current_deck_count >= 6: # Zeige nur Decks die fast voll sind
                missing_list.append({"deck": d, "count": current_deck_count, "cards": temp_missing})
        
        if missing_list:
            st.write(f"Hier sind die Karten, die **{search_name}** für seine besten Decks fehlen:")
            for item in missing_list:
                cols = st.columns([1, 4])
                cols[0].write(f"**Deck {item['deck']} ({item['count']}/9):**")
                cols[1].write(", ".join([f" `{c}`" for c in item['cards']]))
        else:
            st.info("Dieser Spieler hat noch keine Decks mit mindestens 6 Karten.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- ADMIN TAUSCH ANALYSE ---
    st.markdown("### 🕵️‍♂️ ADMIN-BEREICH")
    if st.text_input("Sicherheits-Code", type="password") == ADMIN_PASSWORT:
        gebot, bedarf = [], []
        for _, row in df_raw.iterrows():
            spieler = str(row.iloc[0]).strip()
            for d in range(1, 16):
                start_c = 1 + ((d - 1) * 9)
                besitz = sum(1 for i in range(9) if safe_int(row.iloc[start_c + i]) > 0)
                for i in range(9):
                    c_name = df_raw.columns[start_c + i]
                    anz = safe_int(row.iloc[start_c + i])
                    if anz >= 2: gebot.append({"s": spieler, "k": c_name})
                    elif anz == 0: bedarf.append({"s": spieler, "k": c_name, "f": besitz, "d_id": f"{spieler}_D{d}"})

        bedarf = sorted(bedarf, key=lambda x: (x['f'], x['d_id']), reverse=True)

        def get_matches(is_dia):
            results, weg_geber = [], set()
            fortschritt_tracker = {b['d_id']: b['f'] for b in bedarf}
            for b in bedarf:
                if (("(D)" in b["k"]) == is_dia):
                    found_match = False
                    for g in gebot:
                        if g["s"] not in weg_geber and g["s"] != b["s"] and g["k"] == b["k"]:
                            aktuell = fortschritt_tracker[b['d_id']]
                            if aktuell >= 9: continue
                            label = "🚨 FINISHER!" if aktuell == 8 else f"({aktuell}/9)"
                            results.append(f"**{label}** {g['s']} ➔ {b['s']} ({b['k']})")
                            fortschritt_tracker[b['d_id']] += 1
                            weg_geber.add(g["s"])
                            found_match = True
                            break
            return results

        t1, t2 = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        with t1:
            res_g = get_matches(False)
            if res_g: 
                for m in res_g: st.success(m)
            else: st.write("Keine Gold-Tausche möglich.")
        with t2:
            res_d = get_matches(True)
            if res_d:
                for m in res_d: st.info(m)
            else: st.write("Keine Diamant-Tausche möglich.")
            
except Exception as e:
    st.error(f"Fehler: {e}")
