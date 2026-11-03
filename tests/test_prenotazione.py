"""Test di PrenotaTurno (RF18, NF6) e AnnullaPrenotazione (RF20)."""
import unittest
from datetime import date, datetime, time
from attivita.prenotazione import Prenotazione
from tests.base import TestBase
from utenti.patente import Patente

class TestPrenotaTurno(TestBase):
    def test_prenotazione_registrata_e_posti_aggiornati(self):
        v, t = self.nuovo_volontario(), self.nuovo_turno(posti=3)
        self.assertEqual(Prenotazione().prenotaTurno(t, v), "")
        self.assertEqual(t.getDati()["postiLiberi"], 2)
        self.assertEqual(len(v.visualizzaPrenotazioni()), 1)

    def test_gia_prenotato_allo_stesso_turno(self):
        v, t = self.nuovo_volontario(), self.nuovo_turno()
        Prenotazione().prenotaTurno(t, v)
        self.assertIn("gia' prenotato", Prenotazione().prenotaTurno(t, v))
        self.assertEqual(t.getDati()["postiLiberi"], 2)

    def test_turni_sovrapposti(self):
        v = self.nuovo_volontario()
        t1 = self.nuovo_turno("T1", inizio=time(8, 0), fine=time(12, 0))
        t2 = self.nuovo_turno("T2", inizio=time(11, 0), fine=time(14, 0))
        Prenotazione().prenotaTurno(t1, v)
        self.assertIn("sovrappone", Prenotazione().prenotaTurno(t2, v))

    def test_turni_consecutivi_non_sovrapposti(self):
        v = self.nuovo_volontario()
        t1 = self.nuovo_turno("T1", inizio=time(8, 0), fine=time(12, 0))
        t2 = self.nuovo_turno("T2", inizio=time(12, 0), fine=time(14, 0))
        Prenotazione().prenotaTurno(t1, v)
        self.assertEqual(Prenotazione().prenotaTurno(t2, v), "")

    def test_ultimo_posto_riservato_a_chi_ha_la_patente(self):
        t = self.nuovo_turno(posti=2, patente="CRI 5")
        senza1 = self.nuovo_volontario("a@cri.it", "AAAAAA80A01H501U")
        senza2 = self.nuovo_volontario("b@cri.it", "BBBBBB80A01H501U")
        self.assertEqual(Prenotazione().prenotaTurno(t, senza1), "")
        self.assertIn("riservato", Prenotazione().prenotaTurno(t, senza2))

    def test_ultimo_posto_libero_se_la_patente_ce_gia(self):
        t = self.nuovo_turno(posti=2, patente="CRI 5")
        autista = self.nuovo_volontario("a@cri.it", "AAAAAA80A01H501U")
        Patente().inserisciDatiPatente("P1", "CRI 5", date(2027, 1, 1), autista)
        altro = self.nuovo_volontario("b@cri.it", "BBBBBB80A01H501U")
        Prenotazione().prenotaTurno(t, autista)
        self.assertEqual(Prenotazione().prenotaTurno(t, altro), "")

    def test_patente_scaduta_alla_data_del_turno_non_conta(self):
        t = self.nuovo_turno(posti=1, patente="CRI 5", giorno=date(2026, 11, 5))
        v = self.nuovo_volontario()
        Patente().inserisciDatiPatente("P1", "CRI 5", date(2026, 11, 4), v)
        self.assertIn("riservato", Prenotazione().prenotaTurno(t, v))


class TestAnnullaPrenotazione(TestBase):
    def test_annullamento_con_piu_di_24_ore(self):
        v, t = self.nuovo_volontario(), self.nuovo_turno()
        p = Prenotazione()
        p.prenotaTurno(t, v)
        self.assertTrue(v.annullaPrenotazione(p))
        self.assertEqual(t.getDati()["postiLiberi"], 3)
        self.assertEqual(v.visualizzaPrenotazioni(), [])

    def test_annullamento_negato_a_meno_di_24_ore(self):
        v, t = self.nuovo_volontario(), self.nuovo_turno()
        p = Prenotazione()
        p.prenotaTurno(t, v)
        self.vai_a(datetime(2026, 11, 4, 9, 0))
        self.assertFalse(v.annullaPrenotazione(p))
        self.assertEqual(t.getDati()["postiLiberi"], 2)


if __name__ == "__main__":
    unittest.main()
