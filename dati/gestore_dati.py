"""Package Dati: GestoreDati, l'unico punto che legge e scrive il file pickle.
Tutto il sistema sta in UN SOLO dizionario salvato in dati/dati.pickle.
Un solo pickle.dump conserva i riferimenti condivisi: la Prenotazione che sta
nella lista del Turno e quella nella lista del Volontario restano lo stesso
oggetto anche dopo il caricamento.
"""
import os
import pickle

PERCORSO_FILE = os.path.join("dati", "dati.pickle")

_dati = None # dizionario condiviso da tutte le classi

def _struttura_vuota() -> dict:
    return {
        "utenti": {},                  # e-mail -> Volontario / Referente
        "patenti": {},                 # codice -> Patente
        "turni": {},                   # codice -> Turno
        "prenotazioni": {},            # codice -> Prenotazione
        "corsi": {},                   # codice -> Corso
        "iscrizioni": {},              # codice -> Iscrizione
        "codici_autorizzazione": set(),# NF4
        "ultima_esecuzione": {},       # attivita del Tempo gia eseguite oggi
    }

class GestoreDati:
    def __init__(self): 
        self.__percorsoFile = PERCORSO_FILE

    def carica(self) -> dict:
        global _dati
        if _dati is None:
            if os.path.isfile(self.__percorsoFile):
                with open(self.__percorsoFile, "rb") as file:
                    _dati = pickle.load(file)
            else:
                _dati = _struttura_vuota()
        return _dati

    def salva(self, dati: dict) -> None:
        global _dati
        cartella = os.path.dirname(self.__percorsoFile)
        if cartella:
            os.makedirs(cartella, exist_ok=True)
        temporaneo = self.__percorsoFile + ".tmp"
        with open(temporaneo, "wb") as file:
            pickle.dump(dati, file)
        os.replace(temporaneo, self.__percorsoFile)  # scrittura atomica
        _dati = dati
