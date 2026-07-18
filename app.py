import streamlit as st
import pandas as pd
import requests
import time

# --- 1. SETUP ---
st.set_page_config(page_title="The Gang HQ", page_icon="💀", layout="wide")

# --- 2. KONFIGURATION & WERTE ---
GID = "2025591169"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw71UB_1bRLELpRK1pzygSgV_uSxR4FHme1CRez4nC-80wGrwwORgYntwSyz0VofCs/exec" 
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
    cb = int(time.time()) 
    url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&cachebust={cb}"
    try:
        df = pd.read_csv(url, dtype=str)
        df = df[df.iloc[:, 0].notna()]
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return None

df = load_data()

if df is not None:
    st.title("💀 THE GANG HQ")

    # Namen in der Original-Reihenfolge des Sheets
    namen = [str(n).strip() for n in df.iloc[:, 0].unique() if str(n).strip() != ""]
    n_sel = st.selectbox("Wer bist du?", ["Wählen..."] + namen)
    
    if n_sel != "Wählen...":
        sz = df[df.iloc[:, 0].str.strip() == n_sel].copy()
        
        if sz.empty:
            st.warning("Spieler nicht gefunden.")
        else:
            st.markdown(f"### 📋 Deine Deck-Übersicht ({n_sel})")
            
            if st.button("🔄 DATEN FRISCH LADEN"):
                st.rerun()

            st.info("🎤 Gib die 9 Zahlen ein. Der Counter hilft dir beim Zählen!")
            
            alle_inputs = {}

            def save_all():
                erfolg = 0
                prozent_balken = st.progress(0)
                decks_to_save = list(alle_inputs.items())
                
                for i, (d_nr, werte_str) in enumerate(decks_to_save):
                    clean = "".join([c for c in werte_str if c.isdigit()]).ljust(9, '0')[:9]
                    w_send = ",".join(list(clean))
                    
                    sc_idx = 1 + ((d_nr - 1) * 9)
                    old_str = "".join([str(safe_int(sz.iloc[0, sc_idx + k])) for k in range(9)])
                    
                    if clean != old_str:
                        try:
                            requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_nr, "werte": w_send}, timeout=10)
                            erfolg += 1
                        except:
                            pass
                    
                    prozent_balken.progress((i + 1) / len(decks_to_save))

                st.balloons()
                st.success(f"Erfolgreich {erfolg} Decks aktualisiert!")
                time.sleep(2)
                st.rerun()

            if st.button("🚀 ALLE ÄNDERUNGEN SPEICHERN", use_container_width=True, key="save_top"):
                save_all()

            st.markdown("---")
            
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                if sc + 8 < len(sz.columns):
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
                        val = st.text_input(
                            f"Zahlen D{d}", value=current_str, key=f"in_d{d}_{n_sel}", label_visibility="collapsed"
                        )
                        alle_inputs[d] = val
                        
                        count = len(val)
                        if count == 9:
                            st.markdown(f"<p style='color:green; font-size:12px; margin-top:-10px;'>✅ 9 Zeichen</p>", unsafe_allow_html=True)
                        elif count < 9:
                            st.markdown(f"<p style='color:orange; font-size:12px; margin-top:-10px;'>⚠️ {count}/9 Zeichen</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='color:red; font-size:12px; margin-top:-10px;'>❌ Zu viele! ({count}/9)</p>", unsafe_allow_html=True)

            st.markdown("---")
            if st.button("🚀 ALLE ÄNDERUNGEN SPEICHERN", use_container_width=True, key="save_bottom"):
                save_all()

    # --- ADMIN BEREICH ---
    st.markdown("---")
    pwd = st.text_input("Admin-Passwort für Tauschanalyse", type="password")
    if pwd == ADMIN_PASSWORT:
        st.markdown("### 🎯 PRIORISIERTE TAUSCHLISTE (Fortschritt vor Kugeln)")
        gbt, bdr = [], []
        for _, row in df.iterrows():
            sp = str(row.iloc[0]).strip()
            if sp.lower() in ["vorlage", ""]:
                continue
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9) 
                if sc+8 < len(df.columns):
                    cols_deck = df.columns[sc:sc+9]
                    dia_dichte = sum(1 for c in cols_deck if "(D)" in str(c))
                    besitz = sum(1 for i in range(9) if safe_int(row.iloc[sc+i]) > 0)
                    deck_wert = DECK_WERTE.get(d, 0)
                    
                    if besitz == 8: f_bonus = 10000000
                    elif besitz == 7: f_bonus = 1000000
                    elif besitz == 6: f_bonus = 100000
                    else: f_bonus = besitz * 1000 
                    
                    score = f_bonus + deck_wert + (dia_dichte * 10)
                    
                    for i in range(9):
                        cn = df.columns[sc+i]
                        val = safe_int(row.iloc[sc+i])
                        if val >= 2: gbt.append({"s": sp, "k": cn})
                        elif val == 0: bdr.append({
                            "s": sp, "k": cn, "f": besitz, "dichte": dia_dichte, 
                            "wert": deck_wert, "deck_nr": d, "score": score
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

        t1, t2 = st.tabs(["🌕 GOLD", "💎 DIAMANT"])
        for tab, is_dia in zip([t1, t2], [False, True]):
            with tab:
                trades = process_trades(is_dia)
                if not trades: st.write("Keine Täusche verfügbar.")
                else:
                    for g, b in trades:
                        k_bel = DECK_WERTE.get(b['deck_nr'], 0)
                        
                        # Extrahiere Kartennummer kompakt aus Spaltenname (z.B. aus D1-K8 wird K8)
                        k_short = b['k'].split('-')[-1] if '-' in b['k'] else b['k']
                        
                        if b['f'] >= 8: 
                            st.success(f"🔥 **PRIO 1 (8/9):** D{b['deck_nr']}, {k_short} von {g['s']} ➔ {b['s']} ({k_bel} K.)")
                        elif b['f'] == 7:
                            st.info(f"⭐ **PRIO 2 (7/9):** D{b['deck_nr']}, {k_short} von {g['s']} ➔ {b['s']} ({k_bel} K.)")
                        elif b['f'] == 6:
                            st.warning(f"📈 **PRIO 3 (6/9):** D{b['deck_nr']}, {k_short} von {g['s']} ➔ {b['s']} ({k_bel} K.)")
                        else:
                            st.write(f"🤝 **Tausch:** D{b['deck_nr']}, {k_short} von {g['s']} ➔ {b['s']} ({k_bel} K.)")
