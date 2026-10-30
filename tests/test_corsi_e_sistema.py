"""Test di Corsi, Iscrizioni, Statistiche e Backup (RF21-RF35)."""
import os
import unittest
from datetime import date, datetime, timedelta
from tests.base import TestBase
from attivita.corso import Corso
from attivita.iscrizione import Iscrizione
from attivita.stato_attivita import StatoAttivita
from dati.gestore_dati import GestoreDati
from dati.gestore_backup import GestoreBackup
from statistiche.gestore_statistiche import GestoreStatistiche


class TestCorsi(TestBase):
    def test_iscrizione_e_doppia_iscrizione(self):
        c = Corso()
        c.inserisciDatiCorso("C1", "Primo Soccorso", "Descrizione", "Mario Rossi",
                             "Base", date(2026, 11, 10), date(2026, 11, 15),
                             "18:00 - 20:00", "Sede", 2)
        v = self.nuovo_volontario()

        # Prima iscrizione
        self.assertTrue(Iscrizione().iscriviCorso(c, v))
        self.assertEqual(c.getDati()["postiLiberi"], 1)
        self.assertEqual(len(v.visualizzaIscrizioni()), 1)

        # Doppia iscrizione rifiutata
        self.assertFalse(Iscrizione().iscriviCorso(c, v))
        self.assertEqual(c.getDati()["postiLiberi"], 1)

    def test_annullamento_entro_due_giorni_negato(self):
        c = Corso()
        c.inserisciDatiCorso("C1", "Primo Soccorso", "Descrizione", "Mario Rossi",
                             "Base", date(2026, 11, 4), date(2026, 11, 5),
                             "18:00 - 20:00", "Sede", 5)
        v = self.nuovo_volontario()
        i = Iscrizione()
        i.iscriviCorso(c, v)
        self.assertEqual(c.getDati()["postiLiberi"], 4)

        # ORA_FINTA è 2026-11-02: mancano esattamente 2 giorni (4 nov - 2 nov = 2 <= 2 giorni)
        # L'annullamento entro 2 giorni deve essere negato
        self.assertFalse(v.annullaIscrizione(i))
        self.assertEqual(c.getDati()["postiLiberi"], 4)

        # Se il corso iniziasse tra 3 giorni (5 nov), l'annullamento al 2 nov deve essere consentito
        c2 = Corso()
        c2.inserisciDatiCorso("C2", "Corso Avanzato", "Descrizione", "Mario Rossi",
                              "Base", date(2026, 11, 5), date(2026, 11, 6),
                              "18:00 - 20:00", "Sede", 5)
        i2 = Iscrizione()
        i2.iscriviCorso(c2, v)
        self.assertTrue(v.annullaIscrizione(i2))
        self.assertEqual(c2.getDati()["postiLiberi"], 5)

    def test_stato_e_attestazione(self):
        c = Corso()
        c.inserisciDatiCorso("C1", "BLSD", "Descrizione", "Direttore",
                             "Sanitario", date(2026, 11, 3), date(2026, 11, 4),
                             "09:00 - 13:00", "Sede", 10)
        v = self.nuovo_volontario()
        i = Iscrizione()
        i.iscriviCorso(c, v)

        # Non ancora concluso -> attestaPartecipazione restituisce lista vuota
        self.assertEqual(Corso().attestaPartecipazione(c), [])

        # Avanza data oltre dataFine (5 nov) e aggiorna stato corsi
        self.vai_a(datetime(2026, 11, 5, 10, 0))
        Corso().aggiornaStatoCorsi()
        self.assertEqual(c.getStato(), StatoAttivita.CONCLUSO)

        # Ora concluso -> attestaPartecipazione restituisce la lista degli iscritti
        iscritti = Corso().attestaPartecipazione(c)
        self.assertEqual(len(iscritti), 1)
        self.assertIs(iscritti[0], v)

        # Seleziona superati
        Corso().selezionaSuperati(c, [v])
        self.assertTrue(i.getSuperato())
        # Carriera del volontario mostra il corso superato
        self.assertIn("BLSD", v.visualizzaCarriera()["corsiSuperati"])

    def test_statistiche_corsi_tramite_interfaccia(self):
        c = Corso()
        c.inserisciDatiCorso("C1", "TSSA", "Descrizione", "Direttore",
                             "Soccorso", date(2026, 11, 3), date(2026, 11, 4),
                             "09:00 - 13:00", "Sede", 10)
        v = self.nuovo_volontario()
        i = Iscrizione()
        i.iscriviCorso(c, v)

        # Sposta a corso concluso e superato
        self.vai_a(datetime(2026, 11, 5, 10, 0))
        Corso().aggiornaStatoCorsi()
        Corso().selezionaSuperati(c, [v])

        stats = GestoreStatistiche().gestisciStatistiche("corsi")
        self.assertIn("perStato", stats)
        self.assertEqual(stats["iscrizioniTotali"], 1)
        self.assertEqual(stats["percentualeSuperati"]["TSSA"], 100.0)


class TestBackup(TestBase):
    def test_backup_crea_il_file_del_giorno(self):
        self.nuovo_volontario()
        backup_manager = GestoreBackup()
        backup_dir = f"{self.cartella}/backup_test"
        backup_manager._GestoreBackup__percorsoBackup = backup_dir

        backup_manager.effettuaBackup()
        giorno_str = f"{self.ora:%Y%m%d}"
        file_atteso = os.path.join(backup_dir, f"dati_{giorno_str}.pickle")
        self.assertTrue(os.path.isfile(file_atteso))


if __name__ == "__main__":
    unittest.main()
