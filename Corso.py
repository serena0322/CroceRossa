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
        # Specifiche PDF UC 10:
        direttore: str = "",
        luogo: str = "",
        orari: str = "",
        requisitiIscrizione: str = "",
        maxPartecipanti: int = 20,
        # Compatibility arguments:
        nome: str = "",
        esito: bool = False,
        checklist: List[dict] = None,
        scadenza: str = "",
        **kwargs
    ):
        self.id = id
        self.dataFine = dataFine
        self.dataInizio = dataInizio
        self.mesiValidita = mesiValidita
        self.qualificaRilasciata = qualificaRilasciata if qualificaRilasciata else (titolo if titolo else "")
        self.stato = stato
        self.titolo = titolo
        self.direttore = direttore or kwargs.get("direttore_corso", "")
        self.luogo = luogo or kwargs.get("luogo_corso", "")
        self.orari = orari or kwargs.get("orari_corso", "")
        self.requisitiIscrizione = requisitiIscrizione or kwargs.get("requisiti_iscrizione", "")
        try:
            self.maxPartecipanti = int(maxPartecipanti or kwargs.get("numero_massimo_partecipanti", 20))
        except (ValueError, TypeError):
            self.maxPartecipanti = 20
        
        # Compatibility properties:
        self.nome = nome if nome else (titolo if titolo else "")
        self.esito = esito
        self.checklist = checklist if checklist is not None else []
        self.scadenza = scadenza
        self.referente: Referente | None = None
        self.partecipanti: List[Volontario] = []
        self.certificati_ids: List[str] = []

    def aggiornaDati(self, c: Corso) -> None:
        self.id = c.id
        self.dataFine = c.dataFine
        self.dataInizio = c.dataInizio
        self.mesiValidita = c.mesiValidita
        self.qualificaRilasciata = c.qualificaRilasciata
        self.stato = c.stato
        self.titolo = c.titolo
        self.direttore = c.direttore
        self.luogo = c.luogo
        self.orari = c.orari
        self.requisitiIscrizione = c.requisitiIscrizione
        self.maxPartecipanti = c.maxPartecipanti

    def is_completo(self) -> bool:
        return len(self.partecipanti) >= self.maxPartecipanti

    def isCompleto(self) -> bool:
        """Alias UML per is_completo."""
        return self.is_completo()

    def aggiungiIscritto(self, dati: Volontario) -> bool:
        if dati in self.partecipanti:
            return True
        # Verifica capienza massima partecipanti come da requisiti
        if len(self.partecipanti) >= self.maxPartecipanti:
            print(f"⚠️ Impossibile iscrivere {dati.nome}: corso '{self.titolo}' ha raggiunto la capienza massima ({self.maxPartecipanti} posti).")
            return False
            
        self.partecipanti.append(dati)
        if self not in dati.formazione:
            dati.formazione.append(self)
        return True

    def aggiungi_partecipante(self, volontario: Volontario):
        return self.aggiungiIscritto(volontario)

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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "dataFine": self.dataFine,
            "dataInizio": self.dataInizio,
            "mesiValidita": self.mesiValidita,
            "qualificaRilasciata": self.qualificaRilasciata,
            "stato": self.stato,
            "titolo": self.titolo,
            "nome": self.nome,
            "esito": self.esito,
            "checklist": self.checklist,
            "scadenza": self.scadenza,
            "direttore": getattr(self, "direttore", ""),
            "luogo": getattr(self, "luogo", ""),
            "orari": getattr(self, "orari", ""),
            "requisitiIscrizione": getattr(self, "requisitiIscrizione", ""),
            "maxPartecipanti": getattr(self, "maxPartecipanti", 20),
            "partecipanti_ids": [str(p.cod_fiscale) for p in self.partecipanti if hasattr(p, "cod_fiscale")],
            "certificati_ids": getattr(self, "certificati_ids", [])
        }

    def aggiorna_db(self):
        """Salva lo stato corrente del corso nel database locale JSON."""
        from Sistema import Sistema
        s = Sistema.get_instance()
        if s:
            s.salva_dati()

    def aggiorna_firestore(self):
        """Metodo di compatibilità: salva lo stato nel database locale JSON."""
        self.aggiorna_db()
