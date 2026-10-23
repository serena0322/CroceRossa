from __future__ import annotations
from typing import List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from Volontario import Volontario
    from Referente import Referente


class Corso:
    """
    Rappresenta un corso di formazione della Croce Rossa Italiana.
    Classe conforme al diagramma delle classi UML (Package Attivita).

    Attributi UML:
        codice: str (String)
        dataFine: str (Data)
        dataInizio: str (Data)
        descrizione: str (String)
        direttoreCorso: str (String)
        luogo: str (String)
        nome: str (String)
        orario: str (String)
        postiLiberi: int (Integer)
        postiTotali: int (Integer)
        stato: str (StatoAttivita: PROGRAMMATO, IN_CORSO, CONCLUSO)
        tipoCorso: str (String)

    Metodi UML:
        getDati(), setDati(), setPostiLiberi(), isCompleto(),
        aggiungiPartecipante(), rimuoviPartecipante(), ordinaPerData().
    """
    def __init__(
        self,
        codice: str = "",
        dataFine: str = "",
        dataInizio: str = "",
        descrizione: str = "",
        direttoreCorso: str = "",
        luogo: str = "",
        nome: str = "",
        orario: str = "",
        postiLiberi: int | None = None,
        postiTotali: int = 20,
        stato: str = "PROGRAMMATO",
        tipoCorso: str = "",
        # Compatibility parameters:
        id: str = "",
        titolo: str = "",
        direttore: str = "",
        orari: str = "",
        maxPartecipanti: int | None = None,
        mesiValidita: int = 12,
        qualificaRilasciata: str = "",
        requisitiIscrizione: str = "",
        esito: bool = False,
        checklist: List[dict] | None = None,
        scadenza: str = "",
        **kwargs
    ):
        self.codice = str(codice or id or "").strip()
        self.id = self.codice  # Riferimento diretto per compatibilità
        self.dataFine = str(dataFine).strip()
        self.dataInizio = str(dataInizio).strip()
        self.descrizione = str(descrizione or kwargs.get("descrizione_corso", "")).strip()
        self.direttoreCorso = str(direttoreCorso or direttore or kwargs.get("direttore_corso", "")).strip()
        self.direttore = self.direttoreCorso
        self.luogo = str(luogo or kwargs.get("luogo_corso", "")).strip()
        self.nome = str(nome or titolo or "").strip()
        self.titolo = self.nome
        self.orario = str(orario or orari or kwargs.get("orari_corso", "")).strip()
        self.orari = self.orario

        totali = maxPartecipanti if maxPartecipanti is not None else postiTotali
        try:
            self.postiTotali = int(totali)
        except (ValueError, TypeError):
            self.postiTotali = 20
        self.maxPartecipanti = self.postiTotali

        self.stato = str(stato).strip()
        self.tipoCorso = str(tipoCorso or qualificaRilasciata or "").strip()
        self.qualificaRilasciata = self.tipoCorso

        self.mesiValidita = mesiValidita
        self.requisitiIscrizione = str(requisitiIscrizione or kwargs.get("requisiti_iscrizione", "")).strip()
        self.esito = esito
        self.checklist = checklist if checklist is not None else []
        self.scadenza = scadenza
        self.referente: Referente | None = None
        self.partecipanti: List[Volontario] = []
        self.certificati_ids: List[str] = []

        if postiLiberi is not None:
            self.postiLiberi = int(postiLiberi)
        else:
            self.postiLiberi = max(0, self.postiTotali - len(self.partecipanti))

    def getDati(self) -> dict:
        """Restituisce i dati del corso conformi al diagramma di sequenza UML VisualizzaCorsi."""
        return {
            "codice": self.codice,
            "nome": self.nome,
            "dataInizio": self.dataInizio,
            "dataFine": self.dataFine,
            "orario": self.orario,
            "luogo": self.luogo,
            "direttoreCorso": self.direttoreCorso,
            "descrizione": self.descrizione,
            "tipoCorso": self.tipoCorso,
            "postiTotali": self.postiTotali,
            "postiLiberi": self.postiLiberi,
            "stato": self.stato
        }

    def setDati(self, **kwargs) -> None:
        """Aggiorna le informazioni del corso (UML)."""
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        if "nome" in kwargs:
            self.titolo = self.nome
        if "postiTotali" in kwargs:
            self.maxPartecipanti = self.postiTotali
            self.postiLiberi = max(0, self.postiTotali - len(self.partecipanti))

    def setPostiLiberi(self, val: int) -> None:
        """Imposta il numero di posti liberi rimasti per il corso (UML)."""
        self.postiLiberi = max(0, int(val))

    def isCompleto(self) -> bool:
        """Verifica se il corso ha raggiunto la capienza massima (UML)."""
        return len(self.partecipanti) >= self.postiTotali

    def aggiungiPartecipante(self, dati: Volontario) -> bool:
        """Iscrive un volontario al corso (UML)."""
        if dati in self.partecipanti:
            return True
        if self.isCompleto():
            print(f"[Corso/Avviso] Impossibile iscrivere {dati.nome}: corso '{self.nome}' ha raggiunto la capienza massima ({self.postiTotali} posti).")
            return False
        self.partecipanti.append(dati)
        self.postiLiberi = max(0, self.postiTotali - len(self.partecipanti))
        if self not in getattr(dati, "formazione", []):
            dati.formazione.append(self)
        return True

    # Alias per compatibilità
    def aggiungiIscritto(self, dati: Volontario) -> bool:
        return self.aggiungiPartecipante(dati)

    def rimuoviPartecipante(self, volontario: Volontario) -> bool:
        """Rimuove un volontario dal corso (UML)."""
        if volontario in self.partecipanti:
            self.partecipanti.remove(volontario)
            self.postiLiberi = max(0, self.postiTotali - len(self.partecipanti))
            if self in getattr(volontario, "formazione", []):
                volontario.formazione.remove(self)
            return True
        return False

    def rimuoviIscritto(self, volontario: Volontario) -> bool:
        return self.rimuoviPartecipante(volontario)

    def getIscritti(self) -> List[Volontario]:
        """Restituisce la lista degli iscritti al corso (UML)."""
        return self.partecipanti

    def getMonteOre(self) -> None:
        """Stampa il monte ore previsto per il corso (UML)."""
        print(f"Monte Ore per il corso {self.nome}: {self.mesiValidita * 10} ore")

    @staticmethod
    def ordinaPerData(corsi: List[Corso]) -> List[Corso]:
        """Ordina i corsi dal più recente al meno recente (UML VisualizzaCorsi)."""
        return sorted(corsi, key=lambda c: str(getattr(c, "dataInizio", "")), reverse=True)

    def verifica_checklist(self) -> bool:
        return all(item.get("completato", False) for item in self.checklist)

    def sta_per_scadere(self) -> bool:
        try:
            if not self.scadenza:
                return False
            scadenza_date = datetime.strptime(self.scadenza, "%Y-%m-%d")
            return (scadenza_date - datetime.today()).days <= 30
        except Exception as e:
            print(f"Errore nel parsing della data di scadenza: {e}")
            return False

    def imposta_referente(self, referente: Referente):
        self.referente = referente
        print(f"Referente {referente.nome} assegnato al corso {self.nome}.")

    def to_dict(self) -> dict:
        return {
            "codice": self.codice,
            "id": self.codice,
            "nome": self.nome,
            "titolo": self.titolo,
            "dataInizio": self.dataInizio,
            "dataFine": self.dataFine,
            "descrizione": self.descrizione,
            "direttoreCorso": self.direttoreCorso,
            "luogo": self.luogo,
            "orario": self.orario,
            "postiTotali": self.postiTotali,
            "postiLiberi": self.postiLiberi,
            "maxPartecipanti": self.postiTotali,
            "stato": self.stato,
            "tipoCorso": self.tipoCorso,
            "qualificaRilasciata": self.qualificaRilasciata,
            "mesiValidita": self.mesiValidita,
            "esito": self.esito,
            "checklist": self.checklist,
            "scadenza": self.scadenza,
            "requisitiIscrizione": self.requisitiIscrizione,
            "partecipanti_ids": [str(p.cod_fiscale) for p in self.partecipanti if hasattr(p, "cod_fiscale")],
            "certificati_ids": getattr(self, "certificati_ids", [])
        }

    def aggiorna_db(self):
        from Sistema import Sistema
        s = Sistema.get_instance()
        if s:
            s.salva_dati()

    def aggiorna_firestore(self):
        self.aggiorna_db()
