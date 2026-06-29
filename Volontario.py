from __future__ import annotations
from Utente import Utente
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from Referente import Referente
    from Corso import Corso
    from Turno import Turno

class Volontario(Utente):
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
        monteOreTotale: int = 0,
        patenti: List[str] | None = None,
        qualifiche: List[str] | None = None,
        disponibilita: List[str] | None = None,
        # compatibility arguments:
        cod_fiscale: int | None = None,
        nascita: str | None = None,
        data_nascita: str | None = None,
        curriculum: str = "",
        formazione: List[Corso] | None = None,
        compagnia_appartenenza: str = ""
    ):
        cf = str(cod_fiscale) if cod_fiscale is not None else codFiscale
        dn = dataNascita if dataNascita else (data_nascita if data_nascita else (nascita if nascita else ""))
        super().__init__(
            cod_fiscale=cf,
            nome=nome,
            cognome=cognome,
            email=email,
            data_nascita=dn,
            ruolo=ruolo,
            telefono=telefono
        )
        
        self.password = password
        self.monteOreTotale = monteOreTotale
        self.patenti = patenti if patenti is not None else []
        self.qualifiche = qualifiche if qualifiche is not None else []
        self.disponibilita = disponibilita if disponibilita is not None else []
        
        # Compatibility properties:
        self.curriculum = curriculum
        self.formazione = formazione if formazione is not None else []
        self.compagnia_appartenenza = compagnia_appartenenza
        self.referente: Optional[Referente] = None
        self.turni_assegnati: List[Turno] = []
        self.corsi_frequentati: List[Corso] = []
        self.ore_lavorate: dict[int, float] = {}

    @property
    def codFiscale(self) -> str:
        return self.cod_fiscale
        
    @codFiscale.setter
    def codFiscale(self, val: str):
        self.cod_fiscale = val

    @property
    def dataNascita(self) -> str:
        return self.data_nascita
        
    @dataNascita.setter
    def dataNascita(self, val: str):
        self.data_nascita = val

    def aggiornaProfilo(self, v: Volontario) -> bool:
        self.nome = v.nome
        self.cognome = v.cognome
        self.email = v.email
        self.dataNascita = v.dataNascita
        self.telefono = v.telefono
        self.ruolo = v.ruolo
        self.password = v.password
        self.monteOreTotale = v.monteOreTotale
        self.patenti = v.patenti
        self.qualifiche = v.qualifiche
        self.disponibilita = v.disponibilita
        return True

    def aggiungiOreServizio(self, ore: int) -> None:
        self.monteOreTotale += ore

    def aggiungiPatente(self, patente: str) -> None:
        if patente not in self.patenti:
            self.patenti.append(patente)

    def aggiungiQualifica(self, qualifica: str) -> None:
        if qualifica not in self.qualifiche:
            self.qualifiche.append(qualifica)

    def getMonteOre(self) -> int:
        return self.monteOreTotale

    def verificaCredenziali(self, email: str, password: str) -> bool:
        return self.email == email and self.password == password

    # Compatibility methods:
    def aggiorna_firestore(self) -> bool:
        from GestioneUtenteController import GestioneUtenteController
        controller = GestioneUtenteController()
        return controller.modificaProfilo(self)

    def aggiorna_email(self, nuova_email: str) -> bool:
        self.email = nuova_email
        from GestioneUtenteController import GestioneUtenteController
        controller = GestioneUtenteController()
        return controller.modificaProfilo(self)

    def iscriviti_al_corso(self, corso: Corso):
        if corso not in self.formazione:
            self.formazione.append(corso)
            print(f"{self.nome} iscritto al corso {corso.nome}")

    def disiscriviti_dal_corso(self, corso: Corso):
        if corso in self.formazione:
            self.formazione.remove(corso)
            print(f"{self.nome} disiscritto dal corso {corso.nome}")

    def prenota_turno(self, turno: Turno, parent=None):
        if turno not in self.turni_assegnati:
            self.turni_assegnati.append(turno)

    def annulla_prenotazione(self, turno: Turno):
        if turno in self.turni_assegnati:
            self.turni_assegnati.remove(turno)

    def compila_report_turno(self, turno: Turno, ore_lavorate: float):
        self.ore_lavorate[turno.id_turno] = ore_lavorate
        self.aggiungiOreServizio(int(ore_lavorate))
        print(f"{self.nome} ha registrato {ore_lavorate} ore per il turno del {turno.data}")

    def calcola_ore_totali(self) -> float:
        return float(self.monteOreTotale)

    def has_disponibilita(self, giorno: str) -> bool:
        return giorno in self.disponibilita

    def visualizza_turni_scelti(self):
        if not self.turni_assegnati:
            print(f"{self.nome} non ha turni assegnati.")
            return
        print(f"📅 Turni assegnati a {self.nome}:")
        for turno in self.turni_assegnati:
            print(f" - {turno.data} ({turno.fascia_oraria}) in {turno.luogo}")

    def visualizza_rubrica(self, colleghi: List[Volontario]):
        if not colleghi:
            print("Rubrica vuota.")
            return
        print("📘 Rubrica volontari:")
        for volontario in colleghi:
            print(f" - {volontario.get_nome_completo()} | 📧 {volontario.email} | 📞 {volontario.telefono}")

    def apri_modifica_dati(self):
        from layout.modifica_dati_dialog import ModificaDatiDialog
        dialog = ModificaDatiDialog(self)
        dialog.exec_()

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "monteOreTotale": self.monteOreTotale,
            "patenti": self.patenti,
            "qualifiche": self.qualifiche,
            "disponibilita": self.disponibilita,
            "curriculum": self.curriculum,
            "compagnia_appartenenza": self.compagnia_appartenenza
        })
        return d
