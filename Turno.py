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
        dispositivi_richiesti: List[str] = None
    ):
        self.id = str(id_turno) if id_turno is not None else id
        self.data = data
        self.luogoDestinazione = luogoDestinazione if luogoDestinazione else (luogo if luogo else "")
        self.luogoPrelevamento = luogoPrelevamento if luogoPrelevamento else (luogo if luogo else "")
        
        if fascia_oraria and " - " in fascia_oraria:
            parts = fascia_oraria.split(" - ")
            self.oraInizio = parts[0]
            self.oraFine = parts[1]
        else:
            self.oraInizio = oraInizio
            self.oraFine = oraFine

        self.patenteRichiesta = patenteRichiesta if patenteRichiesta else (corso_richiesto if corso_richiesto else "")
        self.paziente = paziente
        
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
    def luogo(self) -> str:
        return self.luogoDestinazione
        
    @luogo.setter
    def luogo(self, val: str):
        self.luogoDestinazione = val
        self.luogoPrelevamento = val

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
            "personeRichieste": self.personeRichieste,
            "persone_richieste": self.persone_richieste,
            "stato": self.stato,
            "tipoServizio": self.tipoServizio,
            "checklist": bool(self.checklist),
            "mezzo_targa": targa_val,
            "volontari_ids": [str(v.cod_fiscale) for v in self.volontari_assegnati],
            "volontari_ruoli": self.volontari_ruoli
        }, merge=True)
