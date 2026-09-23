
class Utente:
    """
    Classe base per la gestione degli utenti del sistema Croce Rossa Italiana.
    Incapsula le informazioni anagrafiche e i metodi comuni a tutti i profili.
    """
    def __init__(self, cod_fiscale, nome, cognome, email, data_nascita, ruolo, telefono):
        self.cod_fiscale = str(cod_fiscale).strip().upper() if cod_fiscale else ""
        self.nome = str(nome).strip() if nome else ""
        self.cognome = str(cognome).strip() if cognome else ""
        self.email = str(email).strip().lower() if email else ""
        self.data_nascita = str(data_nascita).strip() if data_nascita else ""
        self.telefono = str(telefono).strip() if telefono is not None else ""
        self.ruolo = str(ruolo).strip().lower() if ruolo else "volontario"
        
        # Campi di stato e appartenenza associativa
        self.compagnia_appartenenza = ""
        self.curriculum = ""
        self.patenti = []
        self.qualifiche = []
        self.disponibilita = []
        self.patente_pdf_path = ""
        self.formazione = []
        self.corsi_frequentati = []

    # --- Property per garantire compatibilità con le varie convenzioni di naming dell'UML ---
    @property
    def nascita(self) -> str:
        return self.data_nascita

    @nascita.setter
    def nascita(self, val: str):
        self.data_nascita = val

    @property
    def dataNascita(self) -> str:
        return self.data_nascita

    @dataNascita.setter
    def dataNascita(self, val: str):
        self.data_nascita = val

    @property
    def codFiscale(self) -> str:
        return self.cod_fiscale

    @codFiscale.setter
    def codFiscale(self, val: str):
        self.cod_fiscale = val

    @property
    def comitato_appartenenza(self) -> str:
        """Denominazione ufficiale del comitato CRI territoriale di afferenza (UML)."""
        return self.compagnia_appartenenza

    @comitato_appartenenza.setter
    def comitato_appartenenza(self, val: str):
        self.compagnia_appartenenza = val

    @property
    def com_appartenenza(self) -> str:
        return self.compagnia_appartenenza

    @com_appartenenza.setter
    def com_appartenenza(self, val: str):
        self.compagnia_appartenenza = val

    # --- Metodi di utilità anagrafica ---
    def get_nome_completo(self) -> str:
        """Restituisce nome e cognome formattati per la visualizzazione a video."""
        return f"{self.nome} {self.cognome}".strip()

    def getNomeCompleto(self) -> str:
        """Alias camelCase conforme al diagramma delle classi UML."""
        return self.get_nome_completo()

    def descrizione_breve(self) -> str:
        """Fornisce una sintesi identificativa con nome, cognome e codice fiscale."""
        return f"{self.get_nome_completo()} - CF: {self.cod_fiscale}"

    def ha_ruolo(self, ruolo: str) -> bool:
        """Verifica se l'utente possiede un determinato ruolo nel sistema."""
        return self.ruolo == (ruolo.strip().lower() if ruolo else "")

    def haRuolo(self, ruolo: str) -> bool:
        """Alias camelCase conforme al diagramma delle classi UML."""
        return self.ha_ruolo(ruolo)

    def validaDati(self) -> bool:
        """
        Verifica la validità dell'anagrafica di base.
        Controlla che i campi minimi obbligatori siano valorizzati.
        """
        return bool(self.cod_fiscale and self.nome and self.cognome and self.email)

    def to_dict(self) -> dict:
        """
        Serializza l'oggetto in un dizionario compatibile con i documenti Firestore.
        Facilita la persistenza su database NoSQL.
        """
        return {
            "cod_fiscale": self.cod_fiscale,
            "nome": self.nome,
            "cognome": self.cognome,
            "email": self.email,
            "data_nascita": self.data_nascita,
            "telefono": self.telefono,
            "ruolo": self.ruolo,
            "compagnia_appartenenza": self.compagnia_appartenenza,
            "comitato_appartenenza": self.compagnia_appartenenza,
            "patente_pdf_path": self.patente_pdf_path
        }