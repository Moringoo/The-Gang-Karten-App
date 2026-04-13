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

# Belohnungstabelle für die Priorisierung (Kugeln als Wertfaktor)
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
    c1, c2 = st.columns(2)
    n_sel = c1.selectbox("Wer bist du?", ["Wählen..."] + namen)
    d_sel = c2.selectbox("Welches Deck?", list(range(1, 16)))
    
    if n_sel != "Wählen...":
        sz = df[df.iloc[:, 0] == n_sel]
        sc = 1 + ((d_sel - 1) * 9)
        db_vals = [safe_int(sz.iloc[0, sc + i]) for i in range(9)]
        st.subheader(f"🃏 Deck {d_sel} ({sum(1 for v in db_vals if v > 0)}/9)")
        neue_werte = []
        cols = st.columns(3) + st.columns(3) + st.columns(3)
        for i in range(9):
            with cols[i]:
                v = st.number_input(f"K{i+1}", 0, 9, value=db_vals[i], key=f"k_{n_sel}_{d_sel}_{i}")
                neue_werte.append(v)
        
        if st.button("🚀 SPEICHERN", use_container_width=True):
            w_str = ",".join([str(int(x)) for x in neue_werte])
            requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": w_str})
            st.balloons()
            time.sleep(1)
            st.rerun()

    # --- ADMIN BEREICH ---
    st.markdown("---")
    if st.text_input("Admin-Passwort", type="password") == ADMIN_PASSWORT:
        st.markdown("### 🎯 PROFIT-OPTIMIERTE TAUSCHVORSCHLÄGE")
        
        gbt, bdr = [], []
        for _, row in df.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                cols_deck = df.columns[sc:sc+9]
                dia_dichte = sum(1 for c in cols_deck if "(D)" in str(c))
                besitz = sum(1 for i in range(9) if safe_int(row.iloc[sc+i]) > 0)
                deck_wert = DECK_WERTE.get(d, 0)
                
                for i in range(9):
                    cn = df.columns[sc+i]
                    val = safe_int(row.iloc[sc+i])
                    if val >= 2: 
                        gbt.append({"s": sp, "k": cn})
                    elif val == 0: 
                        bdr.append({"s": sp, "k": cn, "f": besitz, "dichte": dia_dichte, "wert": deck_wert, "deck_nr": d})

        def process_trades(filter_dia):
            weg_geber = set()
            akt_bdr = [b for b in bdr if ("(D)" in b["k"]) == filter_dia]
            
            # Sortierung: 
            # 1. Finisher (f=8) zuerst
            # 2. Höchster Deck-Wert (Kugeln)
            # 3. Diamanten-Dichte
            akt_bdr = sorted(akt_bdr, key=lambda x: (x['f'], x['wert'], x['dichte']), reverse=True)
            
            results = []
            for b in akt_bdr:
                mögliche_geber = [g for g in gbt if g['k'] == b['k'] and g['s'] not in weg_geber and g['s'] != b["s"]]
                if mögliche_geber:
                    # Spezialisten-Check: Geber mit den wenigsten Gesamtangeboten zuerst nehmen
                    mögliche_geber.sort(key=lambda x: sum(1 for g2 in gbt if g2['s'] == x['s']))
                    best_g = mögliche_geber[0]
                    results.append((best_g, b))
                    weg_geber.add(best_g['s'])
            return results

        t_gold, t_dia = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        
        for tab, is_dia in zip([t_gold, t_dia], [False, True]):
            with tab:
                trades = process_trades(is_dia)
                if not trades: st.write("Keine Täusche möglich.")
                for g, b in trades:
                    # Info-Text für die Belohnung
                    kugeln = DECK_WERTE.get(b['deck_nr'], 0)
                    if b['f'] >= 8:
                        st.success(f"🌟 **FINISHER ({kugeln} Kugeln):** {g['k']} von {g['s']} ➔ {b['s']} (Deck {b['deck_nr']})")
                    else:
                        st.info(f"🤝 **TAUSCH ({kugeln} Kugeln):** {g['k']} von {g['s']} ➔ {b['s']} (Deck {b['deck_nr']})")
