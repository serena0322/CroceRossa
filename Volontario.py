from __future__ import annotations
from Utente import Utente
from typing import Optional, TYPE_CHECKING

from layout.modifica_dati_dialog import ModificaDatiDialog
from layout.ruolo_dialog import RuoloDialog

if TYPE_CHECKING:
    from Referente import Referente
    from Corso import Corso
    from Turno import Turno

class Volontario(Utente):
    def __init__(
        self,
        cod_fiscale: int,
        nome: str,
        cognome: str,
        email: str,
        nascita: str,
        telefono: str,
        ruolo: str = "volontario",
        curriculum: str = "",
        patenti: list[str] = [],
        formazione: list[Corso] = [],
        compagnia_appartenenza: str = "",
        disponibilita: list[str] = []
    ):
        super().__init__(cod_fiscale, nome, cognome, email, nascita, telefono, ruolo)
        self.curriculum = curriculum
        self.patenti = patenti
        self.formazione = formazione
        self.compagnia_appartenenza = compagnia_appartenenza
        self.disponibilita = disponibilita
        self.referente: Optional[Referente] = None
        self.turni_assegnati: list[Turno] = []
        self.corsi_frequentati: list[Corso] = []
        self.ore_lavorate: dict[int, float] = {}

    def iscriviti_al_corso(self, corso: Corso):
        if corso not in self.formazione:
            self.formazione.append(corso)
            print(f"{self.nome} iscritto al corso {corso.nome}")

    def disiscriviti_dal_corso(self, corso: Corso):
        if corso in self.formazione:
            self.formazione.remove(corso)
            print(f"{self.nome} disiscritto dal corso {corso.nome}")

    def prenota_turno(self, turno: Turno, parent=None):
        ruoli_disponibili = []
        for ruolo, numero in turno.persone_richieste.items():
            attuali = turno.persone_prenotate.get(ruolo, [])
            if len(attuali) < numero:
                if ruolo == "autista" and not self.patenti:
                    continue
                ruoli_disponibili.append(ruolo)

        if not ruoli_disponibili:
            print(f"❌ Nessun ruolo disponibile per il turno del {turno.data}")
            return

        def ruolo_selezionato(ruolo_scelto):
            turno.persone_prenotate.setdefault(ruolo_scelto, []).append(self.cod_fiscale)
            self.turni_assegnati.append(turno)
            print(f"✅ {self.nome} prenotato come {ruolo_scelto} per il turno del {turno.data}")

        dialog = RuoloDialog(ruoli_disponibili, ruolo_selezionato)
        dialog.exec_()

    def annulla_prenotazione(self, turno: Turno):
        if turno in self.turni_assegnati:
            self.turni_assegnati.remove(turno)
            print(f"{self.nome} ha annullato il turno del {turno.data}")

    def compila_report_turno(self, turno: Turno, ore_lavorate: float):
        self.ore_lavorate[turno.id_turno] = ore_lavorate
        print(f"{self.nome} ha registrato {ore_lavorate} ore per il turno del {turno.data}")

    def calcola_ore_totali(self) -> float:
        return sum(self.ore_lavorate.values())

    def disponibilita(self, giorno: str) -> bool:
        return giorno in self.disponibilita

    def visualizza_turni_scelti(self):
        if not self.turni_assegnati:
            print(f"{self.nome} non ha turni assegnati.")
            return
        print(f"📅 Turni assegnati a {self.nome}:")
        for turno in self.turni_assegnati:
            print(f" - {turno.data} ({turno.orario}) in {turno.sede}")


    def visualizza_rubrica(self, colleghi: list[Volontario]):
        if not colleghi:
            print("Rubrica vuota.")
            return
        print("📘 Rubrica volontari:")
        for volontario in colleghi:
            print(f" - {volontario.get_nome_completo()} | 📧 {volontario.email} | 📞 {volontario.telefono}")

    def apri_modifica_dati(self):
        dialog = ModificaDatiDialog(self.volontario)
        dialog.exec_()