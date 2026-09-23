from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from Turno import Turno
    from Volontario import Volontario

class Report:
    """
    Rappresenta il resoconto di missione / fine turno redatto dal caposquadra o soccorritore.
    Registra i chilometri percorsi dall'automezzo, il monte ore effettivo di servizio
    e le note operative dell'intervento.
    """
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
        """
        Calcola la distanza percorsa come differenza tra chilometraggio finale e iniziale (UML).
        Garantisce la non-negatività del valore calcolato.
        """
        if self.kmFinali and self.kmFinali >= self.kmIniziali:
            return self.kmFinali - self.kmIniziali
        return self.kmPercorsi

    def creaResoconto(self) -> bool:
        """
        Valida la coerenza metrica del resoconto operativo (UML):
        Verifica che i chilometri finali non siano inferiori a quelli rilevati ad inizio servizio.
        """
        if self.kmFinali and self.kmFinali < self.kmIniziali:
            return False
        return True

    def getKmPercorsi(self) -> int:
        """Restituisce i chilometri percorsi calcolati (UML)."""
        return self.calcolaKmPercorsi()

    def getOreEffettive(self) -> int:
        """Restituisce le ore di servizio effettivamente prestate dal soccorritore (UML)."""
        return self.oreEffettive

