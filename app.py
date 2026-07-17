import streamlit as st
import requests
import pandas as pd
import time

# --- KONFIGURATION ---
# Deine Google Apps Script Web-App URL (wird automatisch aus den Secrets geladen)
SCRIPT_URL = st.secrets.get("SCRIPT_URL", "https://script.google.com/macros/s/AKfycbzqvISwbnj74Ab7_NO5X3AeeHyvDeWFNFREiWd420_QBdlKyMWaNI6ZL9I0wyoLjEI/exec")

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

# Live-Counter für den URL-Wechsel
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
    
    # Speicher für die neuen Werte im Session State
    if "input_storage" not in st.session_state:
        st.session_state.input_storage = {}
        
    # Erstelle Eingabefelder für alle 9 Decks
    cols = st.columns(3)
    changes_detected = False
    
    for i in range(1, 10):
        deck_key = f"Deck {i}"
        current_val_str = str(player_row.get(deck_key, "000000000"))
        # Sicherstellen, dass der String genau 9 Zeichen hat
        current_val_str = current_val_str.ljust(9, '0')[:9]
        
        with cols[(i-1) % 3]:
            st.markdown(f"### 📑 Deck {i}")
            new_digits = []
            
            # Zeige die 9 Karten nebeneinander als kompakte Eingabe
            sub_cols = st.columns(9)
            for k in range(9):
                with sub_cols[k]:
                    old_digit = current_val_str[k]
                    storage_key = f"{selected_player}_{deck_key}_{k}"
                    
                    # Initialisiere Speicher falls leer
                    if storage_key not in st.session_state.input_storage:
                        st.session_state.input_storage[storage_key] = int(old_digit) if old_digit.isdigit() else 0
                        
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
            
            new_val_str = "".join(new_digits)
            if new_val_str != current_val_str:
                changes_detected = True
                st.caption(f"🔄 Geändert: {current_val_str} ➡️ **{new_val_str}**")
            else:
                st.caption(f"✅ Aktuell: {current_val_str}")

    # --- SPEICHER-BUTTON (Eiskalt an Google vorbei) ---
    st.markdown("---")
    if changes_detected:
        if st.button("🚀 ALLE ÄNDERUNGEN SPEICHERN", type="primary", use_container_width=True):
            with st.spinner("Übertrage Daten an Google Sheets..."):
                success_count = 0
                
                # Gehe alle Decks durch und sende nur die geänderten
                for i in range(1, 10):
                    deck_key = f"Deck {i}"
                    current_val_str = str(player_row.get(deck_key, "000000000")).ljust(9, '0')[:9]
                    
                    # Generiere den neuen String aus dem Speicher
                    new_digits = [str(st.session_state.input_storage[f"{selected_player}_{deck_key}_{k}"]) for k in range(9)]
                    new_val_str = "".join(new_digits)
                    
                    if new_val_str != current_val_str:
                        # Direkter Sende-Befehl an die Google-Schnittstelle
                        api_url = f"{SCRIPT_URL}?name={selected_player}&deck={i}&werte={new_val_str}"
                        try:
                            res = requests.get(api_url, timeout=10)
                            if res.status_code == 200:
                                success_count += 1
                        except Exception as e:
                            st.error(f"Fehler bei Deck {i}: {e}")
                
                if success_count > 0:
                    st.success(f"🔥 {success_count} Deck(s) erfolgreich im Google Sheet aktualisiert!")
                    st.balloons()
                    # Cache leeren und App neu laden
                    st.cache_data.clear()
                    st.session_state.cache_tick = int(time.time())
                    # Lösche temporären Speicher, damit neue Daten geladen werden
                    del st.session_state.input_storage
                    time.sleep(1.5)
                    st.rerun()
    else:
        st.button("✨ ALLES AUF DEM NEUESTEN STAND", disabled=True, use_container_width=True)

# --- TAUSCH-ANALYSE (Das Herzstück für die Gang) ---
st.markdown("---")
st.header("📊 Strategische Tausch-Analyse (Wer braucht was?)")

if not df_data.empty and "Name" in df_data.columns:
    # Berechne den Status aller Karten für alle Spieler
    analysis_data = []
    
    for _, row in df_data.iterrows():
        p_name = row["Name"]
        if p_name == "Vorlage" or pd.isna(p_name):
            continue
            
        for i in range(1, 10):
            deck_val = str(row.get(f"Deck {i}", "000000000")).ljust(9, '0')[:9]
            
            # Zähle wie viele Karten vorhanden sind (Wert > 0)
            owned_cards = sum(1 for char in deck_val if char.isdigit() and int(char) > 0)
            
            # Finde doppelte Karten (Wert > 1)
            doubles = [k+1 for k, char in enumerate(deck_val) if char.isdigit() and int(char) > 1]
            # Finde fehlende Karten (Wert == 0)
            missing = [k+1 for k, char in enumerate(deck_val) if char == '0']
            
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
        # Sortierung nach Priorität (9/9 Decks ausblenden, Decks mit 8/9 oder 7/9 ganz nach oben)
        df_incomplete = df_analysis[df_analysis["Sterne"] < 9].copy()
        df_incomplete["Priorität"] = df_incomplete["Sterne"].apply(lambda x: 1 if x == 8 else (2 if x == 7 else 3))
        df_incomplete = df_incomplete.sort_values(by=["Priorität", "Sterne"], ascending=[True, False])
        
        # Schöne Anzeige der Tausch-Möglichkeiten
        st.markdown("### 🎯 Höchste Gang-Priorität (Decks kurz vor Fertigstellung!)")
        
        for _, target in df_incomplete.iterrows():
            if target["Priorität"] <= 2: # Nur 8/9 und 7/9 Decks prominent anzeigen
                st.error(f"🚨 **{target['Spieler']}** braucht dringend Hilfe bei **{target['Deck']}** ({target['Fortschritt']})! Fehlende Karten: {target['Fehlt (Braucht)']}")
                
                # Finde passende Spender in der Gang
                potential_donors = []
                for _, donor in df_analysis.iterrows():
                    if donor["Deck"] == target["Deck"] and donor["Spieler"] != target["Spieler"]:
                        # Prüfe, ob der Geber eine Karte doppelt hat, die dem Empfänger fehlt
                        matches = list(set(donor["Doppelt (Gibt ab)"]).intersection(set(target["Fehlt (Braucht)"])))
                        if matches:
                            potential_donors.append(f"-> **{donor['Spieler']}** kann Karte {matches} abgeben!")
                
                if potential_donors:
                    for d in potential_donors:
                        st.markdown(d)
                else:
                    st.caption(" Keine passenden doppelten Karten aktuell in der Gang verfügbar.")
        
        # Komplette Übersichtstabelle für den Boss
        st.markdown("### 📋 Alle offenen Baustellen der Gang")
        st.dataframe(
            df_incomplete[["Spieler", "Deck", "Fortschritt", "Doppelt (Gibt ab)", "Fehlt (Braucht)"]],
            use_container_width=True,
            hide_index=True
        )
