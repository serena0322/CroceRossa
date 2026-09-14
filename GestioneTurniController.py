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
        """Verifica la correttezza dei dati essenziali di un turno."""
        if not t:
            return False
        if not t.data or not str(t.data).strip():
            return False
        if not t.oraInizio or not t.oraFine:
            return False
        if getattr(t, "personeRichieste", 1) < 1:
            return False
        return True

    def verificaCoperturaPatente(self, v: Volontario, t: Turno) -> bool:
        """Verifica se il volontario possiede la patente o corso richiesto dal turno."""
        if not t or not getattr(t, "patenteRichiesta", None):
            return True
        req = str(t.patenteRichiesta).strip().upper()
        if not req or req in ["NESSUNA", "NON RICHIESTA", "TUTTI"]:
            return True
        if not v:
            return False
        patenti = [str(p).strip().upper() for p in getattr(v, "patenti", [])]
        qualifiche = [str(q).strip().upper() for q in getattr(v, "qualifiche", [])]
        return (req in patenti) or (req in qualifiche)

    def verificaTempoLimite(self, v: Volontario, t: Turno) -> bool:
        """Verifica che il volontario non abbia sovrapposizioni orarie con altri turni nello stesso giorno."""
        if not v or not t or not getattr(v, "turni_assegnati", None):
            return True
        for altro in v.turni_assegnati:
            if altro.id == t.id:
                continue
            if str(altro.data).strip() == str(t.data).strip():
                # Controllo sovrapposizione orari (formato HH:MM)
                try:
                    t_ini = t.oraInizio.strip()
                    t_fin = t.oraFine.strip()
                    a_ini = altro.oraInizio.strip()
                    a_fin = altro.oraFine.strip()
                    # Se intervalli si sovrappongono: max(t_ini, a_ini) < min(t_fin, a_fin)
                    if max(t_ini, a_ini) < min(t_fin, a_fin):
                        print(f"⚠️ Sovrapposizione oraria rilevata con turno {altro.id} ({altro.data} {altro.fascia_oraria})")
                        return False
                except Exception:
                    pass
        return True

    def visualizzaTurniDisponibili(self, sistema=None) -> List[Turno]:
        """Restituisce i turni aperti e con posti disponibili."""
        if sistema and getattr(sistema, "turni", None):
            return [
                t for t in sistema.turni
                if t.stato in ["Proposto", "Aperto"]
                and len(getattr(t, "volontari_assegnati", [])) < getattr(t, "personeRichieste", 1)
            ]
        try:
            from FirebaseConfig import db
            from Turno import Turno
            turni = []
            docs = db.collection("turni").get()
            for doc in docs:
                dati = doc.to_dict() or {}
                stato = str(dati.get("stato") or "Proposto")
                if stato in ["Proposto", "Aperto"]:
                    t = Turno(
                        id=doc.id,
                        data=str(dati.get("data") or ""),
                        luogoDestinazione=str(dati.get("luogoDestinazione") or dati.get("luogo") or ""),
                        luogoPrelevamento=str(dati.get("luogoPrelevamento") or dati.get("luogo") or ""),
                        oraInizio=str(dati.get("oraInizio") or ""),
                        oraFine=str(dati.get("oraFine") or ""),
                        patenteRichiesta=str(dati.get("patenteRichiesta") or dati.get("corso_richiesto") or ""),
                        paziente=str(dati.get("paziente") or ""),
                        personeRichieste=int(dati.get("personeRichieste", 1)),
                        stato=stato,
                        tipoServizio=str(dati.get("tipoServizio") or "")
                    )
                    turni.append(t)
            return turni
        except Exception as e:
            print(f"⚠️ Errore visualizzaTurniDisponibili: {e}")
            return []
