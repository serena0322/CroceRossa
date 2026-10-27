from __future__ import annotations
from typing import List, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from Volontario import Volontario
    from Corso import Corso

class GestioneFormazioneController:
    """
    Controller applicativo per i percorsi formativi e brevetti CRI (GRASP Controller).
    Coordina l'iscrizione dei volontari con controllo di capienza massima (maxPartecipanti),
    la registrazione delle presenze e attestazioni, e la suddivisione del catalogo corsi.
    """
    def __init__(self):
        pass

    def attestaPartecipazione(self, s: str, volontari: List[Volontario]) -> None:
        if not s:
            print("[Formazione/Errore] Corso ID vuoto.")
            return
        try:
            from Sistema import Sistema
            sys_inst = Sistema.get_instance()
            if sys_inst:
                c_obj = next((c for c in sys_inst.corsi if str(c.id) == str(s)), None)
                if c_obj:
                    for v in volontari:
                        if v not in c_obj.partecipanti:
                            c_obj.partecipanti.append(v)
                        if not hasattr(c_obj, "certificati_ids") or c_obj.certificati_ids is None:
                            c_obj.certificati_ids = []
                        if v.cod_fiscale not in c_obj.certificati_ids:
                            c_obj.certificati_ids.append(v.cod_fiscale)
                        if c_obj not in v.corsi_frequentati:
                            v.corsi_frequentati.append(c_obj)
                        if c_obj in v.formazione:
                            v.formazione.remove(c_obj)
                sys_inst.salva_dati()
            print(f"[Formazione] attestaPartecipazione per corso {s} completato.")
        except Exception as e:
            print(f"[Formazione/Errore] attestaPartecipazione nel database locale: {e}")

    def creaCorso(self, c: Corso) -> bool:
        if not c.id:
            import uuid
            c.id = str(uuid.uuid4())[:8].upper()
            c.nome = c.nome if c.nome else c.titolo
        try:
            from Sistema import Sistema
            sys_inst = Sistema.get_instance()
            if sys_inst:
                existing = next((x for x in sys_inst.corsi if str(x.id) == str(c.id)), None)
                if not existing:
                    sys_inst.corsi.append(c)
                sys_inst.salva_dati()
            print(f"[Formazione] creaCorso {c.id} salvato nel database locale.")
            return True
        except Exception as e:
            print(f"[Formazione/Errore] creaCorso nel database locale: {e}")
            return False

    def eliminaCorso(self, s: str) -> bool:
        try:
            from Sistema import Sistema
            sys_inst = Sistema.get_instance()
            if sys_inst:
                sys_inst.corsi = [c for c in sys_inst.corsi if str(c.id) != str(s)]
                sys_inst.salva_dati()
            print(f"[Formazione] eliminaCorso {s} cancellato dal database locale.")
            return True
        except Exception as e:
            print(f"[Formazione/Errore] eliminaCorso nel database locale: {e}")
            return False

    def iscriviVolontario(self, v: Volontario, s: Any, sistema=None) -> bool:
        from Sistema import Sistema
        sys_inst = sistema or Sistema.get_instance()
        c_obj = s if hasattr(s, "id") and hasattr(s, "maxPartecipanti") else None
        s_id = str(getattr(s, "id", s))

        # 1. Verifica capienza su oggetto corso diretto
        if c_obj is not None:
            if c_obj.isCompleto() and v not in c_obj.partecipanti:
                print(f"[Formazione/Avviso] Impossibile iscriversi: corso '{c_obj.titolo or c_obj.nome}' al completo ({c_obj.maxPartecipanti} posti).")
                return False
            try:
                c_obj.aggiungiIscritto(v)
            except ValueError as e:
                print(f"[Formazione/Avviso] {e}")
                return False

        # 2. Verifica capienza su oggetto in memoria se presente in sistema
        elif sys_inst and getattr(sys_inst, "corsi", None):
            c_mem = next((c for c in sys_inst.corsi if str(c.id) == s_id), None)
            if c_mem:
                if c_mem.isCompleto() and v not in c_mem.partecipanti:
                    print(f"[Formazione/Avviso] Impossibile iscriversi: corso '{c_mem.titolo or c_mem.nome}' al completo ({c_mem.maxPartecipanti} posti).")
                    return False
                try:
                    c_mem.aggiungiIscritto(v)
                except ValueError as e:
                    print(f"[Formazione/Avviso] {e}")
                    return False

        if sys_inst:
            sys_inst.salva_dati()
        return True

    def disiscriviVolontario(self, v: Volontario, s: str, forza: bool = False) -> bool:
        """
        Rimuove l'iscrizione del volontario a un corso non ancora completato.
        Regola Tesina UML: L'annullamento è consentito fino a 2 giorni prima dell'inizio del corso.
        """
        if not v or not s:
            return False

        from Sistema import Sistema
        sys_inst = Sistema.get_instance()
        c_target = None
        if sys_inst:
            c_target = next((c for c in sys_inst.corsi if str(c.id) == str(s)), None)
        if not c_target and hasattr(v, "formazione"):
            c_target = next((c for c in v.formazione if str(c.id) == str(s)), None)

        if not forza and c_target and hasattr(c_target, "isAnnullabile") and not c_target.isAnnullabile(delta_giorni=2):
            print(f"[Formazione/Avviso] Impossibile annullare l'iscrizione al corso '{c_target.nome or c_target.titolo}': mancano meno di 2 giorni all'inizio.")
            return False

        if sys_inst:
            if c_target and v in c_target.partecipanti:
                c_target.partecipanti.remove(v)
            c_obj = next((c for c in getattr(v, "formazione", []) if str(c.id) == str(s)), None)
            if c_obj:
                v.disiscriviti_dal_corso(c_obj)
            sys_inst.salva_dati()
        return True

    def modificaCorso(self, s: str, c: Corso) -> bool:
        return self.creaCorso(c)

    def visualizzaCatalog(self, sistema=None) -> List[Corso]:
        """Restituisce l'elenco dei corsi di formazione dal sistema."""
        from Sistema import Sistema
        sys_inst = sistema or Sistema.get_instance()
        if sys_inst and getattr(sys_inst, "corsi", None):
            return list(sys_inst.corsi)
        return []

    def visualizzaCatalogo(self, sistema=None) -> List[Corso]:
        """Alias in italiano per visualizzaCatalog (UML)."""
        return self.visualizzaCatalog(sistema=sistema)

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
            cid = c.id or ""
            ctitolo = (c.titolo or c.nome or "").strip().upper()
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

    # ==========================================================
    # CASI D'USO UML (UML Gestione Corsi)
    # ==========================================================

    def visualizzaCatalogoCorsi(self, sistema=None) -> List[Corso]:
        """
        Caso d'uso UML: VisualizzaCatalogoCorsi.
        Restituisce i corsi a catalogo per i volontari.
        """
        return self.visualizzaCatalog(sistema=sistema)

    def visualizzaDettagliCorso(self, c: Corso) -> dict:
        """
        Caso d'uso UML: VisualizzaDettagliCorso («extend» VisualizzaCatalogoCorsi).
        Restituisce i dettagli completi del corso.
        """
        if not c:
            return {}
        return c.getDati() if hasattr(c, "getDati") else {
            "codice": getattr(c, "codice", getattr(c, "id", "")),
            "nome": getattr(c, "nome", getattr(c, "titolo", "")),
            "dataInizio": getattr(c, "dataInizio", ""),
            "dataFine": getattr(c, "dataFine", ""),
            "luogo": getattr(c, "luogo", ""),
            "direttoreCorso": getattr(c, "direttoreCorso", getattr(c, "direttore", "")),
            "postiLiberi": getattr(c, "postiLiberi", 0),
            "postiTotali": getattr(c, "postiTotali", getattr(c, "maxPartecipanti", 20)),
            "stato": getattr(c, "stato", "")
        }

    def filtraCorsi(self, corsi: List[Corso], criterio: str = "", solo_disponibili: bool = False) -> List[Corso]:
        """
        Caso d'uso UML: FiltraCorsi («extend» VisualizzaCatalogoCorsi).
        Filtra l'elenco dei corsi per titolo/nome, qualifica rilasciata o disponibilità.
        """
        risultati = list(corsi)
        if solo_disponibili:
            risultati = [c for c in risultati if not (c.isCompleto() if hasattr(c, "isCompleto") else len(getattr(c, "partecipanti", [])) >= getattr(c, "postiTotali", 20))]
        if criterio:
            crit = criterio.strip().lower()
            risultati = [
                c for c in risultati
                if crit in str(getattr(c, "nome", "")).lower()
                or crit in str(getattr(c, "titolo", "")).lower()
                or crit in str(getattr(c, "tipoCorso", "")).lower()
                or crit in str(getattr(c, "luogo", "")).lower()
            ]
        return risultati

    def iscriviCorso(self, v: Volontario, c: Any, sistema=None) -> bool:
        """
        Caso d'uso UML: IscriviCorso («include» VisualizzaCatalogoCorsi).
        Iscrive il volontario al corso prescelto.
        """
        return self.iscriviVolontario(v, c, sistema=sistema)

    def visualizzaIscrizioni(self, v: Volontario) -> List[Corso]:
        """
        Caso d'uso UML: VisualizzaIscrizioni.
        Restituisce i corsi a cui il volontario è attualmente iscritto.
        """
        if not v:
            return []
        return list(getattr(v, "formazione", []))

    def annullaIscrizioneCorso(self, v: Volontario, id_corso: str, forza: bool = False) -> bool:
        """
        Caso d'uso UML: AnnullaIscrizioneCorso («extend» VisualizzaIscrizioni).
        Cancella l'iscrizione del volontario al corso nel rispetto del preavviso di 2 giorni.
        """
        return self.disiscriviVolontario(v, id_corso, forza=forza)

    def visualizzaCorsi(self, sistema=None) -> List[Corso]:
        """
        Caso d'uso UML: VisualizzaCorsi (Referente).
        Restituisce tutti i corsi gestiti nel sistema CRI.
        """
        from Sistema import Sistema
        sys_inst = sistema or Sistema.get_instance()
        if sys_inst and getattr(sys_inst, "corsi", None):
            return list(sys_inst.corsi)
        return []

    def visualizzaIscrittiCorso(self, c: Corso) -> List[Volontario]:
        """
        Caso d'uso UML: VisualizzaIscrittiCorso («extend» VisualizzaCorsi).
        Restituisce la lista degli iscritti al corso.
        """
        if not c:
            return []
        return c.getIscritti() if hasattr(c, "getIscritti") else list(getattr(c, "partecipanti", []))

    def ricercaCorso(self, criterio: str, sistema=None) -> List[Corso]:
        """
        Caso d'uso UML: RicercaCorso («include» in CUDCorso e in GestioneSistema).
        Cerca tra i corsi del sistema per identificativo, titolo, luogo o qualifica.
        """
        from Sistema import Sistema
        sys_inst = sistema or Sistema.get_instance()
        if not sys_inst or not getattr(sys_inst, "corsi", None):
            return []
        if not criterio:
            return list(sys_inst.corsi)
        crit = str(criterio).strip().lower()
        return [
            c for c in sys_inst.corsi
            if crit in str(getattr(c, "codice", getattr(c, "id", ""))).lower()
            or crit in str(getattr(c, "nome", getattr(c, "titolo", ""))).lower()
            or crit in str(getattr(c, "tipoCorso", "")).lower()
            or crit in str(getattr(c, "luogo", "")).lower()
        ]

    def cudCorso(self, operazione: str, corso_o_id, dati: dict | None = None) -> bool:
        """
        Caso d'uso UML: CUDCorso («include» RicercaCorso).
        Gestisce Creazione, Modifica/Update ed Eliminazione dei corsi di formazione CRI.
        """
        from Corso import Corso
        op = operazione.strip().upper()
        if op in ["C", "CREATE", "CREA"]:
            if isinstance(corso_o_id, Corso):
                return self.creaCorso(corso_o_id)
            elif isinstance(dati, dict):
                c = Corso(**dati)
                return self.creaCorso(c)
            return False

        elif op in ["U", "UPDATE", "MODIFICA"]:
            id_c = str(getattr(corso_o_id, "id", getattr(corso_o_id, "codice", corso_o_id)))
            from Sistema import Sistema
            s = Sistema.get_instance()
            c_obj = next((c for c in getattr(s, "corsi", []) if str(c.id) == id_c or str(c.codice) == id_c), None) if s else None
            if not c_obj and isinstance(corso_o_id, Corso):
                c_obj = corso_o_id
            if c_obj:
                if dati:
                    if hasattr(c_obj, "setDati"):
                        c_obj.setDati(**dati)
                    else:
                        for k, v in dati.items():
                            if hasattr(c_obj, k):
                                setattr(c_obj, k, v)
                return self.modificaCorso(id_c, c_obj)
            return False

        elif op in ["D", "DELETE", "ELIMINA"]:
            id_c = str(getattr(corso_o_id, "id", getattr(corso_o_id, "codice", corso_o_id)))
            return self.eliminaCorso(id_c)

        return False


