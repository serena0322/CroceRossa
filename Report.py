from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from Turno import Turno
    from Volontario import Volontario

class Report:
    def __init__(
        self,
        id: str,
        kmIniziali: int = 0,
        kmFinali: int = 0,
        kmPercorsi: int = 0,
        noteIntervento: str = "",
        oreEffettive: int = 0,
        turnoEseguito: Optional[Turno] = None,
        compilatoDa: Optional[Volontario] = None
    ):
        self.id = id
        self.kmIniziali = kmIniziali
        self.kmFinali = kmFinali
        self.kmPercorsi = kmPercorsi if kmPercorsi else (max(0, kmFinali - kmIniziali) if kmFinali >= kmIniziali else 0)
        self.noteIntervento = noteIntervento
        self.oreEffettive = oreEffettive
        self.turnoEseguito = turnoEseguito
        self.compilatoDa = compilatoDa

    def calcolaKmPercorsi(self) -> int:
        """Calcola la differenza tra chilometri finali e chilometri iniziali."""
        if self.kmFinali and self.kmFinali >= self.kmIniziali:
            return self.kmFinali - self.kmIniziali
        return self.kmPercorsi

    def creaResoconto(self) -> bool:
        """Valida la consistenza del resoconto operativo."""
        if self.kmFinali and self.kmFinali < self.kmIniziali:
            return False
        return True

    def getKmPercorsi(self) -> int:
        return self.calcolaKmPercorsi()

    def getOreEffettive(self) -> int:
        return self.oreEffettive

