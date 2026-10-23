from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from Corso import Corso
    from Volontario import Volontario


class Iscrizione:
    """
    Rappresenta l'iscrizione di un volontario a un corso di formazione.
    Classe conforme al package Attivita del diagramma delle classi UML.

    Attributi UML:
        codice: str
        corso: Corso
        dataIscrizione: str (Data)
        superato: bool (Boolean)
        volontario: Volontario
    """
    def __init__(
        self,
        codice: str = "",
        corso: Corso | None = None,
        dataIscrizione: str = "",
        superato: bool = False,
        volontario: Volontario | None = None,
        **kwargs
    ):
        self.codice = codice or kwargs.get("id", f"ISC_{getattr(corso, 'codice', '')}_{getattr(volontario, 'cod_fiscale', '')}")
        self.corso = corso
        self.dataIscrizione = dataIscrizione or datetime.now().strftime("%Y-%m-%d")
        self.superato = superato
        self.volontario = volontario

    def setSuperato(self, superato: bool = True) -> None:
        """Registra l'esito del superamento del corso per il volontario (UML AttestaPartecipazione)."""
        self.superato = superato

    def to_dict(self) -> dict:
        return {
            "codice": self.codice,
            "corso_codice": getattr(self.corso, "codice", getattr(self.corso, "id", "")),
            "dataIscrizione": self.dataIscrizione,
            "superato": self.superato,
            "volontario_cf": getattr(self.volontario, "cod_fiscale", "")
        }
