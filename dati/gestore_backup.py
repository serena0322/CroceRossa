"""Package Dati: GestoreBackup (caso d'uso Backup, attore Tempo, ogni giorno alle 23.30)."""
import os
import pickle
from dati.gestore_dati import GestoreDati
from supporto import orologio

PERCORSO_BACKUP = "backup"

class GestoreBackup:
    def __init__(self):  # create(): void
        self.__percorsoBackup = PERCORSO_BACKUP

    def effettuaBackup(self) -> None:
        dati = GestoreDati().carica()  # preleva i dati di tutte le categorie
        self.__copiaDatiBackup(dati)

    def __copiaDatiBackup(self, dati: dict) -> None:
        os.makedirs(self.__percorsoBackup, exist_ok=True)
        nome = f"dati_{orologio.adesso():%Y%m%d}.pickle"
        with open(os.path.join(self.__percorsoBackup, nome), "wb") as file:
            pickle.dump(dati, file)
