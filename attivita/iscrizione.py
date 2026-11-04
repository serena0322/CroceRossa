"""Package Attivita: Iscrizione (IscriviCorso, AnnullaIscrizioneCorso, attestazione)."""
from __future__ import annotations
import uuid
from datetime import date
from typing import TYPE_CHECKING
from attivita.partecipazione import Partecipazione
from attivita.stato_attivita import StatoAttivita
from dati.gestore_dati import GestoreDati
from supporto import orologio

if TYPE_CHECKING:
    from attivita.corso import Corso
    from utenti.volontario import Volontario

SUPERATO = "Superato"
NON_SUPERATO = "Non superato"

class Iscrizione(Partecipazione):
    def __init__(self):  # create()
        self.__codice = ""
        self.__corso: Corso | None = None
        self.__dataIscrizione = date.min
        self.__esito = ""
        self.__volontario: Volontario | None = None

    def getDati(self) -> dict:
        return {
            "codice": self.__codice,
            "dataIscrizione": self.__dataIscrizione,
            "esito": self.__esito,
            "superato": self.getSuperato()
    }

    def iscriviCorso(self, corso: Corso, volontario: Volontario) -> bool:
        datiCorso = corso.getDati()
        if datiCorso["stato"] != StatoAttivita.PROGRAMMATO or datiCorso["postiLiberi"] == 0 \
           or self.__verificaGiaIscritto(corso, volontario):
            return False
        self.__codice = uuid.uuid4().hex[:8]
        self.__dataIscrizione = orologio.adesso().date()
        self.__corso, self.__volontario = corso, volontario
        corso.aggiungiIscrizione(self)
        volontario.aggiungiPartecipazione(self)
        dati = GestoreDati().carica()
        dati["iscrizioni"][self.__codice] = self
        GestoreDati().salva(dati)
        return True

    def __verificaGiaIscritto(self, corso: Corso, volontario: Volontario) -> bool:
        return any(i.getVolontario() is volontario for i in corso.getIscrizioni())

    def getVolontario(self) -> Volontario:
        assert self.__volontario is not None, "Volontario non associato"
        return self.__volontario

    def getDataIscrizione(self) -> date:
        return self.__dataIscrizione

    def getDataInizioCorso(self) -> date:
        assert self.__corso is not None, "Corso non associato"
        return self.__corso.getDataInizio()

    def getDatiCorso(self) -> dict:
        assert self.__corso is not None, "Corso non associato"
        return self.__corso.getDati()

    def setSuperato(self) -> None:
        self.__esito = SUPERATO

    def setNonSuperato(self) -> None:
        self.__esito = NON_SUPERATO

    def getSuperato(self) -> bool:
        return self.__esito == SUPERATO

    #Partecipazione
    def getDatiVolontario(self) -> dict:
        assert self.__volontario is not None, "Volontario non associato"
        return self.__volontario.getDati()

    def liberaPosti(self) -> None:
        if self.__corso is not None:
            self.__corso.eliminaIscrizione(self)

    def notificaModifica(self) -> None:
        if self.__corso is not None and self.__volontario is not None:
            self.__volontario.inviaEmail("Corso modificato",
                                         f"Il corso {self.__corso.getDati()['nome']} e' stato modificato.")

    def notificaEliminazione(self) -> None:
        if self.__corso is not None and self.__volontario is not None:
            self.__volontario.inviaEmail("Corso eliminato",
                                         f"Il corso {self.__corso.getDati()['nome']} e' stato eliminato.")
            self.__volontario.eliminaPartecipazione(self)
