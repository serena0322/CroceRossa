import hashlib
import requests
from FirebaseConfig import db, api_key
from UtenteFactory import costruisci_utente

def hash_password(password: str) -> str:
    """Restituisce l'hash SHA-256 della password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def registra_utente(cod_fiscale: str, email: str, password: str, nome: str, ruolo: str) -> bool:
    """Registra un nuovo utente in Firebase Auth e Firestore."""

    # 1. Controlla se già registrato in Firestore
    if utente_gia_registrato(email, cod_fiscale):
        return False

    # 2. Registra in Firebase Authentication
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()  # contiene localId, idToken ecc.
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore durante la creazione dell'utente Firebase Auth: {e}")
        return None

    # 3. Prepara dati utente
    hashed = hash_password(password)
    utente = {
        "cod_fiscale": cod_fiscale,
        "email": email,
        "password": hashed,
        "nome": nome,
        "ruolo": ruolo
    }

    # 4. Determina la collezione corretta
    ruolo = ruolo.lower()
    if ruolo == "volontario":
        collezione = "Volontario"
    elif ruolo == "referente":
        collezione = "Referente"
    elif ruolo == "operatore sanitario":
        collezione = "Operatore_Sanitario"
    else:
        print(f"❌ Ruolo non valido: {ruolo}")
        return False

    # 5. Salva in Firestore nella collezione corretta
    try:
        db.collection(collezione).document(cod_fiscale).set(utente)
        print("✅ Registrazione completata in Firestore.")
        return data  # restituisci i dati Firebase Auth se necessario
    except Exception as e:
        print(f"❌ Errore durante il salvataggio su Firestore: {e}")
        return False

def utente_gia_registrato(email: str, cod_fiscale: str) -> bool:
    """Controlla se esiste già un utente registrato con l'email o codice fiscale in una delle collezioni."""
    collezioni = ["Volontario", "Referente", "Operatore_Sanitario"]

    for collezione in collezioni:
        ref = db.collection(collezione)

        # Controllo codice fiscale come ID documento
        if ref.document(cod_fiscale).get().exists:
            print(f"❌ Codice fiscale già registrato in {collezione}.")
            return True

        # Controllo email duplicata
        risultati = ref.where("email", "==", email).get()
        if risultati:
            print(f"❌ Email già utilizzata in {collezione}.")
            return True

    return False

def recupera_utente_da_firestore(cod_fiscale: str):
    doc = db.collection("utenti").document(cod_fiscale).get()
    if doc.exists:
        data = doc.to_dict()
        return costruisci_utente(data)
    else:
        print("❌ Utente non trovato in Firestore.")
        return None


def login_utente(email: str, password: str, api_key: str) -> dict | None:
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        data = res.json()
        return data  # contiene idToken, refreshToken, localId, email, ecc.
    except requests.exceptions.HTTPError as err:
        print("❌ Login fallito:", err)
        return None


def send_password_reset_email(email: str, api_key: str):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Email per il reset della password inviata con successo.")
        return True
    except requests.exceptions.HTTPError as err:
        print(f"❌ Errore durante l'invio dell'email di reset: {err}")
        return False
