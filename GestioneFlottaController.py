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

    def _verifica_permessi_referente(self, utente) -> bool:
        if utente is None:
            return True  # Fallback per chiamate interne o test
        ruolo = str(getattr(utente, "ruolo", "")).strip().lower()
        if ruolo == "referente" or hasattr(utente, "area_gestita"):
            return True
        print("❌ Operazione negata: solo gli utenti con ruolo 'Referente' possono gestire la flotta.")
        return False

    def aggiungiMezzo(self, m: Mezzo, utente=None) -> bool:
        if not self._verifica_permessi_referente(utente):
            return False
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

    def assegnaMezzoATurno(self, m: Mezzo | None, t: Turno, utente=None) -> bool:
        if not self._verifica_permessi_referente(utente):
            return False
        try:
            from FirebaseConfig import db
            if m:
                t.assegna_mezzo(m)
                db.collection("turni").document(t.id).set({
                    "mezzo_targa": m.targa
                }, merge=True)
                db.collection("mezzi").document(m.targa).set({
                    "stato": "Assegnato",
                    "disponibile": False
                }, merge=True)
                print(f"[GestioneFlottaController] Mezzo {m.targa} assegnato al turno {t.id}.")
            else:
                old_mezzo = getattr(t, "mezzo", None)
                t.rimuovi_mezzo()
                db.collection("turni").document(t.id).set({
                    "mezzo_targa": ""
                }, merge=True)
                if old_mezzo and len(old_mezzo.turni_assegnati) == 0:
                    db.collection("mezzi").document(old_mezzo.targa).set({
                        "stato": "Disponibile",
                        "disponibile": True
                    }, merge=True)
                print(f"[GestioneFlottaController] Mezzo rimosso dal turno {t.id}.")
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
                "dispositiviPresenti": c.dispositiviPresenti,
                "risposte": getattr(c, "risposte", {}),
                "ruoloCompilatore": getattr(c, "ruoloCompilatore", ""),
                "idoneo": c.verificaIdoneita()
            })
            print(f"[GestioneFlottaController] compilaChecklist {c.id} salvata su Firebase.")
            return True
        except Exception as e:
            print(f"⚠️ Errore compilaChecklist in Firebase: {e}")
            return False

    def creaResoconto(self, targa: str = "", km: int = 0, note: str = "") -> bool:
        """Crea un resoconto/report di stato o fine servizio per la flotta."""
        import uuid
        from datetime import datetime
        rep_id = f"RES_{uuid.uuid4().hex[:8].upper()}"
        try:
            from FirebaseConfig import db
            db.collection("resoconti_flotta").document(rep_id).set({
                "id": rep_id,
                "targa": targa,
                "km": km,
                "note": note,
                "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            print(f"[GestioneFlottaController] creaResoconto {rep_id} salvato su Firebase.")
            return True
        except Exception as e:
            print(f"⚠️ Errore creaResoconto in Firebase: {e}")
            return False

    def richiediControlli(self, ruolo: str, c: Checklist | None = None) -> List[str]:
        from Checklist import Checklist
        if c is None:
            c = Checklist(id="TEMP_CL")
        r_clean = Checklist.normalizzaRuolo(ruolo)
        if r_clean == "Autista A":
            return c.getControlliMeccaniciEmergenza()
        elif r_clean == "Autista B":
            return c.getControlliMeccaniciBase()
        elif r_clean == "Soccorritore A":
            return c.getDispositiviSanitariAvanzati()
        elif r_clean == "Soccorritore B":
            return c.getDispositiviSanitariBase()
        return c.getControlliMeccaniciEmergenza()

    def richiediControlliDettagliati(self, ruolo: str, c: Checklist | None = None) -> List[dict]:
        from Checklist import Checklist
        if c is None:
            c = Checklist(id="TEMP_CL")
        return c.getControlliPerRuolo(ruolo)

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

    def visualizzaStatoMezzi(self, sistema=None) -> List[Mezzo]:
        """Restituisce l'elenco dei mezzi dal sistema o interrogando direttamente Firestore."""
        if sistema and getattr(sistema, "mezzi", None):
            return list(sistema.mezzi)
        try:
            from FirebaseConfig import db
            from Mezzo import Mezzo
            mezzi = []
            docs = db.collection("mezzi").get()
            for doc in docs:
                dati = doc.to_dict() or {}
                m = Mezzo(
                    targa=doc.id,
                    tipo=dati.get("tipo", "Ambulanza"),
                    chilometraggioTotale=int(dati.get("chilometraggioTotale", 0) or dati.get("chilometraggio", 0)),
                    stato=dati.get("stato", "Disponibile"),
                    dataScadenzaAssicurazione=dati.get("dataScadenzaAssicurazione", "")
                )
                mezzi.append(m)
            return mezzi
        except Exception as e:
            print(f"⚠️ Errore visualizzaStatoMezzi: {e}")
            return []
