from __future__ import annotations


class Utente:
    """
    Classe base per la gestione degli utenti del sistema Croce Rossa Italiana.
    Conforme al package Utenti del diagramma delle classi UML.

    Attributi UML:
        comitato: str (String)
        email: str (String)
        password: str (String)
        telefono: str (String)

    Metodi UML:
        getEmail(), getPassword(), setPassword(), validaInformazioni(),
        inviaEmail(), getNomeCompleto(), haRuolo(), validaDati().
    """
    def __init__(
        self,
        cod_fiscale: str = "",
        nome: str = "",
        cognome: str = "",
        email: str = "",
        data_nascita: str = "",
        ruolo: str = "volontario",
        telefono: str = "",
        comitato: str = "",
        password: str = "",
        # Compatibility arguments:
        comitato_appartenenza: str = "",
        **kwargs
    ):
        self.cod_fiscale = str(cod_fiscale).strip().upper() if cod_fiscale else ""
        self.nome = str(nome).strip() if nome else ""
        self.cognome = str(cognome).strip() if cognome else ""
        self.email = str(email).strip().lower() if email else ""
        self.data_nascita = str(data_nascita).strip() if data_nascita else ""
        self.telefono = str(telefono).strip() if telefono is not None else ""
        self.ruolo = str(ruolo).strip().lower() if ruolo else "volontario"
        self.password = str(password or kwargs.get("pwd", "")).strip()
        self.comitato = str(comitato or comitato_appartenenza or kwargs.get("compagnia_appartenenza", "")).strip()
        self.comitato_appartenenza = self.comitato

    def getEmail(self) -> str:
        """Restituisce l'email dell'utente (UML Login / CreaAccountReferente)."""
        return self.email

    def getPassword(self) -> str:
        """Restituisce la password dell'utente (UML Login)."""
        return getattr(self, "password", "")

    def setPassword(self, pwd: str) -> None:
        """Imposta la password dell'utente (UML Login)."""
        self.password = pwd

    def validaInformazioni(self) -> bool:
        """Verifica la validità delle informazioni fornite (UML CreaAccountReferente)."""
        return bool(self.email and "@" in self.email and self.password)

    def inviaEmail(self, oggetto: str, messaggio: str) -> None:
        """Invia un'email all'indirizzo dell'utente (UML InviaPromemoriaTurno / Login)."""
        from EmailService import EmailService
        EmailService.inviaMail(
            destinatario=self.email,
            messaggio=messaggio,
            oggetto=oggetto
        )

    def getNomeCompleto(self) -> str:
        """Restituisce nome e cognome formattati per la visualizzazione a video (UML)."""
        return f"{self.nome} {self.cognome}".strip()

    def haRuolo(self, ruolo: str) -> bool:
        """Verifica se l'utente possiede un determinato ruolo nel sistema (UML)."""
        return self.ruolo == (ruolo.strip().lower() if ruolo else "")

    def validaDati(self) -> bool:
        """
        Verifica la validità dell'anagrafica di base.
        Controlla che i campi minimi obbligatori siano valorizzati.
        """
        return bool(self.cod_fiscale and self.nome and self.cognome and self.email)

    def to_dict(self) -> dict:
        """
        Serializza l'oggetto in un dizionario per il salvataggio persistente nel database locale JSON.
        """
        return {
            "cod_fiscale": self.cod_fiscale,
            "nome": self.nome,
            "cognome": self.cognome,
            "email": self.email,
            "data_nascita": self.data_nascita,
            "telefono": self.telefono,
            "ruolo": self.ruolo,
            "password": getattr(self, "password", ""),
            "comitato": self.comitato,
            "comitato_appartenenza": self.comitato
        }

    def __repr__(self) -> str:
        return f"<Utente {self.cod_fiscale} ({self.ruolo}) - {self.getNomeCompleto()}>"