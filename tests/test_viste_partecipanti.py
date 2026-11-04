"""Test di integrazione delle viste VistaIscrittiCorso e VistaPrenotatiTurno."""
import os
import unittest
from datetime import date, time

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PyQt5.QtWidgets import QApplication

from tests.base import TestBase
from attivita.turno import Turno
from attivita.corso import Corso
from attivita.prenotazione import Prenotazione
from attivita.iscrizione import Iscrizione
from viste.gestione_turni.vista_prenotati_turno import VistaPrenotatiTurno
from viste.gestione_corsi.vista_iscritti_corso import VistaIscrittiCorso


class TestVistePartecipanti(TestBase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_vista_prenotati_turno_vuoto(self):
        t = self.nuovo_turno("T_EMPTY", posti=3)
        vista = VistaPrenotatiTurno(t)
        self.assertEqual(vista.tabella.rowCount(), 0)

    def test_vista_prenotati_turno_con_prenotati(self):
        t = self.nuovo_turno("T_PREN", posti=3)
        v1 = self.nuovo_volontario("v1@cri.it", cf="AAAAAA80A01H501U")
        v2 = self.nuovo_volontario("v2@cri.it", cf="BBBBBB80A01H501U")
        Prenotazione().prenotaTurno(t, v1)
        Prenotazione().prenotaTurno(t, v2)

        vista = VistaPrenotatiTurno(t)
        self.assertEqual(vista.tabella.rowCount(), 2)
        # Prima riga
        self.assertEqual(vista.tabella.item(0, 0).text(), "Mario")
        self.assertEqual(vista.tabella.item(0, 1).text(), "Rossi")
        self.assertEqual(vista.tabella.item(0, 2).text(), "v1@cri.it")
        self.assertEqual(vista.tabella.item(0, 3).text(), "3331234567")
        self.assertEqual(vista.tabella.item(0, 4).text(), f"{self.ora:%d/%m/%Y}")
        # Seconda riga
        self.assertEqual(vista.tabella.item(1, 2).text(), "v2@cri.it")

    def test_vista_iscritti_corso_vuoto(self):
        c = Corso()
        c.inserisciDatiCorso("C_EMPTY", "Corso Vuoto", "Desc", "Direttore", "Base",
                             date(2026, 11, 10), date(2026, 11, 15), "18:00", "Sede", 5)
        vista = VistaIscrittiCorso(c)
        self.assertEqual(vista.tabella.rowCount(), 0)

    def test_vista_iscritti_corso_con_iscritti(self):
        c = Corso()
        c.inserisciDatiCorso("C_ISCR", "Corso Base", "Desc", "Direttore", "Base",
                             date(2026, 11, 10), date(2026, 11, 15), "18:00", "Sede", 5)
        v = self.nuovo_volontario("v@cri.it")
        Iscrizione().iscriviCorso(c, v)

        vista = VistaIscrittiCorso(c)
        self.assertEqual(vista.tabella.rowCount(), 1)
        self.assertEqual(vista.tabella.item(0, 0).text(), "Mario")
        self.assertEqual(vista.tabella.item(0, 1).text(), "Rossi")
        self.assertEqual(vista.tabella.item(0, 2).text(), "v@cri.it")
        self.assertEqual(vista.tabella.item(0, 3).text(), "3331234567")
        self.assertEqual(vista.tabella.item(0, 4).text(), f"{self.ora:%d/%m/%Y}")


if __name__ == "__main__":
    unittest.main()

