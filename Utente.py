from __future__ import annotations

class Utente:
    """
    Classe base per la gestione degli utenti del sistema Croce Rossa Italiana.
    Incapsula le informazioni anagrafiche e i metodi comuni a tutti i profili
    (cod_fiscale, nome, cognome, email, data_nascita, ruolo, telefono, comitato_appartenenza).
    
    Come da specifiche UML aggiornate:
    - Associazioni con Corsi, Turni e Patenti partono da Volontario, non da Utente.
    - La 'Gestione Disponibilità' è stata eliminata.
    - L'attributo 'ruolo' e il metodo 'haRuolo(String)' sono mantenuti per l'RNF 'Autorizzazione per Ruolo'.
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
        self.comitato_appartenenza = str(comitato_appartenenza or kwargs.get("compagnia_appartenenza", "")).strip()

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
        """Verifica se l'utente possiede un determinato ruolo nel sistema (RNF Autorizzazione)."""
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
            "comitato_appartenenza": self.comitato_appartenenza
        }

    def __repr__(self) -> str:
        return f"<Utente {self.cod_fiscale} ({self.ruolo}) - {self.get_nome_completo()}>"