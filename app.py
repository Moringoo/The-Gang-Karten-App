import streamlit as st
import requests
import pandas as pd
import time

# --- KONFIGURATION ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwUMOODTrttlwbCQGQzy3xxHAkLUAJ4n832vw2846kh2jH0rKYgPsj3t-ZOtYeMR8w/exec"

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
all_players = list(df_data["Name"].unique()) if "Name" in df_data.columns else []
selected_player = st.selectbox("👤 Wähle deinen Gang-Namen:", all_players)

if selected_player:
    player_row = df_data[df_data["Name"] == selected_player].iloc[0]
    
    st.subheader(f"🗃️ Kartendecks von {selected_player}")
    st.info("Tippe einfach die 9 Zahlen hintereinander ein (z.B. 221000212). 0 = Fehlt, 1 = Vorhanden, 2+ = Doppelt")
    
    if "input_storage" not in st.session_state:
        st.session_state.input_storage = {}
        
    changes_detected = False
    
    # Jedes Deck bekommt ein einziges kompaktes Textfeld
    for i in range(1, 10):
        deck_key = f"Deck {i}"
        current_val_str = str(player_row.get(deck_key, "0,0,0,0,0,0,0,0,0"))
        
        # Säubere alte Datenformate zu einer reinen Zahlenkette (9 Zeichen lang)
        current_digits = [c for c in current_val_str if c.isdigit()]
        while len(current_digits) < 9:
            current_digits.append("0")
        current_digits = current_digits[:9]
        current_chain = "".join(current_digits) # Macht z.B. "221000212" daraus
        
        storage_key = f"{selected_player}_{deck_key}_chain"
        if storage_key not in st.session_state.input_storage:
            st.session_state.input_storage[storage_key] = current_chain
            
        # Das einteilige Eingabefeld
        val_input = st.text_input(
            f"📑 Deck {i}",
            value=st.session_state.input_storage[storage_key],
            max_chars=9,
            key=f"input_{storage_key}"
        )
        
        # Validierung: Falls die Eingabe fehlerhaft ist, füllen wir mit Nullen auf
        clean_input_digits = [c for c in val_input if c.isdigit()]
        while len(clean_input_digits) < 9:
            clean_input_digits.append("0")
        clean_input_chain = "".join(clean_input_digits[:9])
        
        st.session_state.input_storage[storage_key] = clean_input_chain
        
        # Vergleich, ob sich
