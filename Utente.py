from firebase_admin import auth, firestore
from auth import send_password_reset_email
from FirebaseConfig import db

class Utente:
    def __init__(self, cod_fiscale, nome, cognome, email, nascita, ruolo, telefono):
        self.cod_fiscale = cod_fiscale
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.nascita = nascita
        self.telefono = telefono
        self.ruolo = ruolo

    def get_nome_completo(self) -> str:
        return f"{self.nome} {self.cognome}"

    def descrizione_breve(self) -> str:
        return f"{self.get_nome_completo()} - CF: {self.cod_fiscale}"

    def aggiorna_email(self, nuova_email: str):
        try:
            auth.update_user(self.cod_fiscale, email=nuova_email)
            db.collection("utenti").document(self.cod_fiscale).update({"email": nuova_email})
            self.email = nuova_email
            print("✅ Email aggiornata.")
        except Exception as e:
            print(f"❌ Errore aggiornamento email: {e}")

    def aggiorna_password(self, nuova_password: str):
        try:
            auth.update_user(self.cod_fiscale, password=nuova_password)
            print("✅ Password aggiornata.")
        except Exception as e:
            print(f"❌ Errore aggiornamento password: {e}")

    def reset_password(self, api_key: str):
        return send_password_reset_email(self.email, api_key)

    def elimina_account(self):
        try:
            auth.delete_user(self.cod_fiscale)
            db.collection("utenti").document(self.cod_fiscale).delete()
            print("✅ Account eliminato.")
        except Exception as e:
            print(f"❌ Errore eliminazione account: {e}")

    def aggiorna_firestore(self):
        try:
            db.collection("utenti").document(self.cod_fiscale).set(self.to_dict())
            print("✅ Firestore aggiornato.")
        except Exception as e:
            print(f"❌ Errore aggiornamento Firestore: {e}")

    def ha_ruolo(self, ruolo: str) -> bool:
        return self.ruolo == ruolo

    def to_dict(self) -> dict:
        return {
            "cod_fiscale": self.cod_fiscale,
            "nome": self.nome,
            "cognome": self.cognome,
            "email": self.email,
            "ruolo": self.ruolo
        }
