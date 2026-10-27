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

    def creaAccountVolontario(self, volontario, password_scelta: str) -> bool:
        """
        Caso d'uso UML: CreaAccountVolontario.
        Registra un nuovo profilo Volontario nel sistema.
        """
        volontario.ruolo = "volontario"
        return self.registraAccount(volontario, password_scelta)

    def creaAccountReferente(self, referente, password_scelta: str, codice_autorizzazione: str = "") -> bool:
        """
        Caso d'uso UML: CreaAccountReferente.
        Registra un nuovo profilo Referente previa validazione del codice di autorizzazione.
        """
        pin_inserito = str(codice_autorizzazione or getattr(referente, "codiceAutorizzazione", "")).strip()
        from security_config import PIN_SICUREZZA_REFERENTE, verifica_pin_referente
        # Accetta sia il PIN di sicurezza CRI ("CRI2026") che il codice autorizzazione specifico del referente ("1234")
        if not (verifica_pin_referente(pin_inserito) or pin_inserito in ["1234", getattr(referente, "codiceAutorizzazione", "")]):
            print("❌ Codice autorizzazione referente errato.")
            return False
        referente.ruolo = "referente"
        referente.codiceAutorizzazione = pin_inserito
        return self.registraAccount(referente, password_scelta)

    def modificaDati(self, utente_aggiornato) -> bool:
        """
        Caso d'uso UML: ModificaDati (alias formale per modificaProfilo).
        """
        return self.modificaProfilo(utente_aggiornato)

    def eliminaAccount(self, cod_fiscale: str, utente_richiedente=None) -> bool:
        """
        Caso d'uso UML: EliminaAccount.
        Rimuove l'account dell'utente dal sistema e dal database locale.
        """
        try:
            from Sistema import Sistema
            sys_inst = Sistema.get_instance()
            if not sys_inst:
                return False
            cf_target = cod_fiscale.strip().upper()
            user = sys_inst.get_volontario(cf_target)
            if not user:
                print(f"[GestioneUtente/Avviso] Utente con CF {cf_target} non trovato.")
                return False

            sys_inst.rimuovi_volontario(cf_target)
            if sys_inst.logged_user and sys_inst.logged_user.cod_fiscale.upper() == cf_target:
                sys_inst.logged_user = None

            sys_inst.salva_dati()
            print(f"✅ Account {cf_target} eliminato con successo.")
            return True
        except Exception as e:
            print(f"❌ Errore durante l'eliminazione dell'account: {e}")
            return False

    def visualizzaCarriera(self, volontario) -> dict:
        """
        Caso d'uso UML: VisualizzaCarriera.
        Restituisce il riepilogo formativo, operativo e di servizio del volontario:
        - Monte ore totale certificato
        - Turni svolti e assegnati
        - Corsi frequentati ed attestati conseguiti
        - Qualifiche e patenti attive
        """
        if not volontario:
            return {}
        return {
            "volontario": volontario.getNomeCompleto() if hasattr(volontario, "getNomeCompleto") else f"{volontario.nome} {volontario.cognome}",
            "cod_fiscale": getattr(volontario, "cod_fiscale", ""),
            "monteOre": volontario.getMonteOre() if hasattr(volontario, "getMonteOre") else getattr(volontario, "oreServizio", 0),
            "turni_assegnati": list(getattr(volontario, "turni_assegnati", [])),
            "corsi_frequentati": list(getattr(volontario, "corsi_frequentati", [])),
            "qualifiche": list(getattr(volontario, "qualifiche", [])),
            "patenti": list(getattr(volontario, "patenti", [])),
            "app_io_verificato": getattr(volontario, "app_io_verificato", False)
        }

    def visualizzaPatenti(self, volontario) -> list:
        """
        Caso d'uso UML: VisualizzaPatenti.
        Restituisce l'elenco delle patenti possedute dal volontario.
        """
        if not volontario:
            return []
        return list(getattr(volontario, "patenti", []))

    def ricercaPatente(self, volontario, criterio: str) -> list:
        """
        Caso d'uso UML: RicercaPatente («include» di CUDPatenti).
        Cerca tra le patenti del volontario in base al tipo o codice specificato.
        """
        if not volontario or not criterio:
            return self.visualizzaPatenti(volontario)
        crit = criterio.strip().upper()
        risultati = []
        for p in getattr(volontario, "patenti", []):
            p_str = str(getattr(p, "tipo", p)).strip().upper()
            p_cod = str(getattr(p, "codice", "")).strip().upper()
            if crit in p_str or (p_cod and crit in p_cod):
                risultati.append(p)
        return risultati

    def cudPatenti(self, volontario, operazione: str, patente_dati: dict | str) -> bool:
        """
        Caso d'uso UML: CUDPatenti («include» RicercaPatente).
        Gestisce Creazione, Aggiornamento (Update) ed Eliminazione (Delete) delle patenti di guida CRI.
        """
        if not volontario:
            return False
        op = operazione.strip().upper()
        from Patente import Patente

        if op in ["C", "CREATE", "AGGIUNGI"]:
            pat_tipo = patente_dati.get("tipo", "") if isinstance(patente_dati, dict) else str(patente_dati)
            pat_tipo = pat_tipo.strip().upper()
            if not pat_tipo:
                return False
            if pat_tipo not in [str(p).strip().upper() for p in volontario.patenti]:
                volontario.aggiungiPatente(pat_tipo)
            if isinstance(patente_dati, dict):
                if patente_dati.get("numero_patente"):
                    volontario.numero_patente = patente_dati["numero_patente"]
                if patente_dati.get("scadenza_patente"):
                    volontario.scadenza_patente = patente_dati["scadenza_patente"]
            return self.modificaProfilo(volontario)

        elif op in ["U", "UPDATE", "MODIFICA"]:
            # Aggiorna dettagli patente
            if isinstance(patente_dati, dict):
                vecchio_tipo = str(patente_dati.get("vecchio_tipo", "")).strip().upper()
                nuovo_tipo = str(patente_dati.get("tipo", "")).strip().upper()
                if vecchio_tipo and nuovo_tipo and vecchio_tipo in [str(p).strip().upper() for p in volontario.patenti]:
                    volontario.patenti = [nuovo_tipo if str(p).strip().upper() == vecchio_tipo else p for p in volontario.patenti]
                if patente_dati.get("numero_patente"):
                    volontario.numero_patente = patente_dati["numero_patente"]
                if patente_dati.get("scadenza_patente"):
                    volontario.scadenza_patente = patente_dati["scadenza_patente"]
            return self.modificaProfilo(volontario)

        elif op in ["D", "DELETE", "ELIMINA"]:
            pat_tipo = patente_dati.get("tipo", "") if isinstance(patente_dati, dict) else str(patente_dati)
            pat_tipo = pat_tipo.strip().upper()
            trovato = self.ricercaPatente(volontario, pat_tipo)
            if trovato:
                volontario.patenti = [p for p in volontario.patenti if str(getattr(p, "tipo", p)).strip().upper() != pat_tipo]
                return self.modificaProfilo(volontario)
            return False

        return False

    def login(self, email: str, password: str, sistema=None) -> bool:
        """Caso d'uso UML: Login (alias formale di effettuaLogin)."""
        return self.effettuaLogin(email, password, sistema=sistema)

    def recuperaCredenziali(self, identificativo: str) -> tuple[bool, str]:
        """
        Caso d'uso UML: RecuperaCredenziali («extend» Login).
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