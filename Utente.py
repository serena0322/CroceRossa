
class Utente:
    def __init__(self, cod_fiscale, nome, cognome, email, data_nascita, ruolo, telefono):
        self.cod_fiscale = cod_fiscale
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.data_nascita = data_nascita
        self.telefono = telefono
        self.ruolo = ruolo

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
            "ruolo": self.ruolo
        }