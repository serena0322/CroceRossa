import re
import hashlib
import secrets

class GestioneUtenteController:
    def __init__(self):
        # Il controller gestisce le operazioni di business e la persistenza locale
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
        
        # Password di almeno 6 caratteri
        if len(password) < 6:
            return False
            
        return True

    def effettuaLogin(self, email: str, password: str, sistema=None) -> bool:
        """
        Gestisce il flusso di autenticazione.
        Verifica prima i formati e poi controlla il database locale JSON.
        """
        if not self.validaFormato(email, password):
            print("[Auth/Errore] Formato email o password non valido.")
            return False
        
        try:
            from Sistema import Sistema
            sys_inst = sistema or Sistema.get_instance()
            if not sys_inst:
                print("[Auth/Errore] Istanza di Sistema non disponibile.")
                return False

            email_clean = email.strip().lower()
            # Cerca l'utente per email oppure per codice fiscale
            user = next((v for v in sys_inst.volontari if getattr(v, "email", "").strip().lower() == email_clean), None)
            if not user:
                user = next((v for v in sys_inst.volontari if getattr(v, "cod_fiscale", "").strip().upper() == email.strip().upper()), None)

            if user:
                user_pwd = getattr(user, "password", "")
                pwd_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
                # Verifica password (in chiaro o con hash SHA-256)
                if not user_pwd or user_pwd == password or user_pwd == pwd_hash:
                    sys_inst.logged_user = user
                    nome_utente = user.nome or "Volontario"
                    print(f"[Auth] Login effettuato con successo. Benvenuto {nome_utente}")
                    return True
                else:
                    print("[Auth/Errore] Password non corretta.")
                    return False
            else:
                print("[Auth/Errore] Profilo utente non trovato nel database.")
                return False
                
        except Exception as e:
            print(f"[Auth/Errore] Durante l'autenticazione: {e}")
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
        Riceve l'oggetto Utente modificato e aggiorna i record nel database locale JSON.
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
            from Sistema import Sistema
            sys_inst = Sistema.get_instance()
            if sys_inst:
                existing = sys_inst.get_volontario(utente_aggiornato.cod_fiscale)
                if existing and existing is not utente_aggiornato:
                    existing.aggiornaProfilo(utente_aggiornato)
                elif not existing:
                    sys_inst.volontari.append(utente_aggiornato)
                sys_inst.salva_dati()
            
            print("✅ Profilo aggiornato correttamente nel database locale.")
            return True
            
        except Exception as e:
            print(f"❌ Errore durante la modifica del profilo: {e}")
            return False

    def registraAccount(self, nuovo_utente, password_scelta: str) -> bool:
        """
        Registra il nuovo account con hash della password e salva l'anagrafica nel database locale JSON.
        """
        if not self.validaDati(nuovo_utente.nome, nuovo_utente.cognome, nuovo_utente.cod_fiscale, nuovo_utente.telefono):
            print("❌ Dati di registrazione non validi.")
            return False
            
        try:
            hashed = hashlib.sha256(password_scelta.encode('utf-8')).hexdigest()
            nuovo_utente.password = hashed
            
            from Sistema import Sistema
            sys_inst = Sistema.get_instance()
            if sys_inst:
                if nuovo_utente not in sys_inst.volontari:
                    sys_inst.volontari.append(nuovo_utente)
                sys_inst.salva_dati()
            
            print("✅ Nuovo account registrato con successo nel database locale.")
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

        # 2. Cerca l'utente nel sistema locale
        try:
            from Sistema import Sistema
            sys_inst = Sistema.get_instance()
            if sys_inst:
                if not dest_email:
                    u = sys_inst.get_volontario(target_str.upper())
                    if u:
                        dest_email = u.email
                        nome_utente = u.getNomeCompleto() or "Volontario"
                else:
                    u = next((v for v in sys_inst.volontari if getattr(v, "email", "").strip().lower() == dest_email.lower()), None)
                    if u:
                        nome_utente = u.getNomeCompleto() or "Volontario"
        except Exception as e:
            print(f"⚠️ Ricerca utente per recupero credenziali: {e}")

        if not dest_email or "@" not in dest_email:
            return False, f"Nessun account trovato per '{target_str}'. Verifica i dati inseriti."

        # 3. Genera link di ripristino sicuro
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
            oggetto="Recupero Credenziali di Accesso — Croce Rossa Italiana"
        )

        if inviata:
            print(f"[Auth] Email di recupero inviata a {dest_email}.")
            return True, f"Istruzioni di ripristino inviate con successo all'indirizzo:\n{dest_email}"
        else:
            return False, "Impossibile inviare l'email di recupero in questo momento. Riprova più tardi."