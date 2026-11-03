"""Interfaccia Programmabile (realizzata da Turno e Corso).
Python non ha la parola chiave "interface": la si scrive come classe astratta
SENZA attributi e con SOLI metodi astratti, cioe' solo le signature.
"""
from abc import ABC, abstractmethod
from attivita.stato_attivita import StatoAttivita

class Programmabile(ABC):
    @abstractmethod
    def getDati(self) -> dict: ...
    @abstractmethod
    def getStato(self) -> StatoAttivita: ...
    #@abstractmethod
    #def setPostiLiberi(self, posti: int) -> None: ...
    #@abstractmethod
    #def setStato(self, stato: StatoAttivita) -> None: ...
