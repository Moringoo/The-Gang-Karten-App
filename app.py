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

# --- 3. DATEN LADEN ---
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
        st.markdown("### 🎯 PRIORISIERTE TAUSCHVORSCHLÄGE")
        
        gbt, bdr = [], []
        # Analyse der Decks auf Diamanten-Dichte
        for _, row in df.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                cols_deck = df.columns[sc:sc+9]
                
                # Wie viele Diamanten-Karten hat dieses Deck INSGESAMT laut Header?
                dia_dichte = sum(1 for c in cols_deck if "(D)" in str(c))
                # Wie viele Karten hat der Spieler bereits?
                besitz = sum(1 for i in range(9) if safe_int(row.iloc[sc+i]) > 0)
                
                for i in range(9):
                    cn = df.columns[sc+i]
                    val = safe_int(row.iloc[sc+i])
                    if val >= 2: 
                        gbt.append({"s": sp, "k": cn})
                    elif val == 0: 
                        # Wir speichern die 'dia_dichte' als Prioritäts-Faktor
                        bdr.append({"s": sp, "k": cn, "f": besitz, "dichte": dia_dichte})

        t_gold, t_dia = st.tabs(["🌕 GOLD", "💎 DIAMANT (Prio: Hoher Ertrag)"])
        
        with t_gold:
            weg_g = set()
            bdr_g = sorted([b for b in bdr if "(D)" not in b["k"]], key=lambda x: x['f'], reverse=True)
            for b in bdr_g:
                for g in gbt:
                    if "(D)" not in g["k"] and g["s"] not in weg_g and g["s"] != b["s"] and g["k"] == b["k"]:
                        st.write(f"🤝 **{g['k']}**: {g['s']} ➔ {b['s']} ({b['f']}/9)")
                        weg_g.add(g["s"])
                        break

        with t_dia:
            weg_d = set()
            # SORTIERUNG: Erst nach Füllstand (f), dann nach Diamanten-Dichte (dichte)
            bdr_d = sorted([b for b in bdr if "(D)" in b["k"]], 
                           key=lambda x: (x['f'], x['dichte']), reverse=True)
            
            for b in bdr_d:
                for g in gbt:
                    if "(D)" in g["k"] and g["s"] not in weg_d and g["s"] != b["s"] and g["k"] == b["k"]:
                        # Anzeige wie viel "Wert" das Deck hat
                        label = "💰 HOHER ERTRAG" if b['dichte'] >= 3 else "💎 DIAMANT"
                        if b['f'] >= 8:
                            st.success(f"🌟 **FINISHER ({label}):** {g['k']} von {g['s']} ➔ {b['s']} ({b['f']}/9)")
                        else:
                            st.info(f"🔥 **{label}:** {g['k']} von {g['s']} ➔ {b['s']} ({b['f']}/9 - {b['dichte']} Dia-Karten im Deck)")
                        
                        weg_d.add(g["s"])
                        break
