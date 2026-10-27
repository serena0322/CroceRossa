from __future__ import annotations
from typing import List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from Volontario import Volontario
    from Mezzo import Mezzo


class Turno:
    """
    Rappresenta un turno di servizio operativo della Croce Rossa Italiana.
    Classe conforme al diagramma delle classi UML (Package Attivita).

    Attributi UML:
        codice: str (String)
        corsiRichiesti: str (String)
        data: str (Data)
        datiPaziente: str (String)
        luogo: str (String)
        materialeNecessario: str (String)
        mezzo: str (String)
        oraFine: str (Ora)
        oraInizio: str (Ora)
        patenteRichiesta: str (String)
        postiLiberi: int (Integer)
        postiTotali: int (Integer)
        stato: str (StatoAttivita: PROGRAMMATO, IN_CORSO, CONCLUSO)
        tipoServizio: str (String)

    Metodi UML:
        getDati(), setDati(), setPostiLiberi(), isCompleto(), isModificabile(),
        aggiungiVolontario(), rimuoviVolontario(), getTurniDisponibili(),
        getDataOraInizio(), ordinaPerData(), soddisfaCriterio().
    """
    def __init__(
        self,
        codice: str = "",
        data: str = "",
        luogoDestinazione: str = "",
        luogoPrelevamento: str = "",
        oraInizio: str = "",
        oraFine: str = "",
        patenteRichiesta: str = "",
        paziente: str = "",
        paziente_nome: str = "",
        paziente_cognome: str = "",
        paziente_cf: str = "",
        personeRichieste: int | str = 1,
        postiTotali: int | None = None,
        postiLiberi: int | None = None,
        stato: str = "Aperto",
        tipoServizio: str = "",
        mezzo_targa: str = "",
        corsiRichiesti: str = "",
        materialeNecessario: str = "",
        # Compatibility parameters:
        id: str | None = None,
        id_turno: int | None = None,
        fascia_oraria: str | None = None,
        luogo: str | None = None,
        corso_richiesto: str | None = None,
        checklist: bool = False,
        tempoExtra: str = "",
        dispositivi_richiesti: List[str] | None = None,
        **kwargs
    ):
        if id_turno is not None:
            self.codice = str(id_turno)
        elif id is not None:
            self.codice = str(id)
        else:
            self.codice = str(codice or kwargs.get("id", ""))

        self.data = str(data)
        self.luogoDestinazione = luogoDestinazione if luogoDestinazione else (luogo if luogo else "")
        self.luogoPrelevamento = luogoPrelevamento if luogoPrelevamento else (luogo if luogo else "")

        # Gestione campi paziente
        self.paziente_nome = paziente_nome or kwargs.get("paziente_nome_cognome", "")
        self.paziente_cognome = paziente_cognome
        self.paziente_cf = paziente_cf or kwargs.get("codice_fiscale_paziente", "")
        self._paziente_raw = paziente
        if not self.paziente_nome and paziente and paziente != "Nessuno":
            self.paziente_nome = paziente

        if fascia_oraria and " - " in fascia_oraria:
            parts = fascia_oraria.split(" - ")
            self.oraInizio = parts[0].strip()
            self.oraFine = parts[1].strip()
        else:
            self.oraInizio = str(oraInizio).strip()
            self.oraFine = str(oraFine).strip()

        self.patenteRichiesta = patenteRichiesta if patenteRichiesta else (corso_richiesto if corso_richiesto else "")
        self.corsiRichiesti = corsiRichiesti or self.patenteRichiesta
        self.materialeNecessario = materialeNecessario or kwargs.get("materiale_necessario", "")

        tot = postiTotali if postiTotali is not None else personeRichieste
        try:
            self.postiTotali = int(tot)
        except (ValueError, TypeError):
            self.postiTotali = 1
        self.personeRichieste = self.postiTotali

        self.stato = stato
        self.tipoServizio = tipoServizio

        self.volontari_assegnati: List[Volontario] = []
        self.mezzo: Mezzo | None = None
        self.mezzo_targa: str = mezzo_targa
        self.checklist = checklist
        self.tempoExtra = tempoExtra
        self.dispositivi_richiesti = dispositivi_richiesti if dispositivi_richiesti is not None else []
        self.corso_richiesto = self.patenteRichiesta
        self.persone_richieste = {"volontario": self.postiTotali}
        self.persone_prenotate = {}
        self.volontari_ruoli: dict[str, str] = {}

        if postiLiberi is not None:
            self.postiLiberi = int(postiLiberi)
        else:
            self.postiLiberi = max(0, self.postiTotali - len(self.volontari_assegnati))

    @property
    def datiPaziente(self) -> str:
        return self.paziente

    @datiPaziente.setter
    def datiPaziente(self, val: str):
        self.paziente = val

    @property
    def paziente(self) -> str:
        nome_completo = f"{self.paziente_nome} {self.paziente_cognome}".strip()
        if nome_completo and self.paziente_cf:
            return f"{nome_completo} (CF: {self.paziente_cf})"
        return nome_completo or self.paziente_cf or self._paziente_raw or ""

    @paziente.setter
    def paziente(self, val: str):
        self._paziente_raw = val
        if " (CF: " in val:
            parts = val.split(" (CF: ")
            self.paziente_nome = parts[0].strip()
            self.paziente_cf = parts[1].replace(")", "").strip()
        elif val and val != "Nessuno":
            self.paziente_nome = val

    @property
    def luogo(self) -> str:
        if self.luogoPrelevamento and self.luogoDestinazione and self.luogoPrelevamento != self.luogoDestinazione:
            return f"{self.luogoPrelevamento} ➔ {self.luogoDestinazione}"
        return self.luogoDestinazione or self.luogoPrelevamento or ""

    @luogo.setter
    def luogo(self, val: str):
        if " ➔ " in val:
            parts = val.split(" ➔ ")
            self.luogoPrelevamento = parts[0].strip()
            self.luogoDestinazione = parts[1].strip()
        elif " -> " in val:
            parts = val.split(" -> ")
            self.luogoPrelevamento = parts[0].strip()
            self.luogoDestinazione = parts[1].strip()
        else:
            self.luogoDestinazione = val
            self.luogoPrelevamento = val

    @property
    def fascia_oraria(self) -> str:
        return f"{self.oraInizio} - {self.oraFine}"

    @fascia_oraria.setter
    def fascia_oraria(self, val: str):
        if " - " in val:
            parts = val.split(" - ")
            self.oraInizio = parts[0].strip()
            self.oraFine = parts[1].strip()

    def getDati(self) -> dict:
        """Restituisce i dati del turno conformi al diagramma di sequenza UML VisualizzaTurni / PrenotaTurno."""
        return {
            "codice": self.codice,
            "data": self.data,
            "oraInizio": self.oraInizio,
            "oraFine": self.oraFine,
            "luogo": self.luogo,
            "luogoPrelevamento": self.luogoPrelevamento,
            "luogoDestinazione": self.luogoDestinazione,
            "tipoServizio": self.tipoServizio,
            "patenteRichiesta": self.patenteRichiesta,
            "corsiRichiesti": self.corsiRichiesti,
            "materialeNecessario": self.materialeNecessario,
            "datiPaziente": self.datiPaziente,
            "postiTotali": self.postiTotali,
            "postiLiberi": self.postiLiberi,
            "stato": self.stato,
            "mezzo": self.mezzo_targa or (self.mezzo.targa if self.mezzo else "")
        }

    def setDati(self, **kwargs) -> None:
        """Aggiorna le informazioni del turno (UML CUDTurno)."""
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        if "postiTotali" in kwargs:
            self.personeRichieste = self.postiTotali
            self.postiLiberi = max(0, self.postiTotali - len(self.volontari_assegnati))

    def setPostiLiberi(self, val: int | None = None) -> None:
        """Imposta il numero di posti liberi rimasti per il turno (UML PrenotaTurno / CUDTurno)."""
        if val is not None:
            self.postiLiberi = max(0, int(val))
        else:
            self.postiLiberi = max(0, self.postiTotali - len(self.volontari_assegnati))

    def getDataOraInizio(self) -> datetime | None:
        """Restituisce la data e l'ora di inizio come oggetto datetime (UML VisualizzaPrenotazioni)."""
        try:
            return datetime.strptime(f"{self.data} {self.oraInizio}", "%Y-%m-%d %H:%M")
        except Exception:
            return None

    def isAnnullabile(self, delta_ore: float = 24.0) -> bool:
        """
        Regola Tesina UML: L'annullamento della prenotazione è consentito fino a 24 ore prima dell'inizio del turno.
        """
        dt_inizio = self.getDataOraInizio()
        if not dt_inizio:
            return True
        diff_ore = (dt_inizio - datetime.now()).total_seconds() / 3600.0
        return diff_ore >= delta_ore

    def soddisfaCriterio(self, criterio: str = "") -> bool:
        """Verifica se il turno soddisfa un criterio di ricerca (UML RicercaTurno)."""
        if not criterio:
            return True
        crit = criterio.lower()
        return (
            crit in self.codice.lower()
            or crit in self.tipoServizio.lower()
            or crit in self.luogo.lower()
            or crit in self.data.lower()
            or crit in self.stato.lower()
        )

    @staticmethod
    def ordinaPerData(turni: List[Turno]) -> List[Turno]:
        """Ordina i turni dal più recente al meno recente (UML VisualizzaTurni)."""
        return sorted(turni, key=lambda t: f"{getattr(t, 'data', '')} {getattr(t, 'oraInizio', '')}", reverse=True)

    def calcola_durata_ore(self) -> float:
        """Calcola la durata in ore del turno per la verifica dei limiti operativi."""
        try:
            fmt = "%H:%M"
            t_ini = datetime.strptime(self.oraInizio.strip(), fmt)
            t_fin = datetime.strptime(self.oraFine.strip(), fmt)
            diff = (t_fin - t_ini).total_seconds() / 3600.0
            if diff < 0:
                diff += 24.0
            return max(0.5, round(diff, 2))
        except Exception:
            return 4.0

    def aggiornaDati(self, **kwargs) -> None:
        self.setDati(**kwargs)

    def aggiungiVolontario(self, v: Volontario, ruolo: str = "") -> bool:
        """Aggiunge un volontario al turno se ci sono posti disponibili (UML)."""
        if len(self.volontari_assegnati) < self.postiTotali:
            if v not in self.volontari_assegnati:
                self.volontari_assegnati.append(v)
                self.postiLiberi = max(0, self.postiTotali - len(self.volontari_assegnati))
                self.persone_prenotate.setdefault(getattr(v, "ruolo", "volontario"), []).append(v.cod_fiscale)
                if ruolo:
                    self.volontari_ruoli[v.cod_fiscale] = ruolo
                if self not in getattr(v, "turni_assegnati", []):
                    v.turni_assegnati.append(self)
                if len(self.volontari_assegnati) >= self.postiTotali:
                    self.stato = "Completo"
                return True
        return False

    def getVolontariIscritti(self) -> List[Volontario]:
        """Restituisce la lista dei volontari assegnati al turno (UML)."""
        return self.volontari_assegnati

    def isCompleto(self) -> bool:
        """Verifica se il turno ha raggiunto il numero di persone richieste (UML)."""
        return len(self.volontari_assegnati) >= self.postiTotali

    @staticmethod
    def getTurniDisponibili(servizio: str = "") -> List[Turno]:
        """Restituisce i turni disponibili alla prenotazione (UML)."""
        from GestioneTurniController import GestioneTurniController
        ctrl = GestioneTurniController()
        return ctrl.visualizzaTurniDisponibili()

    def rimuoviVolontario(self, v: Volontario) -> None:
        """Rimuove un volontario dal turno (UML)."""
        if v in self.volontari_assegnati:
            self.volontari_assegnati.remove(v)
            self.postiLiberi = max(0, self.postiTotali - len(self.volontari_assegnati))
            if v.cod_fiscale in self.persone_prenotate.get(getattr(v, "ruolo", "volontario"), []):
                self.persone_prenotate[getattr(v, "ruolo", "volontario")].remove(v.cod_fiscale)
            if v.cod_fiscale in self.volontari_ruoli:
                del self.volontari_ruoli[v.cod_fiscale]
            if self in getattr(v, "turni_assegnati", []):
                v.turni_assegnati.remove(self)
            self.stato = "Aperto"

    def assegna_mezzo(self, mezzo: Mezzo):
        self.mezzo = mezzo
        if mezzo:
            self.mezzo_targa = getattr(mezzo, "targa", "")
            if self not in mezzo.turni_assegnati:
                mezzo.assegna_a_turno(self)
        else:
            self.mezzo_targa = ""

    def rimuovi_mezzo(self):
        if self.mezzo:
            if self in self.mezzo.turni_assegnati:
                self.mezzo.turni_assegnati.remove(self)
            if len(self.mezzo.turni_assegnati) == 0:
                self.mezzo.libera_mezzo()
        self.mezzo = None
        self.mezzo_targa = ""

    def completa_checklist(self):
        self.checklist = True

    def cambia_stato(self, nuovo_stato: str):
        self.stato = nuovo_stato

    def isModificabile(self) -> bool:
        """Un turno è modificabile dal referente esclusivamente se si trova in stato 'Aperto' o 'PROGRAMMATO' (UML)."""
        st = str(self.stato).strip().lower()
        return st in ["aperto", "programmato"]

    def richiede_corso(self) -> bool:
        return bool(self.patenteRichiesta)

    def dispositivi_mancanti(self, disponibili: List[str]) -> List[str]:
        return [d for d in self.dispositivi_richiesti if d not in disponibili]

    def to_dict(self) -> dict:
        targa_val = self.mezzo_targa or (self.mezzo.targa if self.mezzo else "")
        return {
            "id": self.codice,
            "codice": self.codice,
            "data": self.data,
            "luogoDestinazione": self.luogoDestinazione,
            "luogoPrelevamento": self.luogoPrelevamento,
            "luogo": self.luogo,
            "oraInizio": self.oraInizio,
            "oraFine": self.oraFine,
            "patenteRichiesta": self.patenteRichiesta,
            "corsiRichiesti": self.corsiRichiesti,
            "materialeNecessario": self.materialeNecessario,
            "datiPaziente": self.datiPaziente,
            "paziente": self.paziente,
            "paziente_nome": self.paziente_nome,
            "paziente_cognome": self.paziente_cognome,
            "paziente_cf": self.paziente_cf,
            "personeRichieste": self.postiTotali,
            "postiTotali": self.postiTotali,
            "postiLiberi": self.postiLiberi,
            "persone_richieste": self.persone_richieste,
            "stato": self.stato,
            "tipoServizio": self.tipoServizio,
            "checklist": self.checklist,
            "mezzo_targa": targa_val,
            "volontari_ids": [v.cod_fiscale for v in self.volontari_assegnati if hasattr(v, "cod_fiscale")],
            "volontari_ruoli": self.volontari_ruoli
        }

    def aggiorna_db(self):
        from Sistema import Sistema
        s = Sistema.get_instance()
        if s:
            s.salva_dati()

    def aggiorna_firestore(self):
        self.aggiorna_db()
