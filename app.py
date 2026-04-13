import streamlit as st
import pandas as pd
import requests
import time
import random

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION ---
GID = "2025591169"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzqvISwbnj74Ab7_NO5X3AeeHyvDeWFNFREiWd420_QBdlKyMWaNI6ZL9I0wyoLjEI/exec" 
ADMIN_PASSWORT = "gang2026" 

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
        st.markdown("### 🎯 INTELLIGENTE TAUSCH-OPTIMIERUNG")
        
        gbt, bdr = [], []
        # 1. Alle Gebote und Bedarfe sammeln
        for _, row in df.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                cols_deck = df.columns[sc:sc+9]
                dia_dichte = sum(1 for c in cols_deck if "(D)" in str(c))
                besitz = sum(1 for i in range(9) if safe_int(row.iloc[sc+i]) > 0)
                for i in range(9):
                    cn = df.columns[sc+i]
                    val = safe_int(row.iloc[sc+i])
                    if val >= 2: gbt.append({"s": sp, "k": cn})
                    elif val == 0: bdr.append({"s": sp, "k": cn, "f": besitz, "dichte": dia_dichte})

        # 2. KNAPPHEITS-CHECK: Wie viele Leute können Karte X geben?
        knappheit = {}
        for g in gbt:
            knappheit[g['k']] = knappheit.get(g['k'], 0) + 1

        # 3. Tausche zuweisen (Spezialisten zuerst!)
        def process_trades(filter_dia):
            weg_geber = set()
            # Sortierung: 
            # 1. Höchster Füllstand (f) 
            # 2. Meiste Dia-Karten (dichte)
            # 3. SELTENSTE Karte zuerst (knappheit) -> Damit Joker für andere Decks frei bleiben
            akt_bdr = [b for b in bdr if ("(D)" in b["k"]) == filter_dia]
            akt_bdr = sorted(akt_bdr, key=lambda x: (x['f'], x['dichte']), reverse=True)
            
            results = []
            for b in akt_bdr:
                # Finde alle Geber für diese Karte, die noch nicht weg sind
                mögliche_geber = [g for g in gbt if g['k'] == b['k'] and g['s'] not in weg_geber and g['s'] != b['s']]
                
                if mögliche_geber:
                    # Nimm den Geber, der am WENIGSTEN andere Karten anbieten kann (Spezialist)
                    # Oder einfach den ersten, da die Knappheit der Karte selbst schon durch die 'bdr'-Sortierung oben indirekt fließt
                    # Wir sortieren die Geber hier nach der Anzahl ihrer Gesamtgebote
                    mögliche_geber.sort(key=lambda x: sum(1 for g2 in gbt if g2['s'] == x['s']))
                    
                    best_g = mögliche_geber[0]
                    results.append((best_g, b))
                    weg_geber.add(best_g['s'])
            return results

        t_gold, t_dia = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        
        for tab, is_dia in zip([t_gold, t_dia], [False, True]):
            with tab:
                trades = process_trades(is_dia)
                if not trades: st.write("Keine optimierten Tausche möglich.")
                for g, b in trades:
                    label = "💰 ERTRAGREICH" if b['dichte'] >= 3 else ("💎 DIA" if is_dia else "🌕 GOLD")
                    if b['f'] >= 8:
                        st.success(f"🌟 **FINISHER:** {g['k']} von {g['s']} ➔ {b['s']} ({b['f']}/9)")
                    else:
                        st.info(f"🤝 **{label}:** {g['k']} von {g['s']} ➔ {b['s']} ({b['f']}/9)")
