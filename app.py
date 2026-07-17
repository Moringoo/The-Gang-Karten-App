import streamlit as st
import requests
import pandas as pd
import time

# --- KONFIGURATION ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwRrLbOa-GNfACWGpxClFmUbfpZspDpVA75CkvTa4VNMSar7a0dondpfBW-3bapqA/exec"

st.set_page_config(page_title="The Gang - Karten-Manager", page_icon="💀", layout="wide")
st.title("💀 The Gang - Karten-Manager")

# --- DATA LOADING (Mit Cache-Busting gegen Google-Verzögerung) ---
@st.cache_data(ttl=10)
def load_data(cache_tick):
    try:
        response = requests.get(f"{SCRIPT_URL}?action=read&_cb={cache_tick}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            return df
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
    return pd.DataFrame()

if "cache_tick" not in st.session_state:
    st.session_state.cache_tick = int(time.time())

df_data = load_data(st.session_state.cache_tick)

if df_data.empty:
    st.warning("⚠️ Keine Daten vom Google Sheet empfangen. Bitte überprüfe die SCRIPT_URL oder lade die Seite neu.")
    if st.button("🔄 Verbindung erneut testen"):
        st.session_state.cache_tick = int(time.time())
        st.rerun()
    st.stop()

# --- SPIELER AUSWAHL ---
all_players = sorted(df_data["Name"].unique()) if "Name" in df_data.columns else []
selected_player = st.selectbox("👤 Wähle deinen Gang-Namen:", all_players)

if selected_player:
    player_row = df_data[df_data["Name"] == selected_player].iloc[0]
    
    st.subheader(f"🗃️ Kartendecks von {selected_player}")
    st.info("Trage pro Karte ein: 0 = Fehlt, 1 = Vorhanden, 2+ = Doppelt (Tauschbar)")
    
    if "input_storage" not in st.session_state:
        st.session_state.input_storage = {}
        
    cols = st.columns(3)
    changes_detected = False
    
    for i in range(1, 10):
        deck_key = f"Deck {i}"
        current_val_str = str(player_row.get(deck_key, "0,0,0,0,0,0,0,0,0"))
        
        # Säubere alte Datenformate zu einer reinen Zahlenliste
        current_digits = [c for c in current_val_str if c.isdigit()]
        while len(current_digits) < 9:
            current_digits.append("0")
        current_digits = current_digits[:9]
        
        with cols[(i-1) % 3]:
            st.markdown(f"### 📑 Deck {i}")
            new_digits = []
            
            sub_cols = st.columns(9)
            for k in range(9):
                with sub_cols[k]:
                    old_digit = current_digits[k]
                    storage_key = f"{selected_player}_{deck_key}_{k}"
                    
                    if storage_key not in st.session_state.input_storage:
                        st.session_state.input_storage[storage_key] = int(old_digit)
                        
                    val = st.number_input(
                        f"K{k+1}", 
                        min_value=0, 
                        max_value=9, 
                        value=st.session_state.input_storage[storage_key],
                        key=f"input_{storage_key}",
                        label_visibility="collapsed"
                    )
                    st.session_state.input_storage[storage_key] = val
                    new_digits.append(str(val))
            
            # Zeige Vorschau mit Kommas passend fürs Sheet
            current_display = ","
