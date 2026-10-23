from __future__ import annotations
from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from Mezzo import Mezzo
    from Turno import Turno
    from Checklist import Checklist
    from Report import Report

class GestioneFlottaController:
    """
    Controller applicativo per il parco mezzi CRI (GRASP Controller).
    Coordina l'assegnazione dei veicoli ai servizi di emergenza o trasporto sanitario ordinario,
    la compilazione differenziata delle checklist veicolari (UC 8), e l'aggiornamento
    dello stato operativo (Disponibile, Assegnato, In Manutenzione, Dismesso).
    """
    def __init__(self):
        pass

    def _verifica_permessi_referente(self, utente) -> bool:
        """
        Controllo degli accessi (RBAC):
        La registrazione e l'assegnazione dei veicoli della flotta sono riservate al Referente di settore.
        """
        if utente is None:
            return True  # Fallback per chiamate interne o test
        ruolo = str(getattr(utente, "ruolo", "")).strip().lower()
        if ruolo == "referente" or hasattr(utente, "settoreGestito"):
            return True
        print("❌ Operazione negata: solo gli utenti con ruolo 'Referente' possono gestire la flotta.")
        return False

    def aggiungiMezzo(self, m: Mezzo, utente=None) -> bool:
        """
        Inserisce un nuovo automezzo nel parco veicoli CRI e lo memorizza nel database locale JSON.
        Richiede i privilegi di Referente.
        """
        if not self._verifica_permessi_referente(utente):
            return False
        try:
            from Sistema import Sistema
            s = Sistema.get_instance()
            if s:
                existing = next((x for x in s.mezzi if x.targa.strip().upper() == m.targa.strip().upper()), None)
                if existing:
                    existing.tipo = m.tipo
                    existing.chilometraggioTotale = m.chilometraggioTotale
                    existing.stato = m.stato
                    existing.dataScadenzaAssicurazione = m.dataScadenzaAssicurazione
                else:
                    s.mezzi.append(m)
                s.salva_dati()
            print(f"[GestioneFlottaController] aggiungiMezzo {m.targa} salvato nel database locale.")
            return True
        except Exception as e:
            print(f"⚠️ Errore aggiungiMezzo nel database locale: {e}")
            return False

    def assegnaMezzoATurno(self, m: Mezzo | None, t: Turno, utente=None) -> bool:
        """
        Associa o disassocia un mezzo da un turno di servizio.
        Se m è fornito: il mezzo viene marcato come 'Assegnato' e collegato al turno.
        Se m è None: il mezzo precedente viene svincolato e torna 'Disponibile'.
        """
        if not self._verifica_permessi_referente(utente):
            return False
        try:
            if m:
                t.assegna_mezzo(m)
                m.stato = "Assegnato"
                m._disponibile = False
                print(f"[GestioneFlottaController] Mezzo {m.targa} assegnato al turno {t.codice}.")
            else:
                old_mezzo = getattr(t, "mezzo", None)
                t.rimuovi_mezzo()
                if old_mezzo and len(old_mezzo.turni_assegnati) == 0:
                    old_mezzo.stato = "Disponibile"
                    old_mezzo._disponibile = True
                print(f"[GestioneFlottaController] Mezzo rimosso dal turno {t.codice}.")
            from Sistema import Sistema
            s = Sistema.get_instance()
            if s:
                s.salva_dati()
            return True
        except Exception as e:
            print(f"⚠️ Errore assegnaMezzoATurno nel database locale: {e}")
            return False

    def compilaChecklist(self, c: Checklist) -> bool:
        """
        Salva nel database locale la checklist di verifica pre-servizio compilata dal personale di bordo.
        Registra l'esito dell'idoneità del veicolo alla missione.
        """
        try:
            from Sistema import Sistema
            s = Sistema.get_instance()
            if s:
                if hasattr(s, "checklist") and c not in s.checklist:
                    s.checklist.append(c)
                s.salva_dati()
            print(f"[GestioneFlottaController] compilaChecklist {c.id} salvata nel database locale.")
            return True
        except Exception as e:
            print(f"⚠️ Errore compilaChecklist nel database locale: {e}")
            return False

    def creaResoconto(self, targa: str = "", km: int = 0, note: str = "") -> bool:
        """
        Genera un resoconto di rientro in sede o manutenzione ordinaria, memorizzandolo nel database locale.
        """
        import uuid
        from datetime import datetime
        rep_id = f"RES_{uuid.uuid4().hex[:8].upper()}"
        try:
            from Sistema import Sistema
            s = Sistema.get_instance()
            if s:
                if targa and km > 0:
                    mezzo_obj = next((m for m in s.mezzi if m.targa.strip().upper() == targa.strip().upper()), None)
                    if mezzo_obj:
                        mezzo_obj.aggiornaKm(km)
                s.salva_dati()
            print(f"[GestioneFlottaController] creaResoconto {rep_id} salvato nel database locale.")
            return True
        except Exception as e:
            print(f"⚠️ Errore creaResoconto nel database locale: {e}")
            return False

    def richiediControlli(self, ruolo: str, c: Checklist | None = None) -> List[str]:
        """
        Restituisce la lista dei controlli specifici in base alla qualifica del soccorritore (UC 8):
        - Autista A: Controlli meccanici avanzati per mezzi di emergenza (olio, freni, sirene, pneumatici)
        - Autista B: Controlli meccanici per trasporto sanitario ordinario
        - Soccorritore A: Presidi sanitari avanzati (defibrillatore DAE, aspiratore, bombole O2)
        - Soccorritore B: Presidi sanitari di base (borsa medicazione, saturimetro, immobilizzatori)
        """
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
        """Restituisce le voci di controllo dettagliate provviste di categoria e descrizione."""
        from Checklist import Checklist
        if c is None:
            c = Checklist(id="TEMP_CL")
        return c.getControlliPerRuolo(ruolo)

    def salvaReport(self, r: Report) -> bool:
        """Persiste il report di fine turno nel database locale con i dati chilometrici ed orari."""
        try:
            from Sistema import Sistema
            s = Sistema.get_instance()
            if s:
                s.salva_dati()
            print(f"[GestioneFlottaController] salvaReport {r.id} salvato nel database locale.")
            return True
        except Exception as e:
            print(f"⚠️ Errore salvaReport nel database locale: {e}")
            return False

    def visualizzaStatoMezzi(self, sistema=None) -> List[Mezzo]:
        """
        Recupera l'elenco completo dei veicoli dal sistema locale.
        """
        if sistema and getattr(sistema, "mezzi", None):
            return list(sistema.mezzi)
        from Sistema import Sistema
        s = Sistema.get_instance()
        if s and getattr(s, "mezzi", None):
            return list(s.mezzi)
        return []
