import json
import os
from datetime import datetime

# File di sessione locale memorizzato nella cartella del progetto
SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".session.json")

def save_session(user) -> bool:
    """Salva i dati della sessione per mantenere l'utente autenticato su questo dispositivo."""
    if not user:
        return False
    try:
        cf = str(getattr(user, "cod_fiscale", "") or "")
        email = str(getattr(user, "email", "") or "")
        nome = str(getattr(user, "nome", "") or "")
        ruolo = str(getattr(user, "ruolo", "volontario") or "")

        data = {
            "cod_fiscale": cf,
            "email": email,
            "nome": nome,
            "ruolo": ruolo,
            "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"[SessionManager] Sessione persistente salvata per {cf or email}")
        return True
    except Exception as e:
        print(f"[SessionManager/Errore] Salvataggio sessione: {e}")
        return False

def load_session() -> dict | None:
    """Restituisce i dati della sessione salvata se presente e valida."""
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("cod_fiscale") or data.get("email"):
            return data
    except Exception as e:
        print(f"[SessionManager/Errore] Caricamento sessione: {e}")
    return None

def clear_session() -> bool:
    """Rimuove la sessione locale al logout."""
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
            print("[SessionManager] Sessione eliminata.")
        return True
    except Exception as e:
        print(f"[SessionManager/Errore] Rimozione sessione: {e}")
        return False
