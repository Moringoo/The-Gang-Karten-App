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
    st.warning("⚠️ Keine Daten vom Google Sheet empfangen. Bitte lade die Seite neu.")
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
        
    # Jedes Deck bekommt ein einziges kompaktes Textfeld
    for i in range(1, 10):
        deck_key = f"Deck {i}"
        current_val_str = str(player_row.get(deck_key, "0,0,0,0,0,0,0,0,0"))
        
        # Säubere alte Datenformate zu einer reinen Zahlenkette
        current_digits = [c for c in current_val_str if c.isdigit()]
        while len(current_digits) < 9:
            current_digits.append("0")
        current_digits = current_digits[:9]
        current_chain = "".join(current_digits)
        
        storage_key = f"{selected_player}_{deck_key}_chain"
        if storage_key not in st.session_state.input_storage:
            st.session_state.input_storage[storage_key] = current_chain
            
        val_input = st.text_input(
            f"📑 Deck {i}",
            value=st.session_state.input_storage[storage_key],
            max_chars=9,
            key=f"input_{storage_key}"
        )
        
        clean_input_digits = [c for c in val_input if c.isdigit()]
        while len(clean_input_digits) < 9:
            clean_input_digits.append("0")
        clean_input_chain = "".join(clean_input_digits[:9])
        
        st.session_state.input_storage[storage_key] = clean_input_chain
        st.caption(f"Aktuell im Sheet: {','.join(current_digits)}")
        st.markdown("---")

    # --- SPEICHER-BUTTON (IMMER SICHTBAR) ---
    if st.button("🚀 AKTUALISIEREN / ÄNDERUNGEN SPEICHERN", type="primary", use_container_width=True):
        with st.spinner("Übertrage Daten an Google Sheets..."):
            success_count = 0
            
            for i in range(1, 10):
                deck_key = f"Deck {i}"
                current_digits = [c for c in str(player_row.get(deck_key, "0,0,0,0,0,0,0,0,0")) if c.isdigit()]
                while len(current_digits) < 9:
                    current_digits.append("0")
                current_chain = "".join(current_digits[:9])
                
                new_chain = st.session_state.input_storage[f"{selected_player}_{deck_key}_chain"]
                
                if new_chain != current_chain:
                    param_werte = ",".join(list(new_chain))
                    api_url = f"{SCRIPT_URL}?name={selected_player}&deck={i}&werte={param_werte}"
                    try:
                        res = requests.get(api_url, timeout=10)
                        if res.status_code == 200:
                            success_count += 1
                    except Exception as e:
                        st.error(f"Fehler bei Deck {i}: {e}")
            
            st.success("🔥 Datenabgleich mit Google Sheets abgeschlossen!")
            st.balloons()
            st.cache_data.clear()
            st.session_state.cache_tick = int(time.time())
            time.sleep(1.5)
            st.rerun()

# --- TAUSCHVORSCHLÄGE MIT PASSWORT SCHUTZ ---
st.markdown("---")
st.header("📊 Strategische Tausch-Analyse")

passwort = st.text_input("🔑 Gib das Passwort ein, um Tauschvorschläge zu sehen:", type="password")

if passwort == "gang2026":
    st.success("🔓 Zugriff gewährt!")
    
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
                missing = [k+1 for k, d in enumerate(deck_digits) if int(d) == 0]
                
                if owned_cards > 0:
                    analysis_data.append({
                        "Spieler": p_name,
                        "Deck": f"Deck {i}",
                        "Fortschritt": f"{owned_cards}/9",
                        "Sterne": owned_cards,
                        "Doppelt (Gibt ab)": doubles,
                        "Fehlt (Braucht)": missing
                    })
                    
        df_analysis = pd.DataFrame(analysis_data)
        
        if not df_analysis.empty:
            df_incomplete = df_analysis[df_analysis["Sterne"] < 9].copy()
            df_incomplete["Priorität"] = df_incomplete["Sterne"].apply(lambda x: 1 if x == 8 else (2 if x == 7 else 3))
            df_incomplete = df_incomplete.sort_values(by=["Priorität", "Sterne"], ascending=[True, False])
            
            st.markdown("### 🎯 Höchste Gang-Priorität (Decks kurz vor Fertigstellung!)")
            
            for _, target in df_incomplete.iterrows():
                if target["Priorität"] <= 2:
                    st.error(f"🚨 **{target['Spieler']}** braucht dringend Hilfe bei **{target['Deck']}** ({target['Fortschritt']})! Fehlende Karten: {target['Fehlt (Braucht)']}")
                    
                    potential_donors = []
                    for _, donor in df_analysis.iterrows():
                        if donor["Deck"] == target["Deck"] and donor["Spieler"] != target["Spieler"]:
                            matches = list(set(donor["Doppelt (Gibt ab)"]).intersection(set(target["Fehlt (Braucht)"])))
                            if matches:
                                potential_donors.append(f"-> **{donor['Spieler']}** kann Karte {matches} abgeben!")
                    
                    if potential_donors:
                        for d in potential_donors:
                            st.markdown(d)
                    else:
                        st.caption("Keine passenden doppelten Karten aktuell in der Gang verfügbar.")
            
            st.markdown("### 📋 Alle offenen Baustellen der Gang")
            st.dataframe(
                df_incomplete[["Spieler", "Deck", "Fortschritt", "Doppelt (Gibt ab)", "Fehlt (Braucht)"]],
                use_container_width=True,
                hide_index=True
            )
elif passwort != "":
    st.error("❌ Falsches Passwort!")
