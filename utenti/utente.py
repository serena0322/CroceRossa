"""Package Utenti: classe astratta Utente (Login, RecuperaCredenziali, ModificaDati, EliminaAccount)."""
import re
import secrets
import string
from abc import ABC, abstractmethod
from dati.gestore_dati import GestoreDati
from supporto import posta

FORMATO_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
FORMATO_PASSWORD = re.compile(r"^[A-Za-z0-9]{6,}$")  

class Utente(ABC):
    def __init__(self): 
        self.__comitato = ""
        self.__email = ""
        self.__password = ""
        self.__telefono = ""

    # get / set usati nei sequence
    def getEmail(self) -> str:
        return self.__email

    def getPassword(self) -> str:
        return self.__password

    def setPassword(self, password: str) -> None:
        self.__password = password

    def setDatiUtente(self, email: str, telefono: str, comitato: str, password: str) -> None:
        self.__email = email
        self.__telefono = telefono
        self.__comitato = comitato
        self.__password = password

    def _datiUtente(self) -> dict:  # usato dai getDati() delle sottoclassi
        return {
            "email": self.__email,
            "telefono": self.__telefono,
            "comitato": self.__comitato
        }

    @abstractmethod
    def getDati(self) -> dict: ...

    # Login
    def login(self) -> None:
        """Messaggio d'avvio del caso d'uso: nel codice lo fa partire VistaLogin."""
        pass

    def inserisciCredenziali(self, email: str, password: str):
    """Restituisce l'Utente autenticato oppure None (credenziali non valide)."""
    utente = self.__validaCredenziali(email, password)
    if utente is not None:
        self.__autentica(utente)
    return utente

    def __validaCredenziali(self, email: str, password: str):
        for utente in GestoreDati().carica()["utenti"].values():
            if utente.getEmail() == email and utente.getPassword() == password:
                return utente
        return None

    def __autentica(self, utente: "Utente") -> None:
        """L'apertura della home giusta la fa la vista (VistaLogin)."""
        pass

    # RecuperaCredenziali (estensione di Login)
    def recuperaCredenziali(self) -> None:
        """Messaggio d'avvio dell'estensione: lo fa partire VistaRecuperaCredenziali."""
        pass

    def inserisciEmail(self, email: str) -> bool:
        utente = self.__validaEmail(email)
        if utente is None:
            return False  # e-mail non registrata
        nuova = self.__generaPassword()
        utente.setPassword(nuova)
        dati = GestoreDati().carica()
        GestoreDati().salva(dati)
        utente.inviaEmail("Recupero password", f"La tua nuova password e': {nuova}")
        return True

    def __validaEmail(self, email: str):
        for utente in GestoreDati().carica()["utenti"].values():
            if utente.getEmail() == email:
                return utente
        return None

    def __generaPassword(self) -> str:
        alfabeto = string.ascii_letters + string.digits
        return "".join(secrets.choice(alfabeto) for _ in range(10))

    def inviaEmail(self, oggetto: str, testo: str) -> None:
        posta.invia(self.__email, oggetto, testo)

    # ModificaDati
    def modificaDati(self, email: str, telefono: str, password: str) -> bool:
        dati = GestoreDati().carica()
        altro = dati["utenti"].get(email)
        if (altro is not None and altro is not self) or not FORMATO_EMAIL.match(email) \
           or not FORMATO_PASSWORD.match(password):
            return False
        del dati["utenti"][self.__email]  # la chiave del dizionario e' l'e-mail
        self.__email, self.__telefono, self.__password = email, telefono, password
        dati["utenti"][email] = self
        GestoreDati().salva(dati)
        return True

    # EliminaAccount
    def eliminaAccount(self) -> None:
        dati = GestoreDati().carica()
        dati["utenti"].pop(self.__email, None)
        GestoreDati().salva(dati)
