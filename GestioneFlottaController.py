from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from Mezzo import Mezzo
    from Turno import Turno
    from Checklist import Checklist
    from Report import Report

class GestioneFlottaController:
    def __init__(self):
        pass

    def aggiungiMezzo(self, m: Mezzo) -> bool:
        try:
            from FirebaseConfig import db
            db.collection("mezzi").document(m.targa).set({
                "targa": m.targa,
                "tipo": m.tipo,
                "chilometraggioTotale": m.chilometraggioTotale,
                "stato": m.stato,
                "dataScadenzaAssicurazione": m.dataScadenzaAssicurazione
            })
            print(f"[GestioneFlottaController] aggiungiMezzo {m.targa} salvato su Firebase.")
            return True
        except Exception as e:
            print(f"⚠️ Errore aggiungiMezzo in Firebase: {e}")
            return False

    def assegnaMezzoATurno(self, m: Mezzo, t: Turno) -> bool:
        try:
            from FirebaseConfig import db
            db.collection("turni").document(t.id).update({
                "mezzo_targa": m.targa
            })
            return True
        except Exception as e:
            print(f"⚠️ Errore assegnaMezzoATurno in Firebase: {e}")
            return False

    def compilaChecklist(self, c: Checklist) -> bool:
        try:
            from FirebaseConfig import db
            db.collection("checklists").document(c.id).set({
                "id": c.id,
                "controlliMeccanici": c.controlliMeccanici,
                "dispositiviMediciRichiesti": c.dispositiviMediciRichiesti,
                "dispositiviPresenti": c.dispositiviPresenti
            })
            print(f"[GestioneFlottaController] compilaChecklist {c.id} salvata su Firebase.")
            return True
        except Exception as e:
            print(f"⚠️ Errore compilaChecklist in Firebase: {e}")
            return False

    def creaResoconto(self) -> bool:
        return True

    def richiediControlli(self, ruolo: str, c: Checklist | None = None) -> List[str]:
        if c is not None:
            if ruolo == "Autista A":
                return c.getControlliMeccaniciEmergenza()
            elif ruolo == "Soccorritore A":
                return c.getDispositiviSanitariAvanzati()
            elif ruolo == "Autista B":
                return c.getControlliMeccaniciBase()
            elif ruolo == "Soccorritore B":
                return c.getDispositiviSanitariBase()
        return []

    def salvaReport(self, r: Report) -> bool:
        try:
            from FirebaseConfig import db
            db.collection("reports").document(r.id).set({
                "id": r.id,
                "kmPercorsi": r.kmPercorsi,
                "noteIntervento": r.noteIntervento,
                "oreEffettive": r.oreEffettive
            })
            print(f"[GestioneFlottaController] salvaReport {r.id} salvato su Firebase.")
            return True
        except Exception as e:
            print(f"⚠️ Errore salvaReport in Firebase: {e}")
            return False

    def visualizzaStatoMezzi(self) -> List[Mezzo]:
        return []
