import streamlit as st
import pandas as pd
import requests
import time
import random

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION & WERTE ---
GID = "2025591169"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzqvISwbnj74Ab7_NO5X3AeeHyvDeWFNFREiWd420_QBdlKyMWaNI6ZL9I0wyoLjEI/exec" 
ADMIN_PASSWORT = "gang2026" 

# Belohnungstabelle (Munition)
DECK_WERTE = {
    1: 500, 2: 550, 3: 750, 4: 1000, 5: 1600, 
    6: 2500, 7: 3000, 8: 4000, 9: 4500, 10: 6000, 
    11: 6500, 12: 10000, 13: 1500, 14: 4000, 15: 6100
}

def safe_int(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan": return 0
        return int(float(str(val).replace(',', '.')))
    except: return 0

def load_data():
    cb = random.randint(1, 1000000)
    url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&cb={cb}"
    try:
        df = pd.read_csv(url, dtype={0: str})
        return df[df.iloc[:, 0].notna()]
    except: return None

df = load_data()

if df is not None:
    st.title("💀 THE GANG HQ")

    # --- SPIELER-BEREICH ---
    namen = df.iloc[:, 0].unique().tolist()
    n_sel = st.selectbox("Wer bist du?", ["Wählen..."] + namen)
    
    if n_sel != "Wählen...":
        st.markdown(f"### 📋 Deine Deck-Übersicht ({n_sel})")
        st.info("🎤 Sprich oder tippe die **9 Zahlen** für dein Deck hintereinander weg.")
        
        sz = df[df.iloc[:, 0] == n_sel]
        
        # Alle 15 Decks untereinander
        for d in range(1, 16):
            sc = 1 + ((d - 1) * 9)
            current_vals = [safe_int(sz.iloc[0, sc + i]) for i in range(9)]
            besitz = sum(1 for v in current_vals if v > 0)
            fehlen = 9 - besitz
            current_str = "".join([str(v) for v in current_vals])
            
            # Layout Zeile
            c1, c2, c3 = st.columns([2, 3, 2])
            
            with c1:
                st.markdown(f"**DECK {d}**")
                # Hier ist die gewünschte Anzeige: z.B. 3/9 (noch 6 fehlen)
                st.caption(f"Status: {besitz}/9 (noch {fehlen} fehlen) | {DECK_WERTE.get(d)} Kugeln")
            
            with c2:
                user_input = st.text_input(
                    f"Zahlen Deck {d}", 
                    value=current_str, 
                    key=f"input_d{d}_{n_sel}", 
                    label_visibility="collapsed"
                )
            
            with c3:
                if st.button(f"💾 Speichern", key=f"save_d{d}_{n_sel}"):
                    clean_input = "".join([c for c in user_input if c.isdigit()])
                    clean_input = clean_input.ljust(9, '0')[:9]
                    w_str = ",".join(list(clean_input))
                    
                    with st.spinner("Sheet wird aktualisiert..."):
                        try:
                            requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d, "werte": w_str}, timeout=5)
                            st.success(f"Deck {d} OK!")
                            time.sleep(0.5)
                            st.rerun()
                        except:
                            st.warning("Verbindung hakt – kurz warten.")
                            time.sleep(1)
                            st.rerun()

    # --- ADMIN BEREICH ---
    st.markdown("---")
    pwd = st.text_input("Admin-Bereich (Passwort)", type="password")
    if pwd == ADMIN_PASSWORT:
        st.markdown("### 🎯 PRIORISIERTE TAUSCHLISTE")
        
        gbt, bdr = [], []
        for _, row in df.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9) 
                cols_deck = df.columns[sc:sc+9]
                dia_dichte = sum(1 for c in cols_deck if "(D)" in str(c))
                besitz = sum(1 for i in range(9) if safe_int(row.iloc[sc+i]) > 0)
                deck_wert = DECK_WERTE.get(d, 0)
                
                # Finisher bei 8 von 9 Karten
                f_bonus = 1000000 if besitz >= 8 else (besitz * 1000)
                score = f_bonus + deck_wert + (dia_dichte * 10)

                for i in range(9):
                    cn = df.columns[sc+i]
                    val = safe_int(row.iloc[sc+i])
                    if val >= 2: 
                        gbt.append({"s": sp, "k": cn})
                    elif val == 0: 
                        bdr.append({
                            "s": sp, "k": cn, "f": besitz, 
                            "dichte": dia_dichte, "wert": deck_wert, 
                            "deck_nr": d, "score": score
                        })

        def process_trades(filter_dia):
            weg_geber = set()
            akt_bdr = [b for b in bdr if ("(D)" in b["k"]) == filter_dia]
            akt_bdr = sorted(akt_bdr, key=lambda x: x['score'], reverse=True)
            results = []
            for b in akt_bdr:
                mögliche_geber = [g for g in gbt if g['k'] == b['k'] and g['s'] not in weg_geber and g['s'] != b["s"]]
                if mögliche_geber:
                    mögliche_geber.sort(key=lambda x: sum(1 for g2 in gbt if g2['s'] == x['s']))
                    best_g = mögliche_geber[0]
                    results.append((best_g, b))
                    weg_geber.add(best_g['s'])
            return results

        t_gold, t_dia = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        for tab, is_dia in zip([t_gold, t_dia], [False, True]):
            with tab:
                trades = process_trades(is_dia)
                if not trades:
                    st.write("Keine Täusche verfügbar.")
                else:
                    for g, b in trades:
                        kugeln = DECK_WERTE.get(b['deck_nr'], 0)
                        if b['f'] >= 8:
                            st.success(f"🌟 **FINISHER ({kugeln} Kugeln):** {g['k']} von {g['s']} ➔ {b['s']} (D{b['deck_nr']})")
                        else:
                            st.info(f"🤝 **TAUSCH ({kugeln} Kugeln):** {g['k']} von {g['s']} ➔ {b['s']} (D{b['deck_nr']})")
