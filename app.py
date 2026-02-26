import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang: Live-Terminal", layout="wide")

# Google Sheet ID (aus deiner URL)
SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stSelectbox label, .stNumberInput label { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ The Gang: Live-Tausch & Self-Service")

# --- DATEN LADEN ---
@st.cache_data(ttl=60) # Lädt alle 60 Sekunden neu
def load_data():
    # Wir laden die Tabelle (Namen in Spalte A)
    df = pd.read_csv(URL, header=None).iloc[4:]
    df.columns = ['Name'] + [f'K{i}' for i in range(1, len(df.columns))]
    return df

try:
    df = load_data()
    spieler_liste = df['Name'].dropna().unique().tolist()

    # --- SELF-SERVICE BEREICH ---
    with st.sidebar:
        st.header("👤 Dein Update")
        user = st.selectbox("Wer bist du?", ["Gast"] + spieler_liste)
        if user != "Gast":
            st.info(f"Hi {user}, was hast du Neues?")
            typ = st.radio("Karten-Typ:", ["Gold", "Diamant"])
            d_nr = st.number_input("Deck Nr:", min_value=1, max_value=25, value=1)
            k_nr = st.number_input("Karte Nr:", min_value=1, max_value=9, value=1)
            anzahl = st.selectbox("Anzahl:", [0, 1, 2], index=1, help="0=Suche, 1=Habe, 2=Doppelt")
            
            if st.button("Update vormerken"):
                st.success(f"Vorgemerkt: {typ} D{d_nr}-K{k_nr} auf {anzahl}")

    # --- HAUPTBEREICH: AUTOMATISCHER SCAN ---
    tab1, tab2 = st.tabs(["🌕 Gold-Tausch", "💎 Diamant-Tausch"])

    def find_matches(start_col, end_col, prefix):
        gebot, bedarf = [], []
        for _, row in df.iterrows():
            name = str(row['Name']).strip()
            # Wir scannen den Bereich der Spalten (z.B. Gold 1-135)
            for i in range(start_col, end_col + 1):
                try:
                    val = int(float(str(row.iloc[i]).strip()))
                    label = f"{prefix} D{(i-1)//9 + 1}-K{(i-1)%9 + 1}"
                    if val >= 2: gebot.append((name, label))
                    elif val == 0: bedarf.append((name, label))
                except: continue
        
        matches = []
        used = set()
        for b_name, b_k in bedarf:
            if b_name in used: continue
            for g_name, g_k in gebot:
                if g_name in used: continue
                if b_k == g_k and b_name != g_name:
                    matches.append(f"🤝 **{g_name}** ➔ **{b_name}** ({g_k})")
                    used.add(g_name); used.add(b_name)
                    break
        return matches

    with tab1:
        # Gold: Spalten 1 bis 135 (Annahme: Deck 1-15)
        gold_matches = find_matches(1, 135, "Gold")
        if gold_matches:
            for m in gold_matches: st.success(m)
        else: st.info("Keine Gold-Matches.")

    with tab2:
        # Diamant: Spalten 136 bis Ende (Annahme: Ab Deck 16)
        diamant_matches = find_matches(136, len(df.columns)-1, "Diamant")
        if diamant_matches:
            for m in diamant_matches: st.info(m)
        else: st.info("Keine Diamant-Matches.")

except Exception as e:
    st.error(f"Verbindung zum Sheet fehlgeschlagen. Prüfe, ob es 'für jeden mit dem Link' freigegeben ist!")
