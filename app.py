import streamlit as st
import pandas as pd
import requests
import time

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

@st.cache_data(ttl=5) 
def load_data(ts):
    try:
        url = f"https://docs.google.com/spreadsheets/d/1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo/export?format=csv&gid={GID}&t={ts}"
        df = pd.read_csv(url, dtype={0: str})
        return df[df.iloc[:, 0].notna()]
    except: return None

df = load_data(int(time.time() / 5))

if df is not None:
    st.title("💀 THE GANG HQ")

    # --- 🎯 TAUSCH-PRIORITÄTEN (ALLES AUF EINEN BLICK) ---
    st.markdown("### 📋 TAUSCH-LISTE (Nach Priorität)")
    
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

    # Sortieren: Wer am weitesten ist (8/9, dann 7/9...), kommt zuerst
    bdr_sorted = sorted(bdr, key=lambda x: x['f'], reverse=True)
    
    weg = set()
    found_any = False
    
    # Wir zeigen hier ALLES an, was möglich ist, sortiert nach Fortschritt
    for b in bdr_sorted:
        for g in gbt:
            if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                # Formatierung je nach Wichtigkeit
                if b["f"] == 8:
                    st.success(f"🌟 **FINISHER:** mit **{g['k']}** von **{g['s']}** an **{b['s']}** (9/9)")
                elif b["f"] == 7:
                    st.info(f"🚀 **PRIO 1:** mit **{g['k']}** von **{g['s']}** an **{b['s']}** (8/9)")
                elif b["f"] == 6:
                    st.warning(f"📈 **PRIO 2:** mit **{g['k']}** von **{g['s']}** an **{b['s']}** (7/9)")
                else:
                    st.write(f"🤝 **Tausch:** mit **{g['k']}** von **{g['s']}** an **{b['s']}** ({b['f']+1}/9)")
                
                weg.add(g["s"])
                found_any = True
                break
    
    if not found_any:
        st.write("Aktuell keine Tauschmöglichkeiten gefunden.")

    st.markdown("---")

    # --- BEARBEITUNGS-BEREICH ---
    namen = df.iloc[:, 0].unique().tolist()
    c1, c2 = st.columns(2)
    with c1: n_sel = st.selectbox("Wer bist du?", ["Wählen..."] + namen)
    with c2: d_sel = st.selectbox("Welches Deck?", list(range(1, 16)))
    
    if n_sel != "Wählen...":
        sz = df[df.iloc[:, 0] == n_sel]
        start_c = 1 + ((d_sel - 1) * 9)
        db_vals = [safe_int(sz.iloc[0, start_c + i]) for i in range(9)]
        
        st.subheader(f"🃏 Deck {d_sel} ({sum(1 for v in db_vals if v > 0)}/9)")
        neue_werte = []
        for r_idx in range(3):
            cols = st.columns(3)
            for c_idx in range(3):
                i = r_idx * 3 + col_idx
                with cols[c_idx]:
                    v = st.number_input(f"Karte {i+1}", 0, 9, value=db_vals[i], key=f"k{i}_{n_sel}_{d_sel}")
                    neue_werte.append(v)
        
        if st.button("🚀 SPEICHERN", use_container_width=True):
            w_str = ",".join([str(int(x)) for x in neue_werte])
            requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": w_str})
            st.balloons()
            st.cache_data.clear()
            st.rerun()

    # --- ADMIN / GOLD-DIAMANT FILTER ---
    st.markdown("---")
    if st.text_input("Admin-Passwort für Filter", type="password") == ADMIN_PASSWORT:
        st.info("Oben siehst du bereits alle Täusche sortiert. Nutze Tabs für gezielte Suche:")
        t1, t2 = st.tabs(["Nur Gold", "Nur Diamant"])
        # (Hier könnten bei Bedarf noch gefilterte Listen stehen)
