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

class Iscrizione(Partecipazione):
    def __init__(self):  # create(): void
        self.__codice = ""
        self.__corso: Corso | None = None
        self.__dataIscrizione = date.min
        self.__superato = False
        self.__volontario: Volontario | None = None

    def getDati(self) -> dict:
        return {
            "codice": self.__codice,
            "dataIscrizione": self.__dataIscrizione,
            "superato": self.__superato
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
        corso.setPostiLiberi(datiCorso["postiLiberi"] - 1)
        volontario.aggiungiPartecipazione(self)
        dati = GestoreDati().carica()
        dati["iscrizioni"][self.__codice] = self
        GestoreDati().salva(dati)
        return True

    def __verificaGiaIscritto(self, corso: Corso, volontario: Volontario) -> bool:
        return any(i.getVolontario() is volontario for i in corso.getIscrizioni())

    def getVolontario(self) -> Volontario:
        return self.__volontario

    def getDataIscrizione(self) -> date:
        return self.__dataIscrizione

    def getDataInizioCorso(self) -> date:
        return self.__corso.getDataInizio()

    def getDatiCorso(self) -> dict:
        return self.__corso.getDati()

    def getSuperato(self) -> bool:
        return self.__superato

    def setSuperato(self, superato: bool = True) -> None:
        self.__superato = superato

    def setNonSuperato(self) -> None:
        self.__superato = False

    # ---------- Partecipazione ----------
    def getDatiVolontario(self) -> dict:
        return self.__volontario.getDati()

    def liberaPosti(self) -> None:
        self.__corso.eliminaIscrizione(self)
        if self.__corso.getStato() == StatoAttivita.PROGRAMMATO:
            self.__corso.setPostiLiberi(self.__corso.getDati()["postiLiberi"] + 1)

    def notificaModifica(self) -> None:
        self.__volontario.inviaEmail("Corso modificato",
                                     f"Il corso {self.__corso.getDati()['nome']} e' stato modificato.")

    def notificaEliminazione(self) -> None:
        self.__volontario.inviaEmail("Corso eliminato",
                                     f"Il corso {self.__corso.getDati()['nome']} e' stato eliminato.")
        self.__volontario.eliminaPartecipazione(self)
