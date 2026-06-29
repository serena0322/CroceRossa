import re
from firebase_admin import auth
from FirebaseConfig import db

class GestioneUtenteController:
    def __init__(self):
        # Il controller gestisce le operazioni di business e dialoga con Firebase
        pass

    def validaFormato(self, email: str, password: str) -> bool:
        """
        Controlla la validità sintattica di email e password per il login.
        Ritorna True se il formato è corretto, altrimenti False.
        """
        if not email or not password:
            return False
        
        # Regex standard per la verifica dell'indirizzo email
        regex_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(regex_email, email):
            return False
        
        # Firebase richiede password di almeno 6 caratteri
        if len(password) < 6:
            return False
            
        return True

    def effettuaLogin(self, email: str, password: str) -> bool:
        """
        Gestisce il flusso di autenticazione.
        Verifica prima i formati e poi interroga il backend.
        """
        if not self.validaFormato(email, password):
            print("❌ Formato email o password non valido.")
            return False
        
        try:
            # Recupera l'utente tramite email su Firebase Auth
            user = auth.get_user_by_email(email)
            
            # Verifica l'esistenza del profilo corrispondente su Firestore
            user_doc = db.collection("utenti").document(user.uid).get()
            if user_doc.exists:
                dati_utente = user_doc.to_dict() or {}
                nome_utente = dati_utente.get('nome', 'Volontario') 
                
                print(f"✅ Login effettuato con successo. Benvenuto {nome_utente}")
                return True
            else:
                print("❌ Profilo utente non trovato nel database.")
                return False
                
        except Exception as e:
            print(f"❌ Errore durante l'autenticazione: {e}")
            return False

    def validaDati(self, nome: str, cognome: str, cod_fiscale: str, telefono: str) -> bool:
        """
        Applica le regole di business per la modifica o registrazione del profilo.
        Controlla campi obbligatori, lunghezza del codice fiscale e formato telefono.
        """
        if not nome or not cognome or not cod_fiscale or not telefono:
            return False
            
        # Il Codice Fiscale deve essere di 16 caratteri
        if len(cod_fiscale) != 16:
            return False
            
        # Il telefono deve contenere solo cifre ed essere di una lunghezza minima realistica
        if not telefono.isdigit() or len(telefono) < 8:
            return False
            
        return True

    def modificaProfilo(self, utente_aggiornato) -> bool:
        """
        Riceve l'oggetto Utente modificato e aggiorna i record su Firebase.
        """
        # Estrae i dati dall'oggetto per la validazione
        if not self.validaDati(
            utente_aggiornato.nome, 
            utente_aggiornato.cognome, 
            utente_aggiornato.cod_fiscale, 
            utente_aggiornato.telefono
        ):
            print("❌ Validazione dei dati del profilo fallita.")
            return False
            
        try:
            # Aggiorna l'indirizzo email su Firebase Authentication (usa il codice fiscale come UID)
            auth.update_user(utente_aggiornato.cod_fiscale, email=utente_aggiornato.email)
            
            # Aggiorna il documento completo su Firestore usando il metodo to_dict() del modello
            db.collection("utenti").document(utente_aggiornato.cod_fiscale).update(utente_aggiornato.to_dict())
            
            print("✅ Profilo aggiornato correttamente su tutte le piattaforme.")
            return True
            
        except Exception as e:
            print(f"❌ Errore durante la modifica del profilo: {e}")
            return False

    def registraAccount(self, nuovo_utente, password_scelta: str) -> bool:
        """
        Crea le credenziali di accesso su Auth e salva l'anagrafica su Firestore.
        """
        if not self.validaDati(nuovo_utente.nome, nuovo_utente.cognome, nuovo_utente.cod_fiscale, nuovo_utente.telefono):
            print("❌ Dati di registrazione non validi.")
            return False
            
        try:
            # 1. Crea l'utente lato Authentication usando il Codice Fiscale come identificatore univoco (UID)
            auth.create_user(
                uid=nuovo_utente.cod_fiscale,
                email=nuovo_utente.email,
                password=password_scelta,
                display_name=nuovo_utente.get_nome_completo()
            )
            
            # 2. Salva il record anagrafico su Firestore
            db.collection("utenti").document(nuovo_utente.cod_fiscale).set(nuovo_utente.to_dict())
            
            print("✅ Nuovo account registrato con successo.")
            return True
            
        except Exception as e:
            print(f"❌ Errore durante la registrazione dell'account: {e}")
            return False

    def recuperaCredenziali(self, email: str) -> bool:
        """
        Avvia la procedura di recupero password inviando un'apposita email.
        """
        if not email or "@" not in email:
            return False
            
        try:
            # Genera il link di reset tramite l'SDK Admin (invio gestibile poi via email service)
            link = auth.generate_password_reset_link(email)
            print(f"✅ Link di reset generato correttamente.")
            # Qui si integrerebbe la chiamata alla funzione per spedire la mail reale
            return True
        except Exception as e:
            print(f"❌ Errore durante il recupero credenziali: {e}")
            return False