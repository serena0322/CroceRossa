from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from Turno import Turno
    from Volontario import Volontario

class Report:
    def __init__(
        self,
        id: str,
        kmPercorsi: int = 0,
        noteIntervento: str = "",
        oreEffettive: int = 0,
        turnoEseguito: Optional[Turno] = None,
        compilatoDa: Optional[Volontario] = None
    ):
        self.id = id
        self.kmPercorsi = kmPercorsi
        self.noteIntervento = noteIntervento
        self.oreEffettive = oreEffettive
        self.turnoEseguito = turnoEseguito
        self.compilatoDa = compilatoDa

    def getKmPercorsi(self) -> int:
        return self.kmPercorsi

    def getOreEffettive(self) -> int:
        return self.oreEffettive

