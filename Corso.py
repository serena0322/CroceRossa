from __future__ import annotations

from typing import List, Optional
from datetime import datetime, timedelta

from Referente import Referente
from Volontario import Volontario

class Corso:
    def __init__(
        self,
        id: str,
        nome: str,
        dataInizio: str,
        esito: bool,
        dataFine: str,
        checklist: List[dict],  # es. [{"item": "slide", "completato": True}]
        titolo: str,
        scadenza: str  # formato "YYYY-MM-DD"
    ):
        self.id = id
        self.nome = nome
        self.titolo = titolo
        self.dataInizio = dataInizio
        self.dataFine = dataFine
        self.esito = esito
        self.scadenza = scadenza
        self.checklist = checklist
        self.referente: Optional[Referente] = None
        self.partecipanti: List[Volontario] = []
        self.stato: List[str] = ["Proposto", "In corso" , "Concluso"]

    def aggiungi_partecipante(self, volontario: Volontario):
        if volontario not in self.partecipanti:
            self.partecipanti.append(volontario)
            print(f"{volontario.nome} aggiunto al corso {self.nome}.")
        else:
            print(f"{volontario.nome} è già iscritto al corso.")

    def rimuovi_partecipante(self, volontario: Volontario):
        if volontario in self.partecipanti:
            self.partecipanti.remove(volontario)
            print(f"{volontario.nome} rimosso dal corso {self.nome}.")

    def verifica_checklist(self) -> bool:
        return all(item.get("completato", False) for item in self.checklist)

    def sta_per_scadere(self) -> bool:
        try:
            scadenza_date = datetime.strptime(self.scadenza, "%Y-%m-%d")
            return scadenza_date - datetime.today() <= timedelta(days=30)
        except Exception as e:
            print(f"Errore nel parsing della data di scadenza: {e}")
            return False

    def imposta_referente(self, referente: Referente):
        self.referente = referente
        print(f"Referente {referente.nome} assegnato al corso {self.nome}.")
