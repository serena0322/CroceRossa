"""Package Utenti: Volontario (CreaAccountVolontario, VisualizzaCarriera, patenti, prenotazioni, iscrizioni)."""
from __future__ import annotations
import re
from datetime import date, timedelta
from typing import TYPE_CHECKING
from attivita.stato_attivita import StatoAttivita
from dati.gestore_dati import GestoreDati
from supporto import orologio
from utenti.utente import FORMATO_EMAIL, FORMATO_PASSWORD, Utente

if TYPE_CHECKING:
    from attivita.iscrizione import Iscrizione
    from attivita.partecipazione import Partecipazione
    from attivita.prenotazione import Prenotazione
    from utenti.patente import Patente

FORMATO_CODICE_FISCALE = re.compile(r"^[A-Z0-9]{16}$")

class Volontario(Utente):
    def __init__(self):
        super().__init__()
        self.__codiceFiscale = ""
        self.__cognome = ""
        self.__nome = ""
        self.__oreServizio = 0.0
        self.__patenti: list[Patente] = []
        self.__prenotazioni: list[Prenotazione] = []
        self.__iscrizioni: list[Iscrizione] = []

    def getDati(self) -> dict:
        return {
            "nome": self.__nome,
            "cognome": self.__cognome,
            "codiceFiscale": self.__codiceFiscale,
            "oreServizio": self.__oreServizio,
            **self._datiUtente()
        }

    # ---------- CreaAccountVolontario ----------
    def creaAccountVolontario(self) -> None:
        """Messaggio d'avvio: lo fa partire VistaRegistrazioneVolontario."""
        pass

    def inserisciInformazioni(self, nome: str, cognome: str, codiceFiscale: str, email: str,
                              telefono: str, comitato: str, password: str) -> bool:
        if not self.__validaInformazioni(nome, cognome, codiceFiscale, email,
                                         telefono, comitato, password):
            return False
        self.__nome, self.__cognome = nome, cognome
        self.__codiceFiscale = codiceFiscale.upper()
        self.setDatiUtente(email, telefono, comitato, password)
        dati = GestoreDati().carica()
        dati["utenti"][email] = self
        GestoreDati().salva(dati)
        return True

    def __validaInformazioni(self, nome: str, cognome: str, codiceFiscale: str, email: str,
                             telefono: str, comitato: str, password: str) -> bool:
        if not all([nome, cognome, telefono, comitato]):
            return False
        if not FORMATO_CODICE_FISCALE.match(codiceFiscale.upper()):
            return False
        if not FORMATO_EMAIL.match(email) or not FORMATO_PASSWORD.match(password):
            return False
        for utente in GestoreDati().carica()["utenti"].values():  # NF3
            if utente.getEmail() == email:
                return False
        return True

    # ---------- ore di servizio, patenti, partecipazioni ----------
    def aggiungiOreServizio(self, ore: float) -> None:
        self.__oreServizio += ore

    def aggiungiPatente(self, patente: Patente) -> None:
        self.__patenti.append(patente)

    def eliminaPatente(self, patente: Patente) -> None:
        self.__patenti.remove(patente)

    def visualizzaPatenti(self) -> list[Patente]:
        return list(self.__patenti)

    def possiedePatenteValida(self, tipo: str, data: date) -> bool:
        return any(p.getDati()["tipo"] == tipo and p.verificaValidita(data)
                   for p in self.__patenti)

    def aggiungiPartecipazione(self, partecipazione: Partecipazione) -> None:
        from attivita.prenotazione import Prenotazione
        if isinstance(partecipazione, Prenotazione):
            self.__prenotazioni.append(partecipazione)
        else:
            self.__iscrizioni.append(partecipazione)

    def eliminaPartecipazione(self, partecipazione: Partecipazione) -> None:
        if partecipazione in self.__prenotazioni:
            self.__prenotazioni.remove(partecipazione)
        elif partecipazione in self.__iscrizioni:
            self.__iscrizioni.remove(partecipazione)

    # ---------- VisualizzaPrenotazioni / AnnullaPrenotazione ----------
    def visualizzaPrenotazioni(self) -> list[Prenotazione]:
        """Prenotazioni presenti = a turni non conclusi."""
        return [p for p in self.__prenotazioni
                if p.getDatiTurno()["stato"] != StatoAttivita.CONCLUSO]

    def annullaPrenotazione(self, prenotazione: Prenotazione) -> bool:
        if prenotazione.getDataOraInizioTurno() - orologio.adesso() <= timedelta(hours=24):
            return False  # annullamento non consentito
        prenotazione.liberaPosti()
        self.eliminaPartecipazione(prenotazione)
        dati = GestoreDati().carica()
        dati["prenotazioni"].pop(prenotazione.getDati()["codice"], None)
        GestoreDati().salva(dati)
        return True

    # ---------- VisualizzaIscrizioni / AnnullaIscrizioneCorso ----------
    def visualizzaIscrizioni(self) -> list[Iscrizione]:
        return [i for i in self.__iscrizioni
                if i.getDatiCorso()["stato"] != StatoAttivita.CONCLUSO]

    def annullaIscrizione(self, iscrizione: Iscrizione) -> bool:
        if iscrizione.getDataInizioCorso() - orologio.adesso().date() <= timedelta(days=2):
            return False
        iscrizione.liberaPosti()
        self.eliminaPartecipazione(iscrizione)
        dati = GestoreDati().carica()
        dati["iscrizioni"].pop(iscrizione.getDati()["codice"], None)
        GestoreDati().salva(dati)
        return True

    # ---------- VisualizzaCarriera ----------
    def visualizzaCarriera(self) -> dict:
        corsi = [i.getDatiCorso()["nome"] for i in self.__iscrizioni if i.getSuperato()]
        turni = [(p.getDatiTurno()["data"], p.getDatiTurno()["codice"])
                 for p in self.__prenotazioni
                 if p.getDatiTurno()["stato"] == StatoAttivita.CONCLUSO]
        return {
            "corsiSuperati": corsi,
            "turniSvolti": turni,
            "oreServizio": self.__oreServizio
        }

    # ---------- EliminaAccount (ridefinito) ----------
    def eliminaAccount(self) -> None:
        dati = GestoreDati().carica()
        for prenotazione in list(self.__prenotazioni):
            prenotazione.liberaPosti()  # i posti tornano liberi solo se il turno e' programmato
            dati["prenotazioni"].pop(prenotazione.getDati()["codice"], None)
        for iscrizione in list(self.__iscrizioni):
            iscrizione.liberaPosti()
            dati["iscrizioni"].pop(iscrizione.getDati()["codice"], None)
        for patente in self.__patenti:
            dati["patenti"].pop(patente.getDati()["codice"], None)
        self.__prenotazioni, self.__iscrizioni, self.__patenti = [], [], []
        super().eliminaAccount()  # toglie l'utente e salva
