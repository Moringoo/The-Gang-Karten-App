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
    st.info("Trage pro Karte ein: 0 = Fehlt, 1 = Vorhanden, 2+ = Doppelt (Tauschbar)")
    
    if "input_storage" not in st.session_state:
        st.session_state.input_storage = {}
        
    changes_detected = False
    
    # Jedes Deck bekommt eine eigene Zeile (keine 3 Spalten mehr)
    for i in range(1, 10):
        deck_key = f"Deck {i}"
        current_val_str = str(player_row.get(deck_key, "0,0,0,0,0,0,0,0,0"))
        
        # Säubere alte Datenformate zu einer reinen Zahlenliste
        current_digits = [c for c in current_val_str if c.isdigit()]
        while len(current_digits) < 9:
            current_digits.append("0")
        current_digits = current_digits[:9]
        
        # Große Zeile für das Deck: Links die Beschriftung, rechts die 9 Felder nebeneinander
        st.markdown(f"#### 📑 Deck {i}")
        new_digits = []
        
        sub_cols = st.columns(9)
        for k in range(9):
            with sub_cols[k]:
                old_digit = current_digits[k]
                storage_key = f"{selected_player}_{deck_key}_{k}"
                
                if storage_key not in st.session_state.input_storage:
                    st.session_state.input_storage[storage_key] = int(old_digit)
                    
                val = st.number_input(
                    f"D{i}K{k+1}", 
                    min_value=0, 
                    max_value=9, 
                    value=st.session_state.input_storage[storage_key],
                    key=f"input_{storage_key}",
                    label_visibility="collapsed"
                )
                st.session_state.input_storage[storage_key] = val
                new_digits.append(str(val))
        
        # Status-Anzeige direkt unter den 9 Feldern des jeweiligen Decks
        current_display = ",".join(current_digits)
        new_display = ",".join(new_digits)
        
        if new_display != current_display:
            changes_detected = True
            st.caption(f"🔄 Geändert: {current_display} ➡️ **{new_display}**")
        else:
            st.caption(f"✅ Aktuell: {current_display}")
            
        st.markdown("---") # Trennlinie zwischen den Decks

    # --- SPEICHER-BUTTON ---
    if changes_detected:
        if st.button("🚀 ALLE ÄNDERUNGEN SPEICHERN", type="primary", use_container_width=True):
            with st.spinner("Übertrage Daten an Google Sheets..."):
                success_count = 0
                
                for i in range(1, 10):
                    deck_key = f"Deck {i}"
                    current_digits = [c for c in str(player_row.get(deck_key, "0,0,0,0,0,0,0,0,0")) if c.isdigit()]
                    while len(current_digits) < 9:
                        current_digits.append("0")
                    current_digits = current_digits[:9]
                    
                    new_digits = [str(st.session_state.input_storage[f"{selected_player}_{deck_key}_{k}"]) for k in range(9)]
                    
                    if new_digits != current_digits:
                        param_werte = ",".join(new_digits)
                        api_url = f"{SCRIPT_URL}?name={selected_player}&deck={i}&werte={param_werte}"
                        try:
                            res = requests.get(api_url, timeout=10)
                            if res.status_code == 200:
                                success_count += 1
                        except Exception as e:
                            st.error(f"Fehler bei Deck {i}: {e}")
                
                if success_count > 0:
                    st.success(f"🔥 {success_count} Deck(s) erfolgreich aktualisiert!")
                    st.balloons()
                    st.cache_data.clear()
                    st.session_state.cache_tick = int(time.time())
                    del st.session_state.input_storage
                    time.sleep(1.5)
                    st.rerun()
    else:
        st.button("✨ ALLES AUF DEM NEUESTEN STAND", disabled=True, use_container_width=True)

# --- TAUSCH-ANALYSE ---
st.header("📊 Strategische Tausch-Analyse (Wer braucht was?)")

if not df_data.empty and "Name" in df_data.columns:
    analysis_data = []
    
    for _, row in df_data.iterrows():
        p_name = row["Name"]
        if p_name == "Vorlage" or pd.isna(p_name):
            continue
            
        for i in range(1, 10):
            raw_val = str(row.get(f"Deck {i}", "0,0,0,0,0,0,0,0,0"))
            deck_digits = [c for c in raw_val if c.isdigit()]
            while len(deck_digits) < 9:
                deck_digits.append("0")
            deck_digits = deck_digits[:9]
            
            owned_cards = sum(1 for d in deck_digits if int(d) > 0)
            doubles = [k+1 for k, d in enumerate(deck_digits) if int(d) > 1]
            missing =
