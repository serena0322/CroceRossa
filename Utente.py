
class Utente:
    def __init__(self, cod_fiscale, nome, cognome, email, data_nascita, ruolo, telefono):
        self.cod_fiscale = cod_fiscale
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.data_nascita = data_nascita
        self.telefono = float(telefono) if isinstance(telefono, (int, float)) else telefono
        self.telefono = str(telefono)
        self.ruolo = ruolo
        self.curriculum = ""
        self.patenti = []
        self.qualifiche = []
        self.compagnia_appartenenza = ""
        self.disponibilita = []
        self.patente_pdf_path = ""
        self.formazione = []
        self.corsi_frequentati = []

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

    def get_nome_completo(self) -> str:
        return f"{self.nome} {self.cognome}"

    def descrizione_breve(self) -> str:
        return f"{self.get_nome_completo()} - CF: {self.cod_fiscale}"

    def ha_ruolo(self, ruolo: str) -> bool:
        return self.ruolo == ruolo

    def to_dict(self) -> dict:
        """Serializza l'oggetto per il salvataggio su Firestore."""
        return {
            "cod_fiscale": self.cod_fiscale,
            "nome": self.nome,
            "cognome": self.cognome,
            "email": self.email,
            "data_nascita": self.data_nascita, # Aggiunto!
            "telefono": self.telefono,         # Aggiunto!
            "ruolo": self.ruolo,
            "patente_pdf_path": self.patente_pdf_path
        }