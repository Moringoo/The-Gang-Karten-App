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

    # --- 🚨 FINISHER-ALARM (DIE DIREKTEN TAUSCH-ANWEISUNGEN) ---
    st.markdown("### 🚨 FINISHER: DRINGEND POSTEN!")
    
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

    finisher_count = 0
    weg_finisher = set()
    
    # Wir suchen hier NUR nach Leuten, die 8/9 haben und eine Karte brauchen
    for b in bdr:
        if b["f"] == 8: # Er hat 8 und braucht die 9. Karte
            for g in gbt:
                if g["s"] not in weg_finisher and g["s"] != b["s"] and g["k"] == b["k"]:
                    # DAS IST DEIN FORMAT: Finisher: Karte von Geber an Nehmer
                    st.error(f"📢 **FINISHER:** mit **{g['k']}** von **{g['s']}** an **{b['s']}**! (Bringt ihn auf 9/9)")
                    weg_finisher.add(g["s"])
                    finisher_count += 1
                    break
    
    if finisher_count == 0:
        st.info("Aktuell keine Täusche für einen direkten Deck-Abschluss (9/9) möglich.")

    st.markdown("---")

    # --- BEARBEITUNGS-BEREICH ---
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
        for r_idx in range(3):
            cols = st.columns(3)
            for c_idx in range(3):
                i = r_idx * 3 + c_idx
                with cols[c_idx]:
                    v = st.number_input(f"Karte {i+1}", 0, 9, value=db_vals[i], key=f"k{i}_{n_sel}_{d_sel}")
                    neue_werte.append(v)
        
        if st.button("🚀 SPEICHERN"):
            w_str = ",".join([str(int(x)) for x in neue_werte])
            r = requests.get(SCRIPT_URL, params={"name": n_sel, "deck": d_sel, "werte": w_str})
            st.balloons()
            st.cache_data.clear()
            st.rerun()

    # --- NORMALE TAUSCHVORSCHLÄGE (ADMIN) ---
    st.markdown("---")
    if st.text_input("Admin-Passwort", type="password") == ADMIN_PASSWORT:
        st.markdown("### 🤝 Weitere Tauschvorschläge")
        t1, t2 = st.tabs(["Gold", "Diamant"])
        for tab, is_d in zip([t1, t2], [False, True]):
            with tab:
                weg = set()
                for b in sorted(bdr, key=lambda x: x['f'], reverse=True):
                    if (("(D)" in b["k"]) == is_d) and b["f"] < 8: # Nur "normale" Täusche
                        for g in gbt:
                            if g["s"] not in weg and g["s"] != b["s"] and g["k"] == b["k"]:
                                st.write(f"{g['k']}: {g['s']} ➔ {b['s']} ({b['f']}/9)")
                                weg.add(g["s"])
                                break
