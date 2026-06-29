from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from Volontario import Volontario
    from Turno import Turno

class GestioneTurniController:
    def __init__(self):
        pass

    def annullaPrenotazione(self, t: Turno) -> bool:
        try:
            from FirebaseConfig import db
            turno_ref = db.collection("turni").document(t.id)
            doc = turno_ref.get()
            if doc.exists:
                dati = doc.to_dict() or {}
                vids = dati.get("volontari_ids", [])
                vruoli = dati.get("volontari_ruoli", {})
                vids = [str(vid) for vid in vids if str(vid) not in [str(v.cod_fiscale) for v in t.volontari_assegnati]]
                for v in t.volontari_assegnati:
                    if str(v.cod_fiscale) in vruoli:
                        del vruoli[str(v.cod_fiscale)]
                turno_ref.update({
                    "volontari_ids": vids,
                    "volontari_ruoli": vruoli
                })
            print(f"[GestioneTurniController] annullaPrenotazione turno {t.id} completato.")
            return True
        except Exception as e:
            print(f"⚠️ Errore annullaPrenotazione in Firebase: {e}")
            return False

    def assegnaTurno(self, v: Volontario, t: Turno) -> None:
        self.prenotaTurno(t.id, v.cod_fiscale)

    def calcolaOrePeriodo(self, v: Volontario, inizio: str, fine: str) -> int:
        # Static calculation or count from database
        return v.monteOreTotale

    def creaTurno(self, t: Turno) -> bool:
        if not t.id:
            import uuid
            t.id = str(uuid.uuid4())[:8].upper()
        try:
            from FirebaseConfig import db
            db.collection("turni").document(t.id).set({
                "id": t.id,
                "data": t.data,
                "luogoDestinazione": t.luogoDestinazione,
                "luogoPrelevamento": t.luogoPrelevamento,
                "oraInizio": t.oraInizio,
                "oraFine": t.oraFine,
                "patenteRichiesta": t.patenteRichiesta,
                "paziente": t.paziente,
                "personeRichieste": t.personeRichieste,
                "persone_richieste": t.persone_richieste,
                "stato": t.stato,
                "tipoServizio": t.tipoServizio,
                "volontari_ids": [str(v.cod_fiscale) for v in t.volontari_assegnati]
            })
            print(f"[GestioneTurniController] creaTurno {t.id} salvato su Firebase.")
            return True
        except Exception as e:
            print(f"⚠️ Errore creaTurno in Firebase: {e}")
            return False

    def modificaTurno(self, idTurno: str, t: Turno) -> bool:
        return self.creaTurno(t)

    def prenotaTurno(self, idTurno: str, idVolontario: str, ruolo: str = "Soccorritore") -> bool:
        try:
            from FirebaseConfig import db
            turno_ref = db.collection("turni").document(idTurno)
            doc = turno_ref.get()
            if doc.exists:
                dati = doc.to_dict() or {}
                vids = dati.get("volontari_ids", [])
                vids = [str(vid) for vid in vids]
                vruoli = dati.get("volontari_ruoli", {})
                if idVolontario not in vids:
                    vids.append(idVolontario)
                vruoli[idVolontario] = ruolo
                turno_ref.update({
                    "volontari_ids": vids,
                    "volontari_ruoli": vruoli
                })
            else:
                # Se il turno non esiste in firebase, lo creiamo al volo
                turno_ref.set({
                    "id": idTurno,
                    "volontari_ids": [idVolontario],
                    "volontari_ruoli": {idVolontario: ruolo},
                    "stato": "Proposto"
                })
            print(f"[GestioneTurniController] prenotaTurno {idTurno} salvato su Firebase.")
            return True
        except Exception as e:
            print(f"⚠️ Errore prenotaTurno in Firebase: {e}")
            return False

    def validaDati(self, t: Turno | None = None) -> bool:
        return True

    def verificaCoperturaPatente(self, t: Turno) -> bool:
        return True

    def verificaTempoLimite(self, v: Volontario, t: Turno) -> bool:
        return True

    def visualizzaTurniDisponibili(self, s: str) -> List[Turno]:
        return []
