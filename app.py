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

# --- 3. DATEN LADEN (Aggressiver Cache-Bust) ---
def load_data():
    # Wir hängen eine Zufallszahl an, damit Google NIEMALS eine alte Datei schickt
    cache_buster = random.randint(1, 1000000)
    url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&cb={cache_buster}"
    try:
        df = pd.read_csv(url, dtype={0: str})
        return df[df.iloc[:, 0].notna()]
    except:
        return None

# Wir laden die Daten bei jedem Skript-Durchlauf komplett neu (kein st.cache_data)
df = load_data()

if df is not None:
    st.title("💀 THE GANG HQ")

    # --- OBEN: SPIELER-BEREICH ---
    namen = df.iloc[:, 0].unique().tolist()
    c1, c2 = st.columns(2)
    n_sel = c1.selectbox("Wer bist du?", ["Wählen..."] + namen)
    d_sel = c2.selectbox("Welches Deck?", list(range(1, 16)))
    
    if n_sel != "Wählen...":
        sz = df[df.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        db_vals = [safe_int(sz.iloc[0, start_c + i]) for i in range(9)]
        
        st.subheader(f"🃏 Deck {d_sel} ({sum(1 for v in db_vals if v > 0)}/9)")
        neue_werte = []
        cols = st.columns(3) + st.columns(3) + st.columns(3)
        for i in range(9):
            with cols[i]:
                v = st.number_input(f"K{i+1}", 0, 9, value=db_vals[i], key=f"k_{n_sel}_{d_sel}_{i}")
                neue_werte.append(v)
        
        if st.button("🚀 SPEICHERN", use_container_width=True):
            w_str = ",".join([str(int(x)) for x in neue_werte])
            with st.spinner("Übertrage an Google..."):
                try:
                    # Wir warten kurz, bis das Script fertig ist
                    requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": w_str}, timeout=15)
                    st.balloons()
                    time.sleep(1) # Kurze Pause für Google
                    st.rerun()
                except:
                    st.error("Verbindung zum Sheet unterbrochen.")

    # --- UNTEN: ADMIN BEREICH (KLAPPT NUR BEI PASSWORT AUF) ---
    st.markdown("---")
    admin_input = st.text_input("Admin-Passwort für Tauschanalyse", type="password")
    
    if admin_input == ADMIN_PASSWORT:
        st.markdown("### 🎯 AKTUELLE TAUSCH-PRIORITÄTEN")
        
        gbt, bdr = [], []
        for _, row in df.iterrows():
            sp = str(row.iloc[0]).strip()
            for d in range(1, 16):
                sc = 1 + ((d - 1) * 9)
                besitz = sum(1 for i in range(9) if safe_int(row.iloc[sc+i]) > 0)
                for i in range(9):
                    cn = df.columns[sc+i]
                    val = safe_int(row.iloc[sc+i])
                    if val >= 2: gbt.append({"s": sp, "k": cn})
                    elif val == 0: bdr.append({"s": sp, "k": cn, "f": besitz})

        t_gold, t_dia = st.tabs(["🌕 GOLD KARTEN", "💎 DIAMANT KARTEN"])
        
        for tab, is_d in zip([t_gold, t_dia], [False, True]):
            with tab:
                weg, found = set(), False
                bdr_s = sorted(bdr, key=lambda x: x['f'], reverse=True)
                for b in bdr_s:
                    if (("(D)" in b["k"]) == is_d):
                        for g in gbt:
                            if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                                if b['f'] == 8:
                                    st.success(f"🌟 **FINISHER:** mit **{g['k']}** von **{g['s']}** an **{b['s']}** (9/9)")
                                elif b['f'] == 7:
                                    st.info(f"🚀 **PRIO 1:** mit **{g['k']}** von **{g['s']}** an **{b['s']}** (8/9)")
                                else:
                                    st.write(f"🤝 **Tausch:** mit **{g['k']}** von **{g['s']}** an **{b['s']}** ({b['f']}/9)")
                                weg.add(g["s"])
                                found = True
                                break
                if not found: st.write("Keine Täusche verfügbar.")
