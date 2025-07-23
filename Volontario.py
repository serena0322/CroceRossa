from __future__ import annotations  # risolve i tipi circolari

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from Referente import Referente
    from Corso import Corso
    from Turno import Turno

class Volontario:
    def __init__(
        self,
        cod_fiscale: int,
        nome: str,
        cognome: str,
        email: str,
        nascita: str,
        telefono: str,
        curriculum: str,
        patenti: list,
        formazione: list[Corso],
        compagnia_appartenenza: str,
        disponibilita: list,
        ruolo: str
    ):
        self.cod_fiscale = cod_fiscale
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.nascita = nascita
        self.telefono = telefono
        self.curriculum = curriculum
        self.patenti = patenti
        self.formazione = formazione
        self.compagnia_appartenenza = compagnia_appartenenza
        self.disponibilita = disponibilita
        self.ruolo = ruolo
        self.referente: Optional[Referente] = None
        self.turni_assegnati: list[Turno] = []
        self.corsi_frequentati: list[Corso] = []
        self.ore_lavorate: dict[int, float] = {}  # id_turno -> ore

    def iscriviti_al_corso(self, corso: Corso):
        if corso not in self.formazione:
            self.formazione.append(corso)
            print(f"{self.nome} iscritto al corso {corso.nome}")

    def disiscriviti_dal_corso(self, corso: Corso):
        if corso in self.formazione:
            self.formazione.remove(corso)
            print(f"{self.nome} disiscritto dal corso {corso.nome}")

    def prenota_turno(self, turno: Turno):
        if turno not in self.turni_assegnati:
            self.turni_assegnati.append(turno)
            print(f"{self.nome} ha prenotato il turno del {turno.data}")

    def annulla_turno(self, turno: Turno):
        if turno in self.turni_assegnati:
            self.turni_assegnati.remove(turno)
            print(f"{self.nome} ha annullato il turno del {turno.data}")

    def compila_report_turno(self, turno: Turno, ore_lavorate: float):
        self.ore_lavorate[turno.id_turno] = ore_lavorate
        print(f"{self.nome} ha registrato {ore_lavorate} ore per il turno del {turno.data}")

    def calcola_ore_totali(self) -> float:
        return sum(self.ore_lavorate.values())

    def è_disponibile(self, giorno: str) -> bool:
        return giorno in self.disponibilità
