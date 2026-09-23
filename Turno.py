from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from Volontario import Volontario
    from Mezzo import Mezzo

class Turno:
    def __init__(
        self,
        id: str = "",
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
        personeRichieste: int = 1,
        stato: str = "Proposto",
        tipoServizio: str = "",
        mezzo_targa: str = "",
        # Compatibility parameters:
        id_turno: int = None,
        fascia_oraria: str = None,
        luogo: str = None,
        corso_richiesto: str = None,
        checklist: bool = False,
        tempoExtra: str = "",
        dispositivi_richiesti: List[str] = None,
        **kwargs
    ):
        self.id = str(id_turno) if id_turno is not None else id
        self.data = data
        self.luogoDestinazione = luogoDestinazione if luogoDestinazione else (luogo if luogo else "")
        self.luogoPrelevamento = luogoPrelevamento if luogoPrelevamento else (luogo if luogo else "")
        
        # Gestione campi separati paziente
        self.paziente_nome = paziente_nome or kwargs.get("paziente_nome_cognome", "")
        self.paziente_cognome = paziente_cognome
        self.paziente_cf = paziente_cf or kwargs.get("codice_fiscale_paziente", "")
        self._paziente_raw = paziente
        if not self.paziente_nome and paziente and paziente != "Nessuno":
            self.paziente_nome = paziente
        
        if fascia_oraria and " - " in fascia_oraria:
            parts = fascia_oraria.split(" - ")
            self.oraInizio = parts[0]
            self.oraFine = parts[1]
        else:
            self.oraInizio = oraInizio
            self.oraFine = oraFine

        self.patenteRichiesta = patenteRichiesta if patenteRichiesta else (corso_richiesto if corso_richiesto else "")
        
        try:
            self.personeRichieste = int(personeRichieste)
        except (ValueError, TypeError):
            self.personeRichieste = 1
            
        self.stato = stato
        self.tipoServizio = tipoServizio
        
        # Compatibility attributes
        self.volontari_assegnati: List[Volontario] = []
        self.mezzo: Mezzo | None = None
        self.mezzo_targa: str = mezzo_targa
        self.checklist = checklist
        self.tempoExtra = tempoExtra
        self.dispositivi_richiesti = dispositivi_richiesti if dispositivi_richiesti is not None else []
        self.corso_richiesto = self.patenteRichiesta
        self.persone_richieste = {"volontario": self.personeRichieste}
        self.persone_prenotate = {}
        self.volontari_ruoli: dict[str, str] = {}

    @property
    def id_turno(self) -> int:
        try:
            return int(self.id)
        except ValueError:
            return 0
            
    @id_turno.setter
    def id_turno(self, val: int):
        self.id = str(val)

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

    def calcola_durata_ore(self) -> float:
        """Calcola la durata in ore del turno per la verifica dei limiti operativi."""
        from datetime import datetime
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

    def to_dict(self) -> dict:
        """Serializza il turno in formato dizionario."""
        return {
            "id": self.id,
            "data": self.data,
            "oraInizio": self.oraInizio,
            "oraFine": self.oraFine,
            "fascia_oraria": self.fascia_oraria,
            "luogoPrelevamento": self.luogoPrelevamento,
            "luogoDestinazione": self.luogoDestinazione,
            "luogo": self.luogo,
            "tipoServizio": self.tipoServizio,
            "paziente_nome": self.paziente_nome,
            "paziente_cognome": self.paziente_cognome,
            "paziente_cf": self.paziente_cf,
            "patenteRichiesta": self.patenteRichiesta,
            "personeRichieste": self.personeRichieste,
            "mezzo_targa": self.mezzo_targa,
            "stato": self.stato,
            "volontari_ids": [getattr(v, "cod_fiscale", str(v)) for v in self.volontari_assegnati],
            "volontari_ruoli": getattr(self, "volontari_ruoli", {})
        }

    @property
    def fascia_oraria(self) -> str:
        return f"{self.oraInizio} - {self.oraFine}"
        
    @fascia_oraria.setter
    def fascia_oraria(self, val: str):
        if " - " in val:
            parts = val.split(" - ")
            self.oraInizio = parts[0]
            self.oraFine = parts[1]

    def aggiornaDati(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def aggiungiVolontario(self, v: Volontario, ruolo: str = "") -> bool:
        if len(self.volontari_assegnati) < self.personeRichieste:
            if v not in self.volontari_assegnati:
                self.volontari_assegnati.append(v)
                self.persone_prenotate.setdefault(v.ruolo, []).append(v.cod_fiscale)
                if ruolo:
                    self.volontari_ruoli[str(v.cod_fiscale)] = ruolo
                if self not in v.turni_assegnati:
                    v.turni_assegnati.append(self)
                if len(self.volontari_assegnati) == self.personeRichieste:
                    self.stato = "Completo"
                return True
        return False

    def assegna_turno(self, utente: Volontario) -> bool:
        return self.aggiungiVolontario(utente)

    def getVolontariIscritti(self) -> List[Volontario]:
        return self.volontari_assegnati

    def isCompleto(self) -> bool:
        return len(self.volontari_assegnati) >= self.personeRichieste

    @staticmethod
    def getTurniDisponibili(servizio: str = "") -> List[Turno]:
        from GestioneTurniController import GestioneTurniController
        ctrl = GestioneTurniController()
        return ctrl.visualizzaTurniDisponibili()

    def rimuoviVolontario(self, v: Volontario) -> None:
        if v in self.volontari_assegnati:
            self.volontari_assegnati.remove(v)
            if v.cod_fiscale in self.persone_prenotate.get(v.ruolo, []):
                self.persone_prenotate[v.ruolo].remove(v.cod_fiscale)
            if str(v.cod_fiscale) in self.volontari_ruoli:
                del self.volontari_ruoli[str(v.cod_fiscale)]
            if self in v.turni_assegnati:
                v.turni_assegnati.remove(self)
            self.stato = "Aperto"

    def rimuovi_volontario(self, volontario: Volontario):
        self.rimuoviVolontario(volontario)

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

    def is_scoperto(self) -> bool:
        return not self.isCompleto()

    def richiede_corso(self) -> bool:
        return bool(self.patenteRichiesta)

    def dispositivi_mancanti(self, disponibili: List[str]) -> List[str]:
        return [d for d in self.dispositivi_richiesti if d not in disponibili]

    def aggiorna_firestore(self):
        from FirebaseConfig import db
        targa_val = self.mezzo_targa or (self.mezzo.targa if self.mezzo else "")
        db.collection("turni").document(self.id).set({
            "id": self.id,
            "data": self.data,
            "luogoDestinazione": self.luogoDestinazione,
            "luogoPrelevamento": self.luogoPrelevamento,
            "oraInizio": self.oraInizio,
            "oraFine": self.oraFine,
            "patenteRichiesta": self.patenteRichiesta,
            "paziente": self.paziente,
            "paziente_nome": self.paziente_nome,
            "paziente_cognome": self.paziente_cognome,
            "paziente_cf": self.paziente_cf,
            "personeRichieste": self.personeRichieste,
            "persone_richieste": self.persone_richieste,
            "stato": self.stato,
            "tipoServizio": self.tipoServizio,
            "checklist": bool(self.checklist),
            "mezzo_targa": targa_val,
            "volontari_ids": [str(v.cod_fiscale) for v in self.volontari_assegnati],
            "volontari_ruoli": self.volontari_ruoli
        }, merge=True)
