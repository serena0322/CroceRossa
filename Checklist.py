from __future__ import annotations
from typing import List

class Checklist:
    def __init__(
        self,
        id: str,
        controlliMeccanici: bool = False,
        dispositiviMediciRichiesti: List[str] = None,
        dispositiviPresenti: bool = False
    ):
        self.id = id
        self.controlliMeccanici = controlliMeccanici
        self.dispositiviMediciRichiesti = dispositiviMediciRichiesti if dispositiviMediciRichiesti is not None else []
        self.dispositiviPresenti = dispositiviPresenti

    def getControlliMeccaniciBase(self) -> List[str]:
        return ["Controllo olio", "Controllo freni", "Controllo pneumatici"]

    def getControlliMeccaniciEmergenza(self) -> List[str]:
        return ["Controllo sirena", "Controllo luci di emergenza", "Livello carburante"]

    def getDispositiviSanitariAvanzati(self) -> List[str]:
        return ["Defibrillatore", "Ossigenoterapia", "Monitor ECG"]

    def getDispositiviSanitariBase(self) -> List[str]:
        return ["Bende", "Cerotti", "Barella standard"]

    def verificaIdoneita(self) -> bool:
        return self.controlliMeccanici and self.dispositiviPresenti
