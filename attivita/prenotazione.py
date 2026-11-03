"""Package Attivita: Prenotazione (PrenotaTurno, AnnullaPrenotazione, promemoria e avvisi)."""
from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING
from attivita.partecipazione import Partecipazione
from attivita.stato_attivita import StatoAttivita
from dati.gestore_dati import GestoreDati
from supporto import orologio

if TYPE_CHECKING:
    from attivita.turno import Turno
    from utenti.volontario import Volontario

class Prenotazione(Partecipazione):
    def __init__(self):  # create(): void
        self.__codice = ""
        self.__dataPrenotazione = date.min
        self.__turno: Turno | None = None
        self.__volontario: Volontario | None = None

    def getDati(self) -> dict:
        return {
            "codice": self.__codice,
            "dataPrenotazione": self.__dataPrenotazione
        }

    # ---------- PrenotaTurno ----------
    def prenotaTurno(self, turno: Turno, volontario: Volontario) -> str:
        """Restituisce "" se la prenotazione e' registrata, altrimenti il messaggio di errore."""
        datiTurno = turno.getDati()
        if datiTurno["stato"] != StatoAttivita.PROGRAMMATO or datiTurno["postiLiberi"] == 0:
            return "Il turno non ha piu' posti liberi."
        if self.__verificaGiaPrenotato(turno, volontario):
            return "Sei gia' prenotato a questo turno."
        if self.__verificaSovrapposizione(turno, volontario):
            return "Sei gia' prenotato a un altro turno che si sovrappone a questo."
        if datiTurno["patenteRichiesta"] and datiTurno["postiLiberi"] == 1 \
           and not turno.verificaPatentePrenotati() \
           and not volontario.possiedePatenteValida(datiTurno["patenteRichiesta"], datiTurno["data"]):
            return "L'ultimo posto e' riservato a un Volontario con la patente richiesta."
        self.__codice = uuid.uuid4().hex[:8]
        self.__dataPrenotazione = orologio.adesso().date()
        self.__turno, self.__volontario = turno, volontario
        turno.aggiungiPrenotazione(self)
        #turno.setPostiLiberi(datiTurno["postiLiberi"] - 1)
        volontario.aggiungiPartecipazione(self)
        dati = GestoreDati().carica()
        dati["prenotazioni"][self.__codice] = self
        GestoreDati().salva(dati)
        return ""

    def __verificaGiaPrenotato(self, turno: Turno, volontario: Volontario) -> bool:
        return any(p.getVolontario() is volontario for p in turno.getPrenotazioni())

    def __verificaSovrapposizione(self, turno: Turno, volontario: Volontario) -> bool:
        inizio, fine = turno.getDataOraInizio(), turno.getDataOraFine()
        for prenotazione in volontario.visualizzaPrenotazioni():
            altro = prenotazione.getTurno()
            if altro.getDataOraInizio() < fine and inizio < altro.getDataOraFine():
                return True
        return False

    # ---------- get usati dagli altri casi d'uso ----------
    def getTurno(self) -> Turno:
        assert self.__turno is not None, "Turno non associato"
        return self.__turno

    def getVolontario(self) -> Volontario:
        assert self.__volontario is not None, "Volontario non associato"
        return self.__volontario

    def getDataPrenotazione(self) -> date:
        return self.__dataPrenotazione

    def getDataOraInizioTurno(self) -> datetime:
        assert self.__turno is not None, "Turno non associato"
        return self.__turno.getDataOraInizio()

    def getDatiTurno(self) -> dict:
        assert self.__turno is not None, "Turno non associato"
        return self.__turno.getDati()

    # ---------- Partecipazione ----------
    def getDatiVolontario(self) -> dict:
        assert self.__volontario is not None, "Volontario non associato"
        return self.__volontario.getDati()

    def liberaPosti(self) -> None:
        if self.__turno is not None:
            self.__turno.eliminaPrenotazione(self)

    def notificaModifica(self) -> None:
        if self.__turno is not None and self.__volontario is not None:
            d = self.__turno.getDati()
            self.__volontario.inviaEmail("Turno modificato",
                                         f"Il turno {d['codice']} del {d['data']:%d/%m/%Y} "
                                         f"e' stato modificato.")

    def notificaEliminazione(self) -> None:
        if self.__turno is not None and self.__volontario is not None:
            d = self.__turno.getDati()
            self.__volontario.inviaEmail("Turno eliminato",
                                         f"Il turno {d['codice']} del {d['data']:%d/%m/%Y} "
                                         f"e' stato eliminato.")
            self.__volontario.eliminaPartecipazione(self)

    # ---------- attore Tempo ----------
    def inviaPromemoria(self) -> None:
        if self.__turno is not None and self.__volontario is not None:
            d = self.__turno.getDati()
            self.__volontario.inviaEmail("Promemoria turno",
                                         f"Domani {d['data']:%d/%m/%Y} alle {d['oraInizio']:%H:%M} "
                                         f"hai il turno {d['codice']} a {d['luogo']}.")

    def aggiungiOreServizio(self, ore: float) -> None:
        if self.__volontario is not None:
            self.__volontario.aggiungiOreServizio(ore)
