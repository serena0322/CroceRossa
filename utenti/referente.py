"""Package Utenti: Referente (CreaAccountReferente)."""
from dati.gestore_dati import GestoreDati
from utenti.utente import FORMATO_EMAIL, FORMATO_PASSWORD, Utente

class Referente(Utente):
    def __init__(self): 
        super().__init__()
        self.__codiceAutorizzazione = ""
        self.__settoreGestito = ""

    def getDati(self) -> dict:
        return {
            "settoreGestito": self.__settoreGestito,
            **self._datiUtente()
        }

    def creaAccountReferente(self) -> None:
        """Messaggio d'avvio: lo fa partire VistaRegistrazioneReferente."""
        pass

    def inserisciInformazioni(self, settoreGestito: str, email: str, telefono: str,
                              comitato: str, password: str, codiceAutorizzazione: str) -> bool:
        if not self.__validaInformazioni(settoreGestito, email, telefono, comitato, password) \
           or not self.__verificaCodiceAutorizzazione(codiceAutorizzazione):
            return False
        self.__settoreGestito = settoreGestito
        self.__codiceAutorizzazione = codiceAutorizzazione
        self.setDatiUtente(email, telefono, comitato, password)
        dati = GestoreDati().carica()
        dati["utenti"][email] = self
        GestoreDati().salva(dati)
        return True

    def __validaInformazioni(self, settoreGestito: str, email: str, telefono: str,
                             comitato: str, password: str) -> bool:
        if not all([settoreGestito, telefono, comitato]):
            return False
        if not FORMATO_EMAIL.match(email) or not FORMATO_PASSWORD.match(password):
            return False
        return all(u.getEmail() != email for u in GestoreDati().carica()["utenti"].values())

    def __verificaCodiceAutorizzazione(self, codice: str) -> bool:
        return codice in GestoreDati().carica()["codici_autorizzazione"]
