import streamlit as st
import pandas as pd

st.set_page_config(page_title="The Gang - Profi Tausch", layout="wide")
st.title("🏆 The Gang: Master-Tausch-Rechner")

SHEET_ID = "1MMncv9mKwkRPs9j9QH7jM-onj3N1qJCL_BE2oMXZSQo"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def get_clean_val(val):
    try:
        return int(float(val)) if pd.notna(val) else 0
    except:
        return 0

try:
    df = pd.read_csv(DATA_URL)
    # Wir löschen komplett leere Zeilen/Spalten
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    
    st.info("💡 Dieser Rechner schlägt nur Täusche vor, wenn der Empfänger 0 Karten hat und der Geber mindestens 2.")

    # Definition der exakten Spalten für deine Tabelle:
    # Deck 1: Spalten 1-9 (B-J)
    # Deck 2: Spalten 11-19 (L-T) - Wir überspringen die Spalte 'Name' in der Mitte!
    # Deck 3: Spalten 21-29 (V-AD)
    decks = {
        "Deck 1": list(range(1, 10)),
        "Deck 2": list(range(11, 20)),
        "Deck 3": list(range(21, 30))
    }

    gebot = []
    bedarf = []

    for d_name, spalten in decks.items():
        for idx, row in df.iterrows():
            spieler = str(row.iloc[0]).strip()
            if spieler.lower() in ["name", "nan", ""]: continue
            
            for i, col_idx in enumerate(spalten):
                if col_idx >= len(row): continue
                
                anzahl = get_clean_val(row.iloc[col_idx])
                karte_label = f"{d_name}-K{i+1}"
                
                if anzahl >= 2:
                    gebot.append({"von": spieler, "karte": karte_label})
                elif anzahl == 0:
                    # DOPPEL-CHECK: Nur wenn wirklich 0 dort steht!
                    bedarf.append({"an": spieler, "karte": karte_label})

    # Fairer Abgleich (Jeder nur 1x)
    final_deals = []
    geber_belegt = set()
    nehmer_belegt = set()

    for b in bedarf:
        if b["an"] in nehmer_belegt: continue
        for g in gebot:
            if g["von"] in geber_belegt: continue
            
            if b["karte"] == g["karte"] and b["an"] != g["von"]:
                final_deals.append(f"✅ {g['von']} ➔ {b['an']} ({g['karte']})")
                geber_belegt.add(g["von"])
                nehmer_belegt.add(b["an"])
                break

    # --- ANZEIGE & WHATSAPP ---
    if final_deals:
        st.header("📋 Heutige Tausch-Liste")
        whatsapp_text = "*Die Gang - Tauschliste für heute:*\n\n" + "\n".join(final_deals)
        
        for deal in final_deals:
            st.success(deal)
            
        st.divider()
        st.subheader("📲 WhatsApp Export")
        st.code(whatsapp_text)
        st.button("Kopieren (In der App markieren & Strg+C)")
    else:
        st.warning("Keine perfekten Matches gefunden. Prüfe, ob genug '2er' und '0er' in der Tabelle stehen.")

except Exception as e:
    st.error(f"Datenfehler: {e}. Bitte die Google Tabelle prüfen!")
