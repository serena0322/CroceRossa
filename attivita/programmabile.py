"""Interfaccia Programmabile (realizzata da Turno e Corso)."""
from abc import ABC, abstractmethod
from attivita.stato_attivita import StatoAttivita

class Programmabile(ABC):
    @abstractmethod
    def getDati(self) -> dict: ...
    @abstractmethod
    def getStato(self) -> StatoAttivita: ...
    
