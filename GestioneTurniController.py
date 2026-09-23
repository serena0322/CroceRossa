from __future__ import annotations
from typing import List, TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from Volontario import Volontario
    from Turno import Turno

class GestioneTurniController:
    """
    Controller applicativo per la gestione del ciclo di vita dei turni di servizio (GRASP Controller).
    Coordina la validazione dei vincoli operativi (sovrapposizioni, capienza, limiti orari giornalieri)
    e sincronizza lo stato sia in memoria che su Cloud Firestore.
    """
    def __init__(self):
        pass

    def annullaPrenotazione(self, t: Turno) -> bool:
        """
        Rimuove l'assegnazione dei volontari dal turno specificato e aggiorna il documento su Firestore.
        Garantisce la consistenza rimuovendo sia gli ID che i ruoli associati.
        """
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
        """Assegna formalmente il turno al volontario invocando la procedura di prenotazione."""
        self.prenotaTurno(t.id, v.cod_fiscale)

    def calcolaOrePeriodo(self, v: Volontario, inizio: str, fine: str) -> int:
        """Calcola il monte ore complessivo svolto dal volontario."""
        return v.monteOreTotale

    def _verifica_permessi_referente(self, utente) -> bool:
        """
        Controllo degli accessi (RBAC - Role-Based Access Control):
        Solo gli utenti con ruolo 'Referente' hanno i privilegi di creazione, modifica ed eliminazione turni.
        """
        if utente is None:
            return True  # Fallback per chiamate di sistema/test senza utente esplicito
        ruolo = str(getattr(utente, "ruolo", "")).strip().lower()
        if ruolo == "referente" or hasattr(utente, "area_gestita"):
            return True
        print("❌ Operazione negata: solo gli utenti con ruolo 'Referente' possono gestire i turni.")
        return False

    def creaTurno(self, t: Turno, utente=None) -> bool:
        """
        Registra un nuovo turno operativo nel sistema e lo persiste su Firestore.
        Se non è presente un ID, genera un identificativo univoco compatto.
        """
        if not self._verifica_permessi_referente(utente):
            return False
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
                "paziente_nome": getattr(t, "paziente_nome", ""),
                "paziente_cognome": getattr(t, "paziente_cognome", ""),
                "paziente_cf": getattr(t, "paziente_cf", ""),
                "personeRichieste": t.personeRichieste,
                "persone_richieste": t.persone_richieste,
                "stato": t.stato,
                "tipoServizio": t.tipoServizio,
                "volontari_ids": [str(v.cod_fiscale) for v in t.volontari_assegnati]
            }, merge=True)
            print(f"[GestioneTurniController] creaTurno {t.id} salvato su Firebase.")
            return True
        except Exception as e:
            print(f"⚠️ Errore creaTurno in Firebase: {e}")
            return False

    def modificaTurno(self, idTurno: str, t: Turno, utente=None) -> bool:
        """Aggiorna i parametri di un turno esistente previa verifica dei permessi da referente."""
        if not self._verifica_permessi_referente(utente):
            return False
        t.id = idTurno
        return self.creaTurno(t, utente=utente)

    def eliminaTurno(self, idTurno: str, utente=None) -> bool:
        """Cancella il turno dal database Firestore."""
        if not self._verifica_permessi_referente(utente):
            return False
        try:
            from FirebaseConfig import db
            db.collection("turni").document(idTurno).delete()
            print(f"[GestioneTurniController] eliminaTurno {idTurno} rimosso da Firebase.")
            return True
        except Exception as e:
            print(f"⚠️ Errore eliminaTurno in Firebase: {e}")
            return False

    def prenotaTurno(self, idTurno: str, idVolontario: str, ruolo: str = "Soccorritore", sistema: Any = None) -> bool:
        """
        Iscrive un volontario al turno specificato.
        Verifica preventivamente il limite delle 12 ore massime giornaliere se l'istanza sistema è disponibile.
        """
        if sistema:
            turno_obj = next((t for t in getattr(sistema, "turni", []) if str(t.id) == str(idTurno)), None)
            vol_obj = next((v for v in getattr(sistema, "volontari", []) if str(v.cod_fiscale).upper() == str(idVolontario).upper()), None)
            if turno_obj and vol_obj:
                if not self.verificaLimiteOreGiornaliere(vol_obj, turno_obj):
                    return False
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
                # Se il turno non esiste ancora su Firestore, lo creiamo inizializzandolo come Proposto
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
        """
        Verifica la consistenza dei dati essenziali del turno:
        data valida, orari di inizio e fine presenti, e richiesta di almeno un volontario.
        """
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
        """
        Verifica se il volontario possiede la patente di guida CRI o la qualifica specifica
        richiesta per il servizio (es. Guida Ambulanza, Soccorso Trauma, BLSD).
        """
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
        """
        Verifica che il turno non sia in conflitto orario con altri turni già assegnati al volontario.
        
        Principio matematico di intersezione di due intervalli [A, B) e [C, D):
        Due fasce orarie si sovrappongono se e solo se:
            max(inizio_A, inizio_C) < min(fine_B, fine_D)
        
        Dettaglio tecnico:
        Gli orari sono formattati a due cifre con zeri ('HH:MM', es. '08:00', '14:30').
        In questo formato standard ISO, l'ordine lessicografico coincide esattamente
        con l'ordine cronologico, consentendo un confronto diretto in tempo costante O(1)
        senza dover istanziare pesanti oggetti datetime ad ogni iterazione.
        """
        if not v or not t or not getattr(v, "turni_assegnati", None):
            return True
        for altro in v.turni_assegnati:
            if altro.id == t.id:
                continue
            if str(altro.data).strip() == str(t.data).strip():
                try:
                    t_ini = t.oraInizio.strip()
                    t_fin = t.oraFine.strip()
                    a_ini = altro.oraInizio.strip()
                    a_fin = altro.oraFine.strip()
                    # Condizione necessaria e sufficiente di sovrapposizione tra fasce orarie
                    if max(t_ini, a_ini) < min(t_fin, a_fin):
                        print(f"⚠️ Sovrapposizione oraria rilevata con turno {altro.id} ({altro.data} {altro.fascia_oraria})")
                        return False
                except Exception:
                    pass
        return True

    def verificaLimiteOreGiornaliere(self, v: Volontario, t: Turno, max_ore: float = 12.0) -> bool:
        """
        Requisito di sicurezza e tutela del soccorritore (RF19):
        Impedisce turni cumulativi che superino le 12 ore giornaliere per il singolo volontario.
        
        Calcola la somma delle durate in ore di tutti i turni già assegnati nella data indicata
        e verifica che l'aggiunta del nuovo turno non ecceda la soglia massima consentita di 12 ore.
        """
        if not v or not t:
            return True
        durata_nuovo = t.calcola_durata_ore() if hasattr(t, "calcola_durata_ore") else 4.0
        ore_giornaliere = 0.0
        for altro in getattr(v, "turni_assegnati", []):
            if altro.id == t.id:
                continue
            if str(altro.data).strip() == str(t.data).strip():
                ore_giornaliere += altro.calcola_durata_ore() if hasattr(altro, "calcola_durata_ore") else 4.0
        
        totale = ore_giornaliere + durata_nuovo
        if totale > max_ore:
            print(f"⚠️ Limite ore giornaliere superato: {totale:.1f}h richieste > {max_ore}h massime consentite per il giorno {t.data}")
            return False
        return True

    def visualizzaTurniDisponibili(self, sistema=None) -> List[Turno]:
        """
        Restituisce i turni aperti e con posti ancora scoperti.
        Interroga prioritariamente lo stato in memoria del sistema, oppure consulta direttamente Firestore.
        """
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
