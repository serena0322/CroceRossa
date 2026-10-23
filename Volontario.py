from __future__ import annotations
from Utente import Utente
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from Referente import Referente
    from Corso import Corso
    from Turno import Turno

class Volontario(Utente):
    """
    Rappresenta il profilo del Soccorritore / Volontario della Croce Rossa Italiana.
    Attributi UML: oreServizio, patenti, qualifiche.
    Metodi UML: aggiornaProfilo, aggiungiOreServizio, aggiungiPatente, aggiungiQualifica,
                getMonteOre, verificaCredenziali, prenotaTurno, annullaPrenotazione,
                getTurniAssegnati.
    """
    def __init__(
        self,
        codFiscale: str = "",
        nome: str = "",
        cognome: str = "",
        email: str = "",
        dataNascita: str = "",
        telefono: str = "",
        ruolo: str = "volontario",
        password: str = "",
        oreServizio: int = 0,
        patenti: List[str] | None = None,
        qualifiche: List[str] | None = None,
        disponibilita: List[str] | None = None,
        # compatibility arguments:
        cod_fiscale: str | None = None,
        nascita: str | None = None,
        data_nascita: str | None = None,
        curriculum: str = "",
        formazione: List[Corso] | None = None,
        comitato_appartenenza: str = "",
        patenti_pdf: dict[str, str] | None = None,
        patente_pdf_path: str = "",
        app_io_verificato: bool = False,
        numero_patente: str = "",
        scadenza_patente: str = "",
        app_io_certificato_id: str = "",
        # old name compatibility:
        monteOreTotale: int | None = None,
        **kwargs
    ):
        cf = cod_fiscale if cod_fiscale is not None else codFiscale
        dn = dataNascita if dataNascita else (data_nascita if data_nascita else (nascita if nascita else ""))
        comitato = comitato_appartenenza or kwargs.get("compagnia_appartenenza", "")
        super().__init__(
            cod_fiscale=cf,
            nome=nome,
            cognome=cognome,
            email=email,
            data_nascita=dn,
            ruolo=ruolo,
            telefono=telefono,
            comitato_appartenenza=comitato
        )

        self.password = password
        # Supporta il vecchio nome monteOreTotale per retrocompatibilità con il DB JSON
        self.oreServizio = monteOreTotale if monteOreTotale is not None else oreServizio
        self.patenti = patenti if patenti is not None else []
        self.qualifiche = qualifiche if qualifiche is not None else []
        self.disponibilita = disponibilita if disponibilita is not None else []
        self.patenti_pdf: dict[str, str] = patenti_pdf if patenti_pdf is not None else kwargs.get("patenti_pdf", {})
        self.patente_pdf_path: str = patente_pdf_path if patente_pdf_path else kwargs.get("patente_pdf_path", "")
        self.app_io_verificato: bool = app_io_verificato or kwargs.get("app_io_verificato", False)
        self.numero_patente: str = numero_patente or kwargs.get("numero_patente", "")
        self.data_rilascio_patente: str = str(kwargs.get("data_rilascio_patente") or kwargs.get("data_rilascio", "")).strip()
        self.scadenza_patente: str = scadenza_patente or kwargs.get("scadenza_patente", "")
        self.app_io_certificato_id: str = app_io_certificato_id or kwargs.get("app_io_certificato_id", "")
        self.punti_patente: int = int(kwargs.get("punti_patente", 30))

        self.curriculum = curriculum
        self.formazione = formazione if formazione is not None else []
        self.referente: Optional[Referente] = None
        self.turni_assegnati: List[Turno] = []
        self.corsi_frequentati: List[Corso] = []
        self.ore_lavorate: dict[str, float] = {}

    def aggiornaProfilo(self, v: Volontario) -> bool:
        """Sincronizza le informazioni del profilo a partire da un'altra istanza Volontario (UML)."""
        self.nome = v.nome
        self.cognome = v.cognome
        self.email = v.email
        self.data_nascita = v.data_nascita
        self.telefono = v.telefono
        self.ruolo = v.ruolo
        self.password = v.password
        self.oreServizio = v.oreServizio
        self.patenti = v.patenti
        self.qualifiche = v.qualifiche
        self.disponibilita = v.disponibilita
        return True

    @property
    def codiceFiscale(self) -> str:
        return self.cod_fiscale

    @codiceFiscale.setter
    def codiceFiscale(self, val: str):
        self.cod_fiscale = val

    def possiedePatenteValida(self, tipo: str = "") -> bool:
        """Verifica se il volontario possiede una patente valida non scaduta (UML PrenotaTurno)."""
        if not tipo:
            return len(self.patenti) > 0
        for p in self.patenti:
            if isinstance(p, str) and p.strip().upper() == tipo.strip().upper():
                return True
            elif hasattr(p, "tipo") and str(p.tipo).strip().upper() == tipo.strip().upper():
                if hasattr(p, "isScaduta") and not p.isScaduta():
                    return True
        return False

    def aggiungiOreServizio(self, ore: int) -> None:
        """Incrementa il monte ore di servizio certificato svolto dal volontario (UML)."""
        self.oreServizio += ore

    def aggiungiPatente(self, patente: str) -> None:
        """Registra una patente di guida nell'elenco del soccorritore (UML)."""
        if patente not in self.patenti:
            self.patenti.append(patente)

    def aggiungiQualifica(self, qualifica: str) -> None:
        """Aggiunge una certificazione o brevetto sanitario al profilo del volontario (UML)."""
        if qualifica not in self.qualifiche:
            self.qualifiche.append(qualifica)

    def getMonteOre(self) -> int:
        """Restituisce il totale cumulato delle ore di volontariato prestate (UML)."""
        return self.oreServizio

    def verificaCredenziali(self, email: str, password: str) -> bool:
        """Verifica la corrispondenza delle credenziali di accesso (UML)."""
        return self.email == email and self.password == password

    def aggiorna_db(self) -> bool:
        """Salva lo stato corrente del profilo volontario nel database locale JSON."""
        from GestioneUtenteController import GestioneUtenteController
        controller = GestioneUtenteController()
        return controller.modificaProfilo(self)

    def aggiorna_firestore(self) -> bool:
        """Salva lo stato nel database locale JSON."""
        return self.aggiorna_db()

    def aggiorna_email(self, nuova_email: str) -> bool:
        self.email = nuova_email
        from GestioneUtenteController import GestioneUtenteController
        controller = GestioneUtenteController()
        return controller.modificaProfilo(self)

    def prenotaTurno(self, turno: Turno | str) -> bool:
        """Prenota un turno di servizio (UML)."""
        if isinstance(turno, str):
            for t in self.turni_assegnati:
                if t.codice == turno:
                    return True
            from Turno import Turno
            t_obj = Turno(codice=turno)
            self.turni_assegnati.append(t_obj)
            return True
        elif turno and turno not in self.turni_assegnati:
            self.turni_assegnati.append(turno)
            return True
        return False

    def annullaPrenotazione(self, turno: Turno | str) -> bool:
        """Annulla la prenotazione a un turno di servizio (UML)."""
        if isinstance(turno, str):
            to_remove = [t for t in self.turni_assegnati if t.codice == turno]
            for t in to_remove:
                self.turni_assegnati.remove(t)
            return True
        elif turno in self.turni_assegnati:
            self.turni_assegnati.remove(turno)
            return True
        return False

    def iscriviti_al_corso(self, corso: Corso) -> bool:
        """Iscrive il volontario a un corso di formazione."""
        if corso not in self.formazione:
            self.formazione.append(corso)
        if hasattr(corso, "aggiungiPartecipante"):
            corso.aggiungiPartecipante(self)
        return True

    def disiscriviti_dal_corso(self, corso: Corso) -> bool:
        """Annulla l'iscrizione del volontario a un corso."""
        if corso in self.formazione:
            self.formazione.remove(corso)
        if hasattr(corso, "rimuoviPartecipante"):
            corso.rimuoviPartecipante(self)
        return True

    def compila_report_turno(self, turno: Turno, ore_lavorate: float):
        self.ore_lavorate[turno.codice] = ore_lavorate
        self.aggiungiOreServizio(int(ore_lavorate))
        print(f"{self.nome} ha registrato {ore_lavorate} ore per il turno del {turno.data}")

    def getTurniAssegnati(self) -> List[Turno]:
        """Restituisce l'elenco dei turni di servizio assegnati al volontario (UML)."""
        return list(self.turni_assegnati)

    def visualizza_turni_scelti(self):
        if not self.turni_assegnati:
            print(f"{self.nome} non ha turni assegnati.")
            return
        print(f"Turni assegnati a {self.nome}:")
        for turno in self.turni_assegnati:
            print(f" • {turno.data} ({turno.fascia_oraria}) in {turno.luogo}")

    def visualizza_rubrica(self, colleghi: List[Volontario]):
        if not colleghi:
            print("Rubrica vuota.")
            return
        print("Rubrica volontari:")
        for volontario in colleghi:
            print(f" • {volontario.getNomeCompleto()} | Email: {volontario.email} | Tel: {volontario.telefono}")

    def apri_modifica_dati(self):
        from layout.modifica_dati_dialog import ModificaDatiDialog
        dialog = ModificaDatiDialog(self)
        dialog.exec_()

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "monteOreTotale": self.oreServizio,
            "patenti": self.patenti,
            "qualifiche": self.qualifiche,
            "disponibilita": self.disponibilita,
            "curriculum": self.curriculum,
            "comitato_appartenenza": self.comitato_appartenenza,
            "patenti_pdf": getattr(self, "patenti_pdf", {}),
            "patente_pdf_path": getattr(self, "patente_pdf_path", ""),
            "app_io_verificato": getattr(self, "app_io_verificato", False),
            "numero_patente": getattr(self, "numero_patente", ""),
            "data_rilascio_patente": getattr(self, "data_rilascio_patente", ""),
            "scadenza_patente": getattr(self, "scadenza_patente", ""),
            "punti_patente": getattr(self, "punti_patente", 30),
            "app_io_certificato_id": getattr(self, "app_io_certificato_id", ""),
            "corsi_frequentati_ids": [str(c.id) for c in getattr(self, "corsi_frequentati", []) if getattr(c, "id", None)],
            "formazione_ids": [str(c.id) for c in getattr(self, "formazione", []) if getattr(c, "id", None)]
        })
        return d
