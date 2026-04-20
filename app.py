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

    namen = df.iloc[:, 0].unique().tolist()
    n_sel = st.selectbox("Wer bist du?", ["Wählen..."] + namen)
    
    if n_sel != "Wählen...":
        st.markdown(f"### 📋 Deine Deck-Übersicht ({n_sel})")
        st.info("🎤 Bearbeite alle Decks (Sprache/Tippen) und klicke dann auf den großen Speicher-Button.")
        
        sz = df[df.iloc[:, 0] == n_sel]
        alle_inputs = {}

        # Zentrale Speicher-Funktion
        def save_all():
            erfolg = 0
            with st.spinner("Übertrage alle Daten an das HQ..."):
                for d_nr, werte_str in alle_inputs.items():
                    clean = "".join([c for c in werte_str if c.isdigit()]).ljust(9, '0')[:9]
                    w_send = ",".join(list(clean))
                    try:
                        requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_nr, "werte": w_send}, timeout=8)
                        erfolg += 1
                    except:
                        pass
            if erfolg > 0:
                st.balloons()
                st.success(f"Mission erfüllt! {erfolg} Decks wurden im Sheet aktualisiert.")
                time.sleep(2)
                st.rerun()

        # Oberer Button für schnellen Zugriff
        if st.button("🚀 ALLE ÄNDERUNGEN SPEICHERN", use_container_width=True, key="save_top"):
            save_all()

        st.markdown("---")
        
        for d in range(1, 16):
            sc = 1 + ((d - 1) * 9)
            current_vals = [safe_int(sz.iloc[0, sc + i]) for i in range(9)]
            besitz = sum(1 for v in current_vals if v > 0)
            fehlen = 9 - besitz
            current_str = "".join([str(v) for v in current_vals])
            kugeln = DECK_WERTE.get(d, 0)
            
            c1, c2 = st.columns([3, 4])
            with c1:
                st.markdown(f"**DECK {d}**")
                st.caption(f"Status: {besitz}/9 (noch {fehlen} fehlen) | 💰 {kugeln} Kugeln")
            with c2:
                alle_inputs[d] = st.text_input(
                    f"Eingabe D{d}", value=current_str, key=f"in_d{d}", label_visibility="collapsed"
                )

        st.markdown("---")
        # Unterer Button (falls man ganz nach unten gescrollt hat)
        if st.button("🚀 ALLE ÄNDERUNGEN SPEICHERN", use_container_width=True, key="save_bottom"):
            save_all()

    # --- ADMIN BEREICH ---
    st.markdown("---")
    pwd = st.text_input("Admin-Passwort für Tauschanalyse", type="password")
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
                f_bonus = 1000000 if besitz >= 8 else (besitz * 1000)
                score = f_bonus + deck_wert + (dia_dichte * 10)
                for i in range(9):
                    cn = df.columns[sc+i]
                    val = safe_int(row.iloc[sc+i])
                    if val >= 2: gbt.append({"s": sp, "k": cn})
                    elif val == 0: bdr.append({"s": sp, "k": cn, "f": besitz, "dichte": dia_dichte, "wert": deck_wert, "deck_nr": d, "score": score})

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
                if not trades: st.write("Keine Täusche verfügbar.")
                else:
                    for g, b in trades:
                        k_belohnung = DECK_WERTE.get(b['deck_nr'], 0)
                        if b['f'] >= 8: st.success(f"🌟 **FINISHER ({k_belohnung} Kugeln):** {g['k']} von {g['s']} ➔ {b['s']} (D{b['deck_nr']})")
                        else: st.info(f"🤝 **TAUSCH ({k_belohnung} Kugeln):** {g['k']} von {g['s']} ➔ {b['s']} (D{b['deck_nr']})")
