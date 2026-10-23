from __future__ import annotations
from enum import Enum


class StatoAttivita(str, Enum):
    """
    Enumerazione conforme al diagramma UML delle classi Attivita.
    Definisce i possibili stati di un Turno o di un Corso.
    """
    PROGRAMMATO = "PROGRAMMATO"
    IN_CORSO = "IN_CORSO"
    CONCLUSO = "CONCLUSO"
