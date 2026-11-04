"""Base comune a tutti i test: file pickle temporaneo, ora finta, e-mail intercettate."""
import shutil
import tempfile
import unittest
from datetime import date, datetime, time
from unittest import mock

import dati.gestore_dati as gestore_dati
from attivita.turno import Turno
from utenti.volontario import Volontario

ORA_FINTA = datetime(2026, 11, 2, 9, 0)  

class TestBase(unittest.TestCase):
    def setUp(self):
        self.cartella = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.cartella)

        patch_file = mock.patch.object(gestore_dati, "PERCORSO_FILE",
                                       f"{self.cartella}/dati.pickle")
        patch_file.start()
        self.addCleanup(patch_file.stop)
        gestore_dati._dati = None
        self.addCleanup(setattr, gestore_dati, "_dati", None)

        self.ora = ORA_FINTA
        patch_ora = mock.patch("supporto.orologio.adesso", side_effect=lambda: self.ora)
        patch_ora.start()
        self.addCleanup(patch_ora.stop)

        self.email = []
        patch_posta = mock.patch("supporto.posta.invia",
                                 side_effect=lambda a, o, t: self.email.append((a, o, t)))
        patch_posta.start()
        self.addCleanup(patch_posta.stop)

    def vai_a(self, istante: datetime) -> None:
        self.ora = istante

    # dati di prova
    def nuovo_volontario(self, email="mario@cri.it", cf="RSSMRA80A01H501U") -> Volontario:
        v = Volontario()
        ok = v.inserisciInformazioni("Mario", "Rossi", cf, email, "3331234567",
                                     "Comitato di Ancona", "abc123")
        self.assertTrue(ok)
        return v

    def nuovo_turno(self, codice="T1", giorno=date(2026, 11, 5), inizio=time(8, 0),
                    fine=time(12, 0), posti=3, patente="") -> Turno:
        t = Turno()
        t.inserisciDatiTurno(codice, "", giorno, inizio, fine, "Ancona", "Trasporto",
                             posti, patente, "", "Ambulanza 1", "")
        return t
