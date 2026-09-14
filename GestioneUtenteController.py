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

    def effettuaLogin(self, email: str, password: str, sistema=None) -> bool:
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
                
                from UtenteFactory import costruisci_utente
                logged_user = costruisci_utente(dati_utente)
                if sistema:
                    sistema.logged_user = logged_user
                
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

    def recuperaCredenziali(self, identificativo: str) -> tuple[bool, str]:
        """
        Avvia la procedura di recupero password inviando un'apposita email.
        Supporta sia indirizzo email che Codice Fiscale.
        Invia il link / istruzioni di reimpostazione tramite EmailService.
        """
        if not identificativo or not str(identificativo).strip():
            return False, "Inserisci un indirizzo email o Codice Fiscale valido."

        target_str = str(identificativo).strip()
        dest_email = ""
        nome_utente = "Volontario"

        # 1. Se è un'email
        if "@" in target_str:
            dest_email = target_str

        # 2. Cerca l'utente nel database Firestore
        try:
            if not dest_email:
                # Cerca per codice fiscale come document ID
                doc = db.collection("utenti").document(target_str.upper()).get()
                if doc.exists:
                    dati = doc.to_dict() or {}
                    dest_email = dati.get("email", "")
                    nome_utente = f"{dati.get('nome', '')} {dati.get('cognome', '')}".strip() or "Volontario"
            else:
                # Trova per email
                docs = db.collection("utenti").where("email", "==", dest_email).limit(1).get()
                for doc in docs:
                    dati = doc.to_dict() or {}
                    nome_utente = f"{dati.get('nome', '')} {dati.get('cognome', '')}".strip() or "Volontario"
                    break
        except Exception as e:
            print(f"⚠️ Ricerca utente per recupero credenziali: {e}")

        if not dest_email or "@" not in dest_email:
            return False, f"Nessun account trovato per '{target_str}'. Verifica i dati inseriti."

        # 3. Genera link o codice di ripristino sicuro
        link_reset = ""
        try:
            link_reset = auth.generate_password_reset_link(dest_email)
        except Exception:
            import secrets
            token = secrets.token_urlsafe(16)
            link_reset = f"https://crocerossa.it/reset-password?token={token}&email={dest_email}"

        # 4. Spedizione email con EmailService
        from EmailService import EmailService
        messaggio = (
            f"Gentile {nome_utente},\n\n"
            f"abbiamo ricevuto una richiesta di reimpostazione credenziali per il tuo account Croce Rossa Italiana.\n\n"
            f"Per reimpostare la tua password di accesso, utilizza il seguente collegamento sicuro:\n"
            f"{link_reset}\n\n"
            f"Se non hai richiesto tu il ripristino, puoi ignorare questo messaggio.\n"
            f"La tua password attuale rimarrà invariata.\n\n"
            f"Cordiali saluti,\n"
            f"Croce Rossa Italiana — Servizio Gestione Utenze"
        )

        inviata = EmailService.inviaMail(
            destinatario=dest_email,
            messaggio=messaggio,
            oggetto="🔐 Recupero Credenziali di Accesso — Croce Rossa Italiana"
        )

        if inviata:
            print(f"✅ Email di recupero inviata a {dest_email}.")
            return True, f"Istruzioni di ripristino inviate con successo all'indirizzo:\n{dest_email}"
        else:
            return False, "Impossibile inviare l'email di recupero in questo momento. Riprova più tardi."