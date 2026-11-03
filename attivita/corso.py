"""Package Attivita: Corso (CUDCorso, RicercaCorso, catalogo, VisualizzaCorsi, iscritti,
AttestaPartecipazione, AggiornaStatoCorso). Stessa struttura di Turno."""
from __future__ import annotations
from datetime import date
from typing import TYPE_CHECKING
from attivita.programmabile import Programmabile
from attivita.stato_attivita import StatoAttivita
from dati.gestore_dati import GestoreDati
from supporto import orologio

if TYPE_CHECKING:
    from attivita.iscrizione import Iscrizione
    from utenti.volontario import Volontario

class Corso(Programmabile):
    def __init__(self):  # create(): void
        self.__codice = ""
        self.__dataFine = date.min
        self.__dataInizio = date.min
        self.__descrizione = ""
        self.__direttoreCorso = ""
        self.__luogo = ""
        self.__nome = ""
        self.__orario = ""
        self.__postiLiberi = 0
        self.__postiTotali = 0
        self.__stato = StatoAttivita.PROGRAMMATO
        self.__tipoCorso = ""
        self.__iscrizioni: list[Iscrizione] = []

    def getDati(self) -> dict:
        return {
            "codice": self.__codice,
            "nome": self.__nome,
            "descrizione": self.__descrizione,
            "direttoreCorso": self.__direttoreCorso,
            "tipoCorso": self.__tipoCorso,
            "dataInizio": self.__dataInizio,
            "dataFine": self.__dataFine,
            "orario": self.__orario,
            "luogo": self.__luogo,
            "postiTotali": self.__postiTotali,
            "postiLiberi": self.__postiLiberi,
            "stato": self.__stato,
            "numeroIscrizioni": len(self.__iscrizioni),
            "numeroIscritti": len(self.__iscrizioni),
            "numeroSuperati": sum(1 for i in self.__iscrizioni if i.getSuperato())
        }

    def getStato(self) -> StatoAttivita:
        return self.__stato

    def setStato(self, stato: StatoAttivita) -> None:
        self.__stato = stato

    def setPostiLiberi(self, posti: int) -> None:
        self.__postiLiberi = posti

    def getDataInizio(self) -> date:
        return self.__dataInizio

    def aggiungiIscrizione(self, iscrizione: Iscrizione) -> None:
        self.__iscrizioni.append(iscrizione)
        self.setPostiLiberi(self.__postiLiberi - 1)

    def eliminaIscrizione(self, iscrizione: Iscrizione) -> None:
        self.__iscrizioni.remove(iscrizione)
        if self.__stato == StatoAttivita.PROGRAMMATO:
            self.setPostiLiberi(self.__postiLiberi + 1)

    def getIscrizioni(self) -> list[Iscrizione]:
        return list(self.__iscrizioni)

    # ---------- CUDCorso ----------
    def inserisciCorso(self, codice: str) -> bool:
        return len(self.ricercaCorso({"codice": codice})) == 0

    def inserisciDatiCorso(self, codice: str, nome: str, descrizione: str, direttoreCorso: str,
                           tipoCorso: str, dataInizio: date, dataFine: date, orario: str,
                           luogo: str, postiTotali: int) -> None:
        self.__validaDati(dataInizio, dataFine, postiTotali, 0)
        self.__codice = codice
        self.setDati(nome, descrizione, direttoreCorso, tipoCorso, dataInizio, dataFine,
                     orario, luogo, postiTotali)
        self.__stato = StatoAttivita.PROGRAMMATO
        self.__postiLiberi = postiTotali
        dati = GestoreDati().carica()
        dati["corsi"][codice] = self
        GestoreDati().salva(dati)

    def setDati(self, nome: str, descrizione: str, direttoreCorso: str, tipoCorso: str,
                dataInizio: date, dataFine: date, orario: str, luogo: str,
                postiTotali: int) -> None:
        self.__nome, self.__descrizione = nome, descrizione
        self.__direttoreCorso, self.__tipoCorso = direttoreCorso, tipoCorso
        self.__dataInizio, self.__dataFine = dataInizio, dataFine
        self.__orario, self.__luogo, self.__postiTotali = orario, luogo, postiTotali

    def __validaDati(self, dataInizio: date, dataFine: date, postiTotali: int,
                     iscritti: int) -> None:  # NF5
        if dataInizio < orologio.adesso().date():
            raise ValueError("La data di inizio non puo' essere gia' passata.")
        if dataFine < dataInizio:
            raise ValueError("La data di fine non puo' precedere quella di inizio.")
        if postiTotali <= 0 or postiTotali < iscritti:
            raise ValueError("Numero di posti non valido.")

    def modificaCorso(self, codice: str) -> dict:
        trovati = self.ricercaCorso({"codice": codice})
        if trovati and trovati[0].getStato() == StatoAttivita.PROGRAMMATO:
            return trovati[0].getDati()
        return {}

    def inserisciModifiche(self, corso: Corso, nome: str, descrizione: str, direttoreCorso: str,
                           tipoCorso: str, dataInizio: date, dataFine: date, orario: str,
                           luogo: str, postiTotali: int) -> bool:
        iscritti = len(corso.getIscrizioni())
        if postiTotali < iscritti:
            return False
        self.__validaDati(dataInizio, dataFine, postiTotali, iscritti)
        corso.setDati(nome, descrizione, direttoreCorso, tipoCorso, dataInizio, dataFine,
                      orario, luogo, postiTotali)
        corso.setPostiLiberi(postiTotali - iscritti)
        for iscrizione in corso.getIscrizioni():
            iscrizione.notificaModifica()
        GestoreDati().salva(GestoreDati().carica())
        return True

    def rimuoviCorso(self, codice: str) -> bool:
        trovati = self.ricercaCorso({"codice": codice})
        if not trovati or trovati[0].getStato() != StatoAttivita.PROGRAMMATO:
            return False
        dati = GestoreDati().carica()
        for iscrizione in trovati[0].getIscrizioni():
            iscrizione.notificaEliminazione()
            dati["iscrizioni"].pop(iscrizione.getDati()["codice"], None)
        del dati["corsi"][codice]
        GestoreDati().salva(dati)
        return True

    # ---------- RicercaCorso ----------
    def ricercaCorso(self, criterio: dict) -> list[Corso]:
        criterio = self.__prelevaCriterio(criterio)
        trovati: list[Corso] = []
        for corso in GestoreDati().carica()["corsi"].values():
            if corso.soddisfaCriterio(criterio):
                self.__aggiungiATrovati(corso, trovati)
        return trovati

    def __prelevaCriterio(self, criterio: dict) -> dict:
        return {chiave: valore for chiave, valore in criterio.items() if valore not in ("", None)}

    def soddisfaCriterio(self, criterio: dict) -> bool:
        for chiave, valore in criterio.items():
            if chiave == "stati":
                if self.__stato not in valore:
                    return False
            elif chiave == "inizioEntro":
                if self.__dataInizio > valore:
                    return False
            elif chiave == "disponibile":
                if not (self.__stato == StatoAttivita.PROGRAMMATO and self.__postiLiberi > 0):
                    return False
            elif chiave == "tipoCorso":
                # Ricerca insensibile a maiuscole/minuscole e per sottostringa per facilitare l'input da testo
                if valore.lower() not in self.__tipoCorso.lower():
                    return False
            elif self.getDati().get(chiave) != valore:
                return False
        return True

    def __aggiungiATrovati(self, corso: Corso, trovati: list[Corso]) -> None:
        trovati.append(corso)

    # ---------- visualizzazioni ----------
    def visualizzaCatalogoCorsi(self) -> list[Corso]:
        return self.ricercaCorso({"disponibile": True})

    def filtraCorsi(self, tipoCorso: str) -> list[Corso]:
        trovati = []
        for corso in self.visualizzaCatalogoCorsi():
            corso.getDati()
            if corso.soddisfaCriterio(self.__prelevaCriterio({"tipoCorso": tipoCorso})):
                self.__aggiungiATrovati(corso, trovati)
        return trovati

    def visualizzaCorsi(self) -> list[Corso]:
        return self.__ordinaPerData(list(GestoreDati().carica()["corsi"].values()))

    def __ordinaPerData(self, corsi: list[Corso]) -> list[Corso]:
        return sorted(corsi, key=lambda c: c.getDataInizio(), reverse=True)

    def visualizzaDettagliCorso(self, corso: Corso) -> dict:
        return corso.getDati()

    def visualizzaIscrittiCorso(self, corso: Corso) -> list[dict]:
        ordinate = sorted(corso.getIscrizioni(), key=lambda i: i.getDataIscrizione())
        risultato = []
        for iscrizione in ordinate:  # loop for each
            dati = iscrizione.getDatiVolontario()  # -> getDati()
            dati["dataIscrizione"] = iscrizione.getDataIscrizione()
            risultato.append(dati)
        return risultato  # elencoIscritti()

    # ---------- AttestaPartecipazione ----------
    def attestaPartecipazione(self, corso: Corso) -> list[Volontario]:
        """Iscritti del corso se e' concluso e ha iscritti, altrimenti lista vuota."""
        if corso.getStato() != StatoAttivita.CONCLUSO:
            return []
        return [i.getVolontario() for i in corso.getIscrizioni()]

    def selezionaSuperati(self, corso: Corso, superati: list[Volontario]) -> None:
        for iscrizione in corso.getIscrizioni():
            if iscrizione.getVolontario() in superati:
                iscrizione.setSuperato()
            else:
                iscrizione.setNonSuperato()
        GestoreDati().salva(GestoreDati().carica())

    # ---------- AggiornaStatoCorso (Tempo, ogni giorno alle 00.00) ----------
    def __impostaCriterio(self) -> dict:
        return {
            "stati": {StatoAttivita.PROGRAMMATO, StatoAttivita.IN_CORSO},
            "inizioEntro": orologio.adesso().date()
        }

    def aggiornaStatoCorsi(self) -> None:
        oggi = orologio.adesso().date()
        for corso in self.ricercaCorso(self.__impostaCriterio()):
            if corso.getStato() == StatoAttivita.PROGRAMMATO:
                corso.setStato(StatoAttivita.IN_CORSO)
            if corso.getDati()["dataFine"] < oggi:
                corso.setStato(StatoAttivita.CONCLUSO)
        GestoreDati().salva(GestoreDati().carica())
