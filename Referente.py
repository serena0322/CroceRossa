from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from Corso import Corso
    from Volontario import Volontario

# Importazione necessaria per l'esecuzione del codice (non solo per type hinting)
import Volontario as volontario_module

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout

class Referente(volontario_module.Volontario):
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
        area_gestita: str
    ):
        super().__init__(
            cod_fiscale, nome, cognome, email, nascita, telefono,
            curriculum, patenti, formazione, compagnia_appartenenza,
            disponibilita, ruolo="referente"
        )
        self.area_gestita = area_gestita

    def crea_corso(self, nome: str, descrizione: str, durata_ore: int) -> Corso:
        return Corso(nome, descrizione, durata_ore)

    def modifica_corso(self, corso: Corso, nome: str = None, descrizione: str = None, durata_ore: int = None):
        if nome:
            corso.nome = nome
        if descrizione:
            corso.descrizione = descrizione
        if durata_ore:
            corso.durata_ore = durata_ore

    def assegna_corso_a_volontario(self, volontario: Volontario, corso: Corso):
        if corso not in volontario.formazione:
            volontario.formazione.append(corso)

    def attesta_partecipazione(self, volontario: Volontario, corso: Corso):
        if corso not in volontario.corsi_frequentati:
            volontario.corsi_frequentati.append(corso)
