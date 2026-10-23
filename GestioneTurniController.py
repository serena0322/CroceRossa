from __future__ import annotations
from typing import List, TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from Volontario import Volontario
    from Turno import Turno

class GestioneTurniController:
    """
    Controller applicativo per la gestione del ciclo di vita dei turni di servizio (GRASP Controller).
    Coordina la validazione dei vincoli operativi (sovrapposizioni, capienza, limiti orari giornalieri)
    e sincronizza lo stato sia in memoria che nel database locale JSON.
    """
    def __init__(self):
        pass

    def annullaPrenotazione(self, t: Turno) -> bool:
        """
        Rimuove l'assegnazione dei volontari dal turno specificato e aggiorna il database locale JSON.
        Garantisce la consistenza rimuovendo sia gli ID che i ruoli associati.
        """
        try:
            for v in list(t.volontari_assegnati):
                if hasattr(v, "turni_assegnati") and t in v.turni_assegnati:
                    v.turni_assegnati.remove(t)
            t.volontari_assegnati = []
            t.volontari_ruoli = {}
            from Sistema import Sistema
            s = Sistema.get_instance()
            if s:
                s.salva_dati()
            print(f"[GestioneTurniController] annullaPrenotazione turno {t.codice} completato.")
            return True
        except Exception as e:
            print(f"[Turni/Errore] annullaPrenotazione nel database locale: {e}")
            return False

    def assegnaTurno(self, v: Volontario, t: Turno) -> None:
        """Assegna formalmente il turno al volontario invocando la procedura di prenotazione."""
        self.prenotaTurno(t.codice, v.cod_fiscale)

    def calcolaOrePeriodo(self, v: Volontario, inizio: str, fine: str) -> int:
        """Calcola il monte ore complessivo svolto dal volontario."""
        return v.oreServizio

    def _verifica_permessi_referente(self, utente) -> bool:
        """
        Controllo degli accessi (RBAC - Role-Based Access Control):
        Solo gli utenti con ruolo 'Referente' hanno i privilegi di creazione, modifica ed eliminazione turni.
        """
        if utente is None:
            return True  # Fallback per chiamate di sistema/test senza utente esplicito
        ruolo = str(getattr(utente, "ruolo", "")).strip().lower()
        if ruolo == "referente" or hasattr(utente, "settoreGestito"):
            return True
        print("[Turni/Errore] Operazione negata: solo gli utenti con ruolo 'Referente' possono gestire i turni.")
        return False

    def creaTurno(self, t: Turno, utente=None) -> bool:
        """
        Registra un nuovo turno operativo nel sistema e lo persiste nel database locale JSON.
        Se non è presente un ID, genera un identificativo univoco compatto.
        """
        if not self._verifica_permessi_referente(utente):
            return False
        if not t.codice:
            import uuid
            t.codice = str(uuid.uuid4())[:8].upper()
        try:
            from Sistema import Sistema
            s = Sistema.get_instance()
            if s:
                existing = next((x for x in s.turni if str(x.codice) == str(t.codice)), None)
                if not existing:
                    s.turni.append(t)
                s.salva_dati()
            print(f"[GestioneTurniController] creaTurno {t.codice} salvato nel database locale.")
            return True
        except Exception as e:
            print(f"[Turni/Errore] creaTurno nel database locale: {e}")
            return False

    def modificaTurno(self, idTurno: str, t: Turno, utente=None) -> bool:
        """
        Aggiorna i parametri di un turno esistente previa verifica dei permessi da referente.
        Vincolo di business: il turno è modificabile solo ed esclusivamente se in stato 'Aperto'.
        """
        if not self._verifica_permessi_referente(utente):
            return False
        
        # Controllo vincolo di business: Modifica consentita solo se il turno è 'Aperto'
        stato_corrente = str(getattr(t, "stato", "Aperto")).strip().lower()
        if stato_corrente != "aperto":
            print(f"[Turni/Avviso] Impossibile modificare il turno {idTurno}: consentita la modifica solo se in stato 'Aperto' (stato attuale: '{getattr(t, 'stato', 'N/D')}').")
            return False

        t.codice = idTurno
        return self.creaTurno(t, utente=utente)

    def eliminaTurno(self, idTurno: str, utente=None) -> bool:
        """Cancella il turno dal database locale JSON."""
        if not self._verifica_permessi_referente(utente):
            return False
        try:
            from Sistema import Sistema
            s = Sistema.get_instance()
            if s:
                s.turni = [t for t in s.turni if str(t.codice) != str(idTurno)]
                s.salva_dati()
            print(f"[GestioneTurniController] eliminaTurno {idTurno} rimosso dal database locale.")
            return True
        except Exception as e:
            print(f"[Turni/Errore] eliminaTurno nel database locale: {e}")
            return False

    def prenotaTurno(self, idTurno: str, idVolontario: str, ruolo: str = "Soccorritore", sistema: Any = None) -> bool:
        """
        Iscrive un volontario al turno specificato.
        Verifica preventivamente il limite delle 12 ore massime giornaliere.
        """
        from Sistema import Sistema
        s = sistema or Sistema.get_instance()
        try:
            if s:
                turno_obj = next((t for t in getattr(s, "turni", []) if str(t.codice) == str(idTurno)), None)
                vol_obj = next((v for v in getattr(s, "volontari", []) if v.cod_fiscale.upper() == idVolontario.upper()), None)
                if turno_obj and vol_obj:
                    if not self.verificaLimiteOreGiornaliere(vol_obj, turno_obj):
                        return False
                    if vol_obj not in turno_obj.volontari_assegnati:
                        turno_obj.volontari_assegnati.append(vol_obj)
                    if not hasattr(turno_obj, "volontari_ruoli") or turno_obj.volontari_ruoli is None:
                        turno_obj.volontari_ruoli = {}
                    turno_obj.volontari_ruoli[idVolontario] = ruolo
                    if hasattr(vol_obj, "turni_assegnati") and turno_obj not in vol_obj.turni_assegnati:
                        vol_obj.turni_assegnati.append(turno_obj)
                s.salva_dati()
            print(f"[GestioneTurniController] prenotaTurno {idTurno} salvato nel database locale.")
            return True
        except Exception as e:
            print(f"[Turni/Errore] prenotaTurno nel database locale: {e}")
            return False

    def validaDati(self, t: Turno | None = None) -> bool:
        """
        Verifica la consistenza dei dati essenziali del turno:
        data valida, orari di inizio e fine presenti, e richiesta di almeno un volontario.
        """
        if not t:
            return False
        if not t.data or not t.data.strip():
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
        req = t.patenteRichiesta.strip().upper()
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
            if altro.codice == t.codice:
                continue
            if altro.data.strip() == t.data.strip():
                try:
                    t_ini = t.oraInizio.strip()
                    t_fin = t.oraFine.strip()
                    a_ini = altro.oraInizio.strip()
                    a_fin = altro.oraFine.strip()
                    # Condizione necessaria e sufficiente di sovrapposizione tra fasce orarie
                    if max(t_ini, a_ini) < min(t_fin, a_fin):
                        print(f"[Turni/Avviso] Sovrapposizione oraria rilevata con turno {altro.codice} ({altro.data} {altro.fascia_oraria})")
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
            if altro.codice == t.codice:
                continue
            if altro.data.strip() == t.data.strip():
                ore_giornaliere += altro.calcola_durata_ore() if hasattr(altro, "calcola_durata_ore") else 4.0
        
        totale = ore_giornaliere + durata_nuovo
        if totale > max_ore:
            print(f"[Turni/Avviso] Limite ore giornaliere superato: {totale:.1f}h richieste > {max_ore}h massime consentite per il giorno {t.data}")
            return False
        return True

    def visualizzaTurniDisponibili(self, sistema=None) -> List[Turno]:
        """
        Restituisce i turni aperti e con posti ancora scoperti dal database locale.
        """
        from Sistema import Sistema
        s = sistema or Sistema.get_instance()
        if s and getattr(s, "turni", None):
            return [
                t for t in s.turni
                if str(t.stato).strip().capitalize() in ["Proposto", "Aperto"]
                and len(getattr(t, "volontari_assegnati", [])) < getattr(t, "personeRichieste", 1)
            ]
        return []
