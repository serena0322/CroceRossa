import hashlib
from typing import Optional
from UtenteFactory import costruisci_utente

def hash_password(password: str) -> str:
    """Restituisce l'hash SHA-256 della password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def registra_utente(cod_fiscale: str, email: str, password: str, nome: str, ruolo: str) -> bool:
    """Registra un nuovo utente nel sistema locale."""
    from Sistema import Sistema
    s = Sistema.get_instance()
    if not s:
        return False

    if utente_gia_registrato(email, cod_fiscale):
        return False

    hashed = hash_password(password)
    dati = {
        "cod_fiscale": cod_fiscale,
        "email": email,
        "password": hashed,
        "nome": nome,
        "ruolo": ruolo
    }
    utente = costruisci_utente(dati)
    s.volontari.append(utente)
    s.salva_dati()
    print("[Auth] Registrazione completata nel database locale.")
    return True

def utente_gia_registrato(email: str, cod_fiscale: str) -> bool:
    """Controlla se esiste già un utente registrato con l'email o codice fiscale."""
    from Sistema import Sistema
    s = Sistema.get_instance()
    if not s:
        return False
    cf_target = cod_fiscale.strip().upper()
    email_target = email.strip().lower()
    for v in s.volontari:
        if v.cod_fiscale.strip().upper() == cf_target:
            return True
        if getattr(v, "email", "").strip().lower() == email_target:
            return True
    return False

def recupera_utente(cod_fiscale: str):
    """Recupera l'utente dal database locale tramite codice fiscale."""
    from Sistema import Sistema
    s = Sistema.get_instance()
    if s:
        return s.get_volontario(cod_fiscale)
    return None

def login_utente(email: str, password: str) -> Optional[dict]:
    """Esegue il login verificando email e password in locale."""
    from Sistema import Sistema
    s = Sistema.get_instance()
    if not s:
        return None
    email_clean = email.strip().lower()
    u = next((v for v in s.volontari if getattr(v, "email", "").strip().lower() == email_clean), None)
    if not u:
        return None
    pwd_hash = hash_password(password)
    user_pwd = getattr(u, "password", "")
    if not user_pwd or user_pwd == password or user_pwd == pwd_hash:
        return {
            "localId": u.cod_fiscale,
            "email": u.email,
            "nome": u.nome,
            "ruolo": u.ruolo
        }
    return None

def send_password_reset_email(email: str) -> bool:
    """Invia un'email di reset tramite EmailService."""
    from EmailService import EmailService
    from Sistema import Sistema
    s = Sistema.get_instance()
    u = None
    if s:
        u = next((v for v in s.volontari if getattr(v, "email", "").strip().lower() == email.strip().lower()), None)
    nome = u.nome if u else "Volontario"
    return EmailService.inviaMail(
        destinatario=email,
        messaggio=f"Gentile {nome},\nUtilizza questo messaggio per confermare il ripristino della tua password.",
        oggetto="Reset Password — Croce Rossa Italiana"
    )
