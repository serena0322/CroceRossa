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

    def disiscriviVolontario(self, v: Volontario, s: str) -> bool:
        """Rimuove l'iscrizione del volontario a un corso non ancora completato."""
        if not v or not s:
            return False
        try:
            from FirebaseConfig import db
            corso_ref = db.collection("corsi").document(s)
            doc = corso_ref.get()
            if doc.exists:
                vids = doc.to_dict().get("partecipanti_ids", [])
                cf_str = str(v.cod_fiscale)
                if cf_str in vids:
                    vids.remove(cf_str)
                    corso_ref.update({"partecipanti_ids": vids})
        except Exception as e:
            print(f"⚠️ Errore disiscriviVolontario su Firebase: {e}")

        # Aggiornamento locale
        c_obj = next((c for c in getattr(v, "formazione", []) if str(c.id) == str(s)), None)
        if c_obj:
            v.disiscriviti_dal_corso(c_obj)
        if hasattr(v, "aggiorna_firestore"):
            try:
                v.aggiorna_firestore()
            except Exception:
                pass
        return True

    def modificaCorso(self, s: str, c: Corso) -> bool:
        return self.creaCorso(c)

    def visualizzaCatalog(self, sistema=None) -> List[Corso]:
        """Restituisce l'elenco dei corsi di formazione dal sistema o da Firestore."""
        if sistema and getattr(sistema, "corsi", None):
            return list(sistema.corsi)
        try:
            from FirebaseConfig import db
            from Corso import Corso
            corsi = []
            docs = db.collection("corsi").get()
            for doc in docs:
                dati = doc.to_dict() or {}
                c = Corso(
                    id=doc.id,
                    titolo=str(dati.get("titolo") or dati.get("nome") or ""),
                    nome=str(dati.get("nome") or dati.get("titolo") or ""),
                    dataInizio=str(dati.get("dataInizio") or ""),
                    dataFine=str(dati.get("dataFine") or ""),
                    esito=bool(dati.get("esito", False)),
                    checklist=dati.get("checklist", []),
                    scadenza=str(dati.get("scadenza") or "")
                )
                c.certificati_ids = dati.get("certificati_ids", []) or []
                corsi.append(c)
            return corsi
        except Exception as e:
            print(f"⚠️ Errore visualizzaCatalog: {e}")
            return []

    def ottieniCorsiSuddivisi(self, utente, sistema=None) -> dict:
        """
        Restituisce i corsi categorizzati in modo trasparente per l'utente:
        - 'effettuati': corsi completati con successo / attestati / con qualifica conseguita
        - 'in_corso': corsi a cui l'utente è attualmente iscritto (non ancora effettuati / in corso)
        - 'disponibili': corsi aperti nel catalogo CRI a cui l'utente non è ancora iscritto
        - 'tutti': intero catalogo corsi
        """
        tutti_corsi = self.visualizzaCatalog(sistema=sistema)
        if not utente:
            return {"effettuati": [], "in_corso": [], "disponibili": tutti_corsi, "tutti": tutti_corsi}

        cf = str(getattr(utente, "cod_fiscale", "")).strip().upper()
        qualifiche_utente = [str(q).strip().upper() for q in getattr(utente, "qualifiche", [])]
        specializzazioni_utente = [str(s).strip().upper() for s in getattr(utente, "specializzazioni", [])]
        competenze = set(qualifiche_utente + specializzazioni_utente)

        cf_frequentati_ids = {str(c.id) for c in getattr(utente, "corsi_frequentati", []) if getattr(c, "id", None)}
        cf_formazione_ids = {str(c.id) for c in getattr(utente, "formazione", []) if getattr(c, "id", None)}

        effettuati = []
        in_corso = []
        disponibili = []

        for c in tutti_corsi:
            cid = str(c.id)
            ctitolo = str(c.titolo or c.nome or "").strip().upper()
            cqualifica = str(getattr(c, "qualificaRilasciata", "")).strip().upper()
            
            # Partecipanti e certificati
            partecipanti_cfs = [str(getattr(p, "cod_fiscale", p)).strip().upper() for p in getattr(c, "partecipanti", [])]
            certificati_cfs = [str(getattr(p, "cod_fiscale", p)).strip().upper() for p in getattr(c, "certificati_ids", [])]

            # È considerato EFFETTUATO / COMPLETATO se:
            # 1. Presente nella lista corsi_frequentati dell'utente
            # 2. Oppure CF presente nei certificati del corso
            # 3. Oppure il titolo o qualifica del corso è tra le qualifiche del volontario
            is_effettuato = (
                cid in cf_frequentati_ids or
                cf in certificati_cfs or
                (ctitolo and ctitolo in competenze) or
                (cqualifica and cqualifica in competenze)
            )

            if is_effettuato:
                effettuati.append(c)
            elif cid in cf_formazione_ids or cf in partecipanti_cfs:
                # È iscritto ma non ancora effettuato / in svolgimento
                in_corso.append(c)
            else:
                # Non ancora effettuato e non iscritto (disponibile a catalogo)
                disponibili.append(c)

        return {
            "effettuati": effettuati,
            "in_corso": in_corso,
            "disponibili": disponibili,
            "tutti": tutti_corsi
        }

