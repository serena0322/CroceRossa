"""Package Attivita: Turno (CUDTurno, RicercaTurno, VisualizzaTurni, VisualizzaTurniDisponibili,
FiltraTurni, VisualizzaDettagliTurno, VisualizzaPrenotatiTurno, AggiornaStatoTurno, InviaPromemoriaTurno)."""
from __future__ import annotations
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING
from attivita.programmabile import Programmabile
from attivita.stato_attivita import StatoAttivita
from dati.gestore_dati import GestoreDati
from supporto import orologio

if TYPE_CHECKING:
    from attivita.prenotazione import Prenotazione
    from utenti.volontario import Volontario

class Turno(Programmabile):
    def __init__(self):  # create(): void
        self.__codice = ""
        self.__corsiRichiesti = ""
        self.__data = date.min
        self.__datiPaziente = ""
        self.__luogo = ""
        self.__materialeNecessario = ""
        self.__mezzo = ""
        self.__oraFine = time.min
        self.__oraInizio = time.min
        self.__patenteRichiesta = ""
        self.__postiLiberi = 0
        self.__postiTotali = 0
        self.__stato = StatoAttivita.PROGRAMMATO
        self.__tipoServizio = ""
        self.__prenotazioni: list[Prenotazione] = []

    # ---------- Programmabile ----------
    def getDati(self) -> dict:
        return {
            "codice": self.__codice,
            "datiPaziente": self.__datiPaziente,
            "data": self.__data,
            "oraInizio": self.__oraInizio,
            "oraFine": self.__oraFine,
            "luogo": self.__luogo,
            "tipoServizio": self.__tipoServizio,
            "postiTotali": self.__postiTotali,
            "postiLiberi": self.__postiLiberi,
            "patenteRichiesta": self.__patenteRichiesta,
            "corsiRichiesti": self.__corsiRichiesti,
            "mezzo": self.__mezzo,
            "materialeNecessario": self.__materialeNecessario,
            "stato": self.__stato,
            "numeroPrenotazioni": len(self.__prenotazioni),
            "numeroPrenotati": len(self.__prenotazioni)
        }

    def getStato(self) -> StatoAttivita:
        return self.__stato

    def setStato(self, stato: StatoAttivita) -> None:
        self.__stato = stato

    def setPostiLiberi(self, posti: int) -> None:
        self.__postiLiberi = posti

    def getDataOraInizio(self) -> datetime:
        return datetime.combine(self.__data, self.__oraInizio)

    def getDataOraFine(self) -> datetime:
        return datetime.combine(self.__data, self.__oraFine)

    def aggiungiPrenotazione(self, prenotazione: Prenotazione) -> None:
        self.__prenotazioni.append(prenotazione)

    def eliminaPrenotazione(self, prenotazione: Prenotazione) -> None:
        self.__prenotazioni.remove(prenotazione)

    def getPrenotazioni(self) -> list[Prenotazione]:
        return list(self.__prenotazioni)

    # ---------- CUDTurno: inserimento ----------
    def inserisciTurno(self, codice: str) -> bool:
        return len(self.ricercaTurno({"codice": codice})) == 0

    def inserisciDatiTurno(self, codice: str, datiPaziente: str, data: date, oraInizio: time,
                           oraFine: time, luogo: str, tipoServizio: str, postiTotali: int,
                           patenteRichiesta: str, corsiRichiesti: str, mezzo: str,
                           materialeNecessario: str) -> None:
        """Solleva ValueError se i dati violano NF5 (la vista mostra il messaggio)."""
        self.__validaDati(data, oraInizio, oraFine, postiTotali, 0)
        self.__codice = codice
        self.setDati(datiPaziente, data, oraInizio, oraFine, luogo, tipoServizio, postiTotali,
                     patenteRichiesta, corsiRichiesti, mezzo, materialeNecessario)
        self.__stato = StatoAttivita.PROGRAMMATO
        self.__postiLiberi = postiTotali
        dati = GestoreDati().carica()
        dati["turni"][codice] = self
        GestoreDati().salva(dati)

    def setDati(self, datiPaziente: str, data: date, oraInizio: time, oraFine: time, luogo: str,
                tipoServizio: str, postiTotali: int, patenteRichiesta: str,
                corsiRichiesti: str, mezzo: str, materialeNecessario: str) -> None:
        self.__datiPaziente, self.__data = datiPaziente, data
        self.__oraInizio, self.__oraFine = oraInizio, oraFine
        self.__luogo, self.__tipoServizio = luogo, tipoServizio
        self.__postiTotali, self.__patenteRichiesta = postiTotali, patenteRichiesta
        self.__corsiRichiesti, self.__mezzo = corsiRichiesti, mezzo
        self.__materialeNecessario = materialeNecessario

    def __validaDati(self, data: date, oraInizio: time, oraFine: time,
                     postiTotali: int, prenotati: int) -> None:  # NF5
        if datetime.combine(data, oraInizio) < orologio.adesso():
            raise ValueError("La data e l'orario di inizio non possono essere gia' passati.")
        if oraFine <= oraInizio:
            raise ValueError("L'orario di fine deve essere successivo a quello di inizio.")
        if postiTotali <= 0:
            raise ValueError("Il numero di posti deve essere positivo.")
        if postiTotali < prenotati:
            raise ValueError("I posti non possono essere meno dei Volontari prenotati.")

    # ---------- CUDTurno: modifica ----------
    def modificaTurno(self, codice: str) -> dict:
        trovati = self.ricercaTurno({"codice": codice})
        if trovati and trovati[0].getStato() == StatoAttivita.PROGRAMMATO:
            return trovati[0].getDati()
        return {}  # turno non modificabile

    def inserisciModifiche(self, turno: Turno, datiPaziente: str, data: date, oraInizio: time,
                           oraFine: time, luogo: str, tipoServizio: str, postiTotali: int,
                           patenteRichiesta: str, corsiRichiesti: str, mezzo: str,
                           materialeNecessario: str) -> bool:
        prenotati = len(turno.getPrenotazioni())
        if postiTotali < prenotati:
            return False  # posti insufficienti
        self.__validaDati(data, oraInizio, oraFine, postiTotali, prenotati)
        turno.setDati(datiPaziente, data, oraInizio, oraFine, luogo, tipoServizio, postiTotali,
                      patenteRichiesta, corsiRichiesti, mezzo, materialeNecessario)
        turno.setPostiLiberi(postiTotali - prenotati)
        for prenotazione in turno.getPrenotazioni():
            prenotazione.notificaModifica()
        GestoreDati().salva(GestoreDati().carica())
        return True

    # ---------- CUDTurno: rimozione ----------
    def rimuoviTurno(self, codice: str) -> bool:
        trovati = self.ricercaTurno({"codice": codice})
        if not trovati or trovati[0].getStato() != StatoAttivita.PROGRAMMATO:
            return False  # turno non rimovibile
        turno = trovati[0]
        dati = GestoreDati().carica()
        for prenotazione in turno.getPrenotazioni():
            prenotazione.notificaEliminazione()  # e-mail + toglie dal Volontario
            dati["prenotazioni"].pop(prenotazione.getDati()["codice"], None)
        del dati["turni"][codice]
        GestoreDati().salva(dati)
        return True

    # ---------- RicercaTurno (incluso) ----------
    def ricercaTurno(self, criterio: dict) -> list[Turno]:
        criterio = self.__prelevaCriterio(criterio)
        trovati: list[Turno] = []
        for turno in GestoreDati().carica()["turni"].values():
            if turno.soddisfaCriterio(criterio):
                self.__aggiungiATrovati(turno, trovati)
        return trovati

    def __prelevaCriterio(self, criterio: dict) -> dict:
        return {chiave: valore for chiave, valore in criterio.items() if valore not in ("", None)}

    def soddisfaCriterio(self, criterio: dict) -> bool:
        """Chiavi ammesse: codice, data, tipoServizio (uguaglianza), stati (insieme di stati
        ammessi), inizioEntro (inizio <= istante), disponibile (programmato con posti liberi)."""
        for chiave, valore in criterio.items():
            if chiave == "stati":
                if self.__stato not in valore:
                    return False
            elif chiave == "inizioEntro":
                if self.getDataOraInizio() > valore:
                    return False
            elif chiave == "disponibile":
                if not (self.__stato == StatoAttivita.PROGRAMMATO and self.__postiLiberi > 0):
                    return False
            elif self.getDati().get(chiave) != valore:
                return False
        return True

    def __aggiungiATrovati(self, turno: Turno, trovati: list[Turno]) -> None:
        trovati.append(turno)

    # ---------- visualizzazioni ----------
    def visualizzaTurni(self) -> list[Turno]:
        return self.__ordinaPerData(list(GestoreDati().carica()["turni"].values()))

    def __ordinaPerData(self, turni: list[Turno]) -> list[Turno]:
        return sorted(turni, key=lambda t: t.getDataOraInizio(), reverse=True)

    def visualizzaTurniDisponibili(self) -> list[Turno]:
        return self.ricercaTurno({"disponibile": True})

    def filtraTurni(self, data: date | None, tipoServizio: str) -> list[Turno]:
        criterio = self.__prelevaCriterio({"data": data, "tipoServizio": tipoServizio})
        selezionati: list[Turno] = []
        for turno in self.visualizzaTurniDisponibili():
            if turno.soddisfaCriterio(criterio):
                self.__aggiungiASelezionati(turno, selezionati)
        return selezionati

    def __aggiungiASelezionati(self, turno: Turno, selezionati: list[Turno]) -> None:
        selezionati.append(turno)

    def visualizzaDettagliTurno(self, turno: Turno) -> dict:
        return turno.getDati()

    def visualizzaPrenotatiTurno(self, turno: Turno) -> list[Volontario]:
        ordinate = sorted(turno.getPrenotazioni(), key=lambda p: p.getDataPrenotazione())
        return [p.getVolontario() for p in ordinate]

    def verificaPatentePrenotati(self) -> bool:
        """True se almeno un prenotato ha una patente valida del tipo richiesto."""
        return any(p.getVolontario().possiedePatenteValida(self.__patenteRichiesta, self.__data)
                   for p in self.__prenotazioni)

    # ---------- attore Tempo ----------
    def impostaCriterio(self, casoDUso: str) -> dict:
        ora = orologio.adesso()
        if casoDUso == "AggiornaStatoTurno":
            return {
                "stati": {StatoAttivita.PROGRAMMATO, StatoAttivita.IN_CORSO},
                "inizioEntro": ora
            }
        if casoDUso == "InviaPromemoriaTurno":
            return {
                "stati": {StatoAttivita.PROGRAMMATO},
                "data": ora.date() + timedelta(days=1)
            }
        return {}

    def aggiornaStatoTurni(self) -> None:
        ora = orologio.adesso()
        for turno in self.ricercaTurno(self.impostaCriterio("AggiornaStatoTurno")):
            if turno.getStato() == StatoAttivita.PROGRAMMATO:
                turno.setStato(StatoAttivita.IN_CORSO)
            if turno.getDataOraFine() <= ora:
                turno.setStato(StatoAttivita.CONCLUSO)
                durata = (turno.getDataOraFine() - turno.getDataOraInizio()).total_seconds() / 3600
                for prenotazione in turno.getPrenotazioni():
                    prenotazione.aggiungiOreServizio(durata)
        GestoreDati().salva(GestoreDati().carica())

    def inviaPromemoriaTurni(self) -> None:
        for turno in self.ricercaTurno(self.impostaCriterio("InviaPromemoriaTurno")):
            for prenotazione in turno.getPrenotazioni():
                prenotazione.inviaPromemoria()
