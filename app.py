import streamlit as st
import pandas as pd
import requests
import time
import re

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ Final", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION ---
GID = "2025591169"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaIWcjmJ5Nn5MsRR66ptz97MBjJ-S0O-B7TVp1Y4pq81Xc1Q0VLNzDFWDn6c9NcB4/exec" 
ADMIN_PASSWORT = "gang2026" 

def safe_int(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan": return 0
        return int(float(str(val).replace(',', '.')))
    except: return 0

# --- 3. SESSION STATE ---
if "form_iter" not in st.session_state:
    st.session_state.form_iter = 0

# Hilfsfunktion zum kompletten Aufräumen
def trigger_reset():
    st.session_state.form_iter += 1
    # Alle temporären Werte löschen, damit wieder die DB-Werte geladen werden
    for i in range(9):
        key = f"voice_val_{i}"
        if key in st.session_state:
            del st.session_state[key]

# --- 4. DATEN LADEN ---
def load_data():
    try:
        # Timestamp verhindert Cache-Probleme bei Google
        url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&t={int(time.time())}"
        df = pd.read_csv(url, dtype={0: str})
        # Nur Zeilen mit Namen behalten
        df = df[df.iloc[:, 0].notna() & (df.iloc[:, 0].str.strip() != "")]
        # Platzhalter raus
        df = df[~df.iloc[:, 0].str.strip().str.lower().isin(['leer', 'platzhalter'])]
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return None

# --- 5. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-title { text-align: center; color: #fbbf24; font-size: 2.2rem; font-weight: bold; margin-bottom: 10px; }
    .voice-area { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 2px solid #3b82f6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. HAUPT-LOGIK ---
df_aktuell = load_data()

if df_aktuell is not None:
    # Namen bleiben in Sheet-Reihenfolge
    spieler_namen = df_aktuell.iloc[:, 0].unique().tolist()
    st.markdown('<p class="main-title">💀 THE GANG: HQ FINAL</p>', unsafe_allow_html=True)

    # --- EINGABE-BEREICH ---
    st.markdown("### 📝 KARTEN AKTUALISIEREN")
    col1, col2 = st.columns(2)
    # Bei Namen- oder Deckwechsel alles auf Null setzen
    n_sel = col1.selectbox("Wer bist du?", ["Wählen..."] + spieler_namen, on_change=trigger_reset)
    d_sel = col2.selectbox("Welches Deck?", list(range(1, 16)), on_change=trigger_reset)
    
    if n_sel != "Wählen...":
        s_zeile = df_aktuell[df_aktuell.iloc[:, 0] == n_sel]
        if len(s_zeile) > 0:
            start_c = 1 + ((d_sel - 1) * 9)
            sheet_vals = [safe_int(s_zeile.iloc[0, start_c + i]) for i in range(9)]

            # VOICE-EINGABE
            st.markdown('<div class="voice-area">', unsafe_allow_html=True)
            v_input = st.text_input("Zahlenkette eingeben (z.B. 121002111) & ENTER:", key=f"v_in_{st.session_state.form_iter}")
            
            # Wenn eine Kette eingegeben wurde, sofort in den State schreiben und Seite neu laden
            if v_input:
                digits = re.findall(r'\d', v_input)
                if len(digits) >= 9:
                    for i in range(9):
                        st.session_state[f"voice_val_{i}"] = int(digits[i])
                    # WICHTIG: Das Textfeld leeren für die nächste Eingabe
                    st.session_state.form_iter += 1 
                    st.rerun() # Zwingt die Boxen unten, die neuen Werte zu übernehmen
                else:
                    st.warning(f"⚠️ Nur {len(digits)} von 9 Zahlen erkannt.")
            st.markdown('</div>', unsafe_allow_html=True)

            # 3x3 RASTER
            neue_werte = []
            cols = st.columns(3) + st.columns(3) + st.columns(3)
            
            for i in range(9):
                with cols[i]:
                    # Checke erst, ob eine Spracheingabe vorliegt
                    if f"voice_val_{i}" in st.session_state:
                        val_to_show = st.session_state[f"voice_val_{i}"]
                    else:
                        val_to_show = sheet_vals[i]
                    
                    # Widget mit dynamischem Key
                    res_val = st.number_input(f"K{i+1}", 0, 9, value=val_to_show, key=f"k_input_{i}_{st.session_state.form_iter}")
                    neue_werte.append(res_val)
            
            if st.button("🚀 ÄNDERUNGEN SPEICHERN", use_container_width=True):
                werte_str = ",".join([str(v) for v in neue_werte])
                # Absenden an Google Script
                try:
                    requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": werte_str})
                    st.balloons()
                    st.success("Erfolgreich im Sheet gespeichert!")
                    trigger_reset() # Alles putzen für die nächste Runde
                    time.sleep(1)
                    st.rerun()
                except:
                    st.error("Fehler beim Senden an Google. Bitte nochmal versuchen.")

    # --- ANALYSE-BEREICH ---
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.text_input("Admin-Passwort", type="password") == ADMIN_PASSWORT:
        if st.button("🔄 DATEN ERNEUT LADEN"):
            st.rerun()
            
        st.markdown("### 🕵️‍♂️ TAUSCH-CHECK (Live-Daten)")
        gebot, bedarf = [], []
        
        for _, row in df_aktuell.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                bz, dia = 0, 0
                for i in range(9):
                    val = safe_int(row.iloc[sc + i])
                    if val > 0: bz += 1
                    if "(D)" in df_aktuell.columns[sc + i]: dia += 1
                for i in range(9):
                    cn = df_aktuell.columns[sc + i]
                    v_val = safe_int(row.iloc[sc + i])
                    if v_val >= 2:
                        gebot.append({"s": sp, "k": cn})
                    elif v_val == 0:
                        bedarf.append({"s": sp, "k": cn, "f": bz, "d": dia})

        bedarf = sorted(bedarf, key=lambda x: (x['f'], x['d']), reverse=True)
        
        def get_matches(is_dia):
            res, weg = [], set()
            for b in bedarf:
                if (("(D)" in b["k"]) == is_dia):
                    for g in gebot:
                        if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                            l = "**🚨 FINISHER!**" if b['f'] == 8 else f"({b['f']}/9)"
                            res.append(f"{l} {g['s']} ➔ {b['s']} ({g['k']})")
                            weg.add(g["s"])
                            break
            return res

        t1, t2 = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        with t1:
            for m in get_matches(False): st.success(m)
        with t2:
            for m in get_matches(True): st.info(m)
