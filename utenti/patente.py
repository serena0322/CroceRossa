from __future__ import annotations
from datetime import date
from typing import TYPE_CHECKING
from dati.gestore_dati import GestoreDati

if TYPE_CHECKING:
    from utenti.volontario import Volontario

class Patente:
    def __init__(self): 
        self.__codice = ""
        self.__dataScadenza = date.min
        self.__tipo = ""

    def getDati(self) -> dict:
        return {
            "codice": self.__codice,
            "tipo": self.__tipo,
            "dataScadenza": self.__dataScadenza
        }

    def setDataScadenza(self, data: date) -> None:
        self.__dataScadenza = data

    def verificaValidita(self, data: date) -> bool:
        """Valida a una certa data (es. la data del turno) se non scade prima."""
        return self.__dataScadenza >= data

    # inserimento
    def inserisciPatente(self, codice: str) -> bool:
        """True se il codice e' libero (la patente non e' presente)."""
        return len(self.ricercaPatente({"codice": codice})) == 0

    def inserisciDatiPatente(self, codice: str, tipo: str, dataScadenza: date,
                             volontario: Volontario) -> None:
        self.__codice, self.__tipo, self.__dataScadenza = codice, tipo, dataScadenza
        dati = GestoreDati().carica()
        dati["patenti"][codice] = self
        volontario.aggiungiPatente(self)
        GestoreDati().salva(dati)

    # modifica
    def modificaPatente(self, codice: str, volontario: Volontario) -> dict:
        """Dati della patente se e' tra quelle del Volontario, altrimenti {}."""
        trovate = self.ricercaPatente({"codice": codice})
        if trovate and trovate[0] in volontario.visualizzaPatenti():
            return trovate[0].getDati()
        return {}

    def inserisciModifiche(self, patente: Patente, dataScadenza: date) -> None:
        patente.setDataScadenza(dataScadenza)
        GestoreDati().salva(GestoreDati().carica())

    # eliminazione
    def eliminaPatente(self, codice: str, volontario: Volontario) -> bool:
        trovate = self.ricercaPatente({"codice": codice})
        if not trovate or trovate[0] not in volontario.visualizzaPatenti():
            return False
        dati = GestoreDati().carica()
        volontario.eliminaPatente(trovate[0])
        del dati["patenti"][codice]
        GestoreDati().salva(dati)
        return True

    # RicercaPatente
    def ricercaPatente(self, criterio: dict) -> list[Patente]:
        criterio = self.__prelevaCriterio(criterio)
        trovate: list[Patente] = []
        for patente in GestoreDati().carica()["patenti"].values():
            if patente.soddisfaCriterio(criterio):
                self.__aggiungiATrovati(patente, trovate)
        return trovate

    def __prelevaCriterio(self, criterio: dict) -> dict:
        return {chiave: valore for chiave, valore in criterio.items() if valore not in ("", None)}

    def soddisfaCriterio(self, criterio: dict) -> bool:
        dati = self.getDati()
        return all(dati.get(chiave) == valore for chiave, valore in criterio.items())

    def __aggiungiATrovati(self, patente: Patente, trovate: list[Patente]) -> None:
        trovate.append(patente)
