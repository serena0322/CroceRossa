from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from Volontario import Volontario
    from Corso import Corso

class GestioneFormazioneController:
    def __init__(self):
        pass

    def attestaPartecipazione(self, s: str, volontari: List[Volontario]) -> None:
        if not s:
            print("⚠️ Errore: Corso ID vuoto.")
            return
        try:
            from FirebaseConfig import db
            # Update matching course document in Firebase to associate verified members
            corso_ref = db.collection("corsi").document(s)
            doc = corso_ref.get()
            if doc.exists:
                vids = doc.to_dict().get("partecipanti_ids", [])
                for v in volontari:
                    if str(v.cod_fiscale) not in vids:
                        vids.append(str(v.cod_fiscale))
                corso_ref.update({"partecipanti_ids": vids})
            print(f"[GestioneFormazioneController] attestaPartecipazione per corso {s} completato.")
        except Exception as e:
            print(f"⚠️ Errore attestaPartecipazione in Firebase: {e}")

    def creaCorso(self, c: Corso) -> bool:
        if not c.id:
            import uuid
            c.id = str(uuid.uuid4())[:8].upper()
            c.nome = c.nome if c.nome else c.titolo
        try:
            from FirebaseConfig import db
            db.collection("corsi").document(c.id).set({
                "id": c.id,
                "titolo": c.titolo,
                "nome": c.nome,
                "dataInizio": c.dataInizio,
                "dataFine": c.dataFine,
                "esito": c.esito,
                "checklist": c.checklist,
                "scadenza": c.scadenza,
                "partecipanti_ids": [str(p.cod_fiscale) for p in c.partecipanti]
            })
            print(f"[GestioneFormazioneController] creaCorso {c.id} salvato su Firebase.")
            return True
        except Exception as e:
            print(f"⚠️ Errore creaCorso in Firebase: {e}")
            return False

    def eliminaCorso(self, s: str) -> bool:
        try:
            from FirebaseConfig import db
            db.collection("corsi").document(s).delete()
            print(f"[GestioneFormazioneController] eliminaCorso {s} cancellato da Firebase.")
            return True
        except Exception as e:
            print(f"⚠️ Errore eliminaCorso in Firebase: {e}")
            return False

    def iscriviVolontario(self, v: Volontario, s: str) -> bool:
        try:
            from FirebaseConfig import db
            corso_ref = db.collection("corsi").document(s)
            doc = corso_ref.get()
            if doc.exists:
                vids = doc.to_dict().get("partecipanti_ids", [])
                if str(v.cod_fiscale) not in vids:
                    vids.append(str(v.cod_fiscale))
                    corso_ref.update({"partecipanti_ids": vids})
            return True
        except Exception as e:
            print(f"⚠️ Errore iscriviVolontario in Firebase: {e}")
            return False

    def modificaCorso(self, s: str, c: Corso) -> bool:
        return self.creaCorso(c)

    def visualizzaCatalog(self) -> List[Corso]:
        return []
