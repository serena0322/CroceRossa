from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from Volontario import Volontario
    from Referente import Referente

class Corso:
    def __init__(
        self,
        id: str = "",
        dataFine: str = "",
        dataInizio: str = "",
        mesiValidita: int = 12,
        qualificaRilasciata: str = "",
        stato: str = "Programmato",
        titolo: str = "",
        # Compatibility arguments:
        nome: str = "",
        esito: bool = False,
        checklist: List[dict] = None,
        scadenza: str = ""
    ):
        self.id = id
        self.dataFine = dataFine
        self.dataInizio = dataInizio
        self.mesiValidita = mesiValidita
        self.qualificaRilasciata = qualificaRilasciata if qualificaRilasciata else (titolo if titolo else "")
        self.stato = stato
        self.titolo = titolo
        
        # Compatibility properties:
        self.nome = nome if nome else (titolo if titolo else "")
        self.esito = esito
        self.checklist = checklist if checklist is not None else []
        self.scadenza = scadenza
        self.referente: Referente | None = None
        self.partecipanti: List[Volontario] = []

    def aggiornaDati(self, c: Corso) -> None:
        self.id = c.id
        self.dataFine = c.dataFine
        self.dataInizio = c.dataInizio
        self.mesiValidita = c.mesiValidita
        self.qualificaRilasciata = c.qualificaRilasciata
        self.stato = c.stato
        self.titolo = c.titolo

    def aggiungiIscritto(self, dati: Volontario) -> bool:
        if dati not in self.partecipanti:
            self.partecipanti.append(dati)
            if self not in dati.formazione:
                dati.formazione.append(self)
            return True
        return False

    def aggiungi_partecipante(self, volontario: Volontario):
        self.aggiungiIscritto(volontario)

    def getIscritti(self) -> List[Volontario]:
        return self.partecipanti

    def getMonteOre(self) -> None:
        print(f"Monte Ore per il corso {self.titolo}: {self.mesiValidita * 10} ore")

    def rimuoviIscritto(self, volontario: Volontario) -> bool:
        if volontario in self.partecipanti:
            self.partecipanti.remove(volontario)
            if self in volontario.formazione:
                volontario.formazione.remove(self)
            return True
        return False

    def rimuovi_partecipante(self, volontario: Volontario):
        self.rimuoviIscritto(volontario)

    def verifica_checklist(self) -> bool:
        return all(item.get("completato", False) for item in self.checklist)

    def sta_per_scadere(self) -> bool:
        from datetime import datetime, timedelta
        try:
            if not self.scadenza:
                return False
            scadenza_date = datetime.strptime(self.scadenza, "%Y-%m-%d")
            return scadenza_date - datetime.today() <= timedelta(days=30)
        except Exception as e:
            print(f"Errore nel parsing della data di scadenza: {e}")
            return False

    def imposta_referente(self, referente: Referente):
        self.referente = referente
        print(f"Referente {referente.nome} assegnato al corso {self.nome}.")

    def aggiorna_firestore(self):
        from FirebaseConfig import db
        db.collection("corsi").document(self.id).set({
            "id": self.id,
            "dataFine": self.dataFine,
            "dataInizio": self.dataInizio,
            "mesiValidita": self.mesiValidita,
            "qualificaRilasciata": self.qualificaRilasciata,
            "stato": self.stato,
            "titolo": self.titolo
        }, merge=True)
