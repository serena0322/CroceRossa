from __future__ import annotations
import os
import json
import pickle
from typing import Any


class GestoreDati:
    """
    Classe GestoreDati del package Dati (UML class Gestione, pkg Package di progettazione).
    
    Attributi UML:
        percorsoFile: str = "dati/dati.pickle"
        
    Metodi UML:
        create()
        carica(): dict
        salva(dict): void
    """

    def __init__(self, percorsoFile: str = "dati/dati.pickle"):
        self.percorsoFile = percorsoFile

    @classmethod
    def create(cls, percorsoFile: str = "dati/dati.pickle") -> GestoreDati:
        """Costruttore esplicito UML create()."""
        return cls(percorsoFile=percorsoFile)

    def _get_full_path(self) -> str:
        if os.path.isabs(self.percorsoFile):
            return self.percorsoFile
        base = os.path.dirname(os.path.abspath(__file__))
        full = os.path.join(base, self.percorsoFile)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        return full

    def carica(self) -> dict:
        """Carica il dizionario dei dati dal file pickle (o json di fallback)."""
        full_path = self._get_full_path()
        if not os.path.exists(full_path):
            # Se esiste un database.json principale nella root del progetto, caricalo come base
            json_fallback = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
            if os.path.exists(json_fallback):
                try:
                    with open(json_fallback, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.salva(data)
                    return data
                except Exception:
                    pass
            return {}

        try:
            with open(full_path, "rb") as f:
                return pickle.load(f)
        except Exception:
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}

    def salva(self, dati: dict) -> None:
        """Salva il dizionario serializzato su file."""
        full_path = self._get_full_path()
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            pickle.dump(dati, f)
