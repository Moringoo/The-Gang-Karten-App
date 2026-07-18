import streamlit as st
import requests
import pandas as pd
import time

# --- KONFIGURATION ---
# Deine neue Bereitstellungs-URL ist jetzt hier fest hinterlegt:
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw71UB_1bRLELpRK1pzygSgV_uSxR4FHme1CRez4nC-80wGrwwORgYntwSyz0VofCs/exec"

st.set_page_config(page_title="The Gang - Karten-Manager", page_icon="💀", layout="wide")
st.title("💀 The Gang - Karten-Manager")

# --- DATA LOADING ---
@st.cache_data(ttl=3)
def load_data(cache_tick):
    try:
        response = requests.get(f"{SCRIPT_URL}?action=read&_cb={cache_tick}", timeout=10)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
    return pd.DataFrame()

if "cache_tick" not in st.session_state:
    st.session_state.cache_tick = int(time.time())

df_data = load_data(st.session_state.cache_tick)

if df_data.empty:
    st.warning("⚠️ Keine Daten vom Google Sheet empfangen. Bitte lade die Seite neu.")
    if st.button("🔄 Verbindung erneut testen"):
        st.session_state.cache_tick = int(time.time())
        st.rerun()
    st.stop()

# --- SPIELER AUSWAHL ---
all_players = list(df_data["Name"].unique()) if "Name" in df_data.columns else []
selected_player = st.selectbox("👤 Wähle deinen Gang-Namen:", all_players)

if selected_player:
    df_data["CleanName"] = df_data["Name"].astype(str).str.strip()
    matched_rows = df_data[df_data["CleanName"] == str(selected_player).strip()]
    
    if not matched_rows.empty:
        player_row = matched_rows.iloc[0]
        
        st.subheader(f"🗃️ Kartendecks von {selected_player}")
        st.info("Tippe einfach die 9 Zahlen hintereinander ein (z.B. 221000212). 0 = Fehlt, 1 = Vorhanden, 2+ = Doppelt")
        
        if "input_storage" not in st.session_state:
            st.session_state.input_storage = {}
            
        for i in range(1, 16):
            # Holt die 9 Kartenwerte aus den Spalten D{i}-K1 bis D{i}-K9
            current_digits = []
            for k in range(1, 10):
                col_key = f"D{i}-K{k}"
                val = str(player_row.get(col_key, "0"))
                current_digits.append(val if val.isdigit() else "0")
                
            current_chain = "".join(current_digits)
            storage_key = f"{selected_player}_Deck_{i}_chain"
            
            if storage_key not in st.session_state.input_storage:
                st.session_state.input_storage[storage_key] = current_chain
                
            val_input = st.text_input(
                f"📑 Deck {i}",
                value=st.session_state.input_storage[storage_key],
                max_chars=9,
                key=f"input_{storage_key}"
            )
            
            clean_digits = [c for c in val_input if c.isdigit()]
            while len(clean_digits) < 9:
                clean_digits.append("0")
            clean_chain = "".join(clean_digits[:9])
            
            st.session_state.input_storage[storage_key] = clean_chain
            st.caption(f"Aktuell im Sheet: {','.join(current_digits)}")
            st.markdown("---")

        # --- SPEICHER-BUTTON ---
        if st.button("🚀 AKTUALISIEREN / ÄNDERUNGEN SPEICHERN", type="primary", use_container_width=True):
            with st.spinner("Übertrage Daten an Google Sheets..."):
                success_count = 0
                
                for i in range(1, 16):
                    orig_digits = []
                    for k in range(1, 10):
                        orig_digits.append(str(player_row.get(f"D{
