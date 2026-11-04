"""Test di Account e Patenti (RF1-RF8, NF2-NF4)."""
import unittest
from datetime import date
from tests.base import TestBase
from utenti.patente import Patente
from utenti.referente import Referente
from utenti.utente import Utente
from utenti.volontario import Volontario
from dati.gestore_dati import GestoreDati


class TestAccount(TestBase):
    def test_email_gia_usata(self):
        self.nuovo_volontario("mario@cri.it")
        v2 = Volontario()
        ok_vol = v2.inserisciInformazioni("Luigi", "Verdi", "VRDLGU80A01H501U",
                                          "mario@cri.it", "3339998877",
                                          "Comitato di Ancona", "pass123")
        self.assertFalse(ok_vol, "La registrazione del Volontario deve fallire se l'email è già in uso.")

        # Verifica anche per il Referente con email già usata
        dati = GestoreDati().carica()
        dati["codici_autorizzazione"].add("REF_TEST")
        GestoreDati().salva(dati)

        r2 = Referente()
        ok_ref = r2.inserisciInformazioni("Sanitario", "mario@cri.it", "3331112233",
                                          "Comitato di Ancona", "pass123", "REF_TEST")
        self.assertFalse(ok_ref, "La registrazione del Referente deve fallire se l'email è già in uso.")


    def test_password_troppo_corta(self):
        v = Volontario()
        ok = v.inserisciInformazioni("Luigi", "Verdi", "VRDLGU80A01H501U",
                                     "luigi@cri.it", "3339998877",
                                     "Comitato di Ancona", "12345")
        self.assertFalse(ok)

    def test_referente_con_codice_valido_e_non_valido(self):
        dati = GestoreDati().carica()
        dati["codici_autorizzazione"].add("REF2026")
        GestoreDati().salva(dati)

        r_err = Referente()
        ok_err = r_err.inserisciInformazioni("Sanitario", "ref_err@cri.it", "3331112233",
                                             "Comitato di Ancona", "secret123", "CODICE_ERRATO")
        self.assertFalse(ok_err)

        r_ok = Referente()
        ok = r_ok.inserisciInformazioni("Sanitario", "ref_ok@cri.it", "3331112233",
                                        "Comitato di Ancona", "secret123", "REF2026")
        self.assertTrue(ok)
        self.assertEqual(r_ok.getDati()["settoreGestito"], "Sanitario")

    def test_login(self):
        self.nuovo_volontario("mario@cri.it")
        # Utente generico chiama inserisciCredenziali
        u = Volontario().inserisciCredenziali("mario@cri.it", "abc123")
        self.assertIsNotNone(u)
        self.assertEqual(u.getEmail(), "mario@cri.it")

        u_err = Volontario().inserisciCredenziali("mario@cri.it", "pass_sbagliata")
        self.assertIsNone(u_err)

    def test_recupero_credenziali(self):
        v = self.nuovo_volontario("mario@cri.it")
        ok_non_reg = v.inserisciEmail("non_registrato@cri.it")
        self.assertFalse(ok_non_reg)

        ok = v.inserisciEmail("mario@cri.it")
        self.assertTrue(ok)
        self.assertEqual(len(self.email), 1)
        self.assertEqual(self.email[0][0], "mario@cri.it")
        self.assertIn("Recupero password", self.email[0][1])

    def test_modifica_dati_con_email_di_un_altro(self):
        v1 = self.nuovo_volontario("mario@cri.it")
        v2 = self.nuovo_volontario("luigi@cri.it", cf="VRDLGU80A01H501U")

        # Modifica con email già usata da v1
        ok = v2.modificaDati("mario@cri.it", "3330001122", "nuovapass123")
        self.assertFalse(ok)

        # Modifica valida
        ok_valido = v2.modificaDati("luigi_nuovo@cri.it", "3330001122", "nuovapass123")
        self.assertTrue(ok_valido)
        self.assertEqual(v2.getEmail(), "luigi_nuovo@cri.it")

    def test_elimina_account_libera_i_posti(self):
        v = self.nuovo_volontario()
        t = self.nuovo_turno(posti=3)
        from attivita.prenotazione import Prenotazione
        p = Prenotazione()
        p.prenotaTurno(t, v)
        self.assertEqual(t.getDati()["postiLiberi"], 2)

        v.eliminaAccount()
        self.assertEqual(t.getDati()["postiLiberi"], 3)
        dati = GestoreDati().carica()
        self.assertNotIn("mario@cri.it", dati["utenti"])


class TestPatenti(TestBase):
    def test_inserimento_modifica_rimozione(self):
        v = self.nuovo_volontario()
        p = Patente()
        # Inserisci patente
        self.assertTrue(p.inserisciPatente("P100"))
        p.inserisciDatiPatente("P100", "CRI 5", date(2028, 1, 1), v)
        self.assertEqual(len(v.visualizzaPatenti()), 1)

        # Modifica patente
        dati_p = p.modificaPatente("P100", v)
        self.assertEqual(dati_p["codice"], "P100")
        p.inserisciModifiche(v.visualizzaPatenti()[0], date(2029, 1, 1))
        self.assertEqual(v.visualizzaPatenti()[0].getDati()["dataScadenza"], date(2029, 1, 1))

        # Elimina patente
        ok_eliminata = p.eliminaPatente("P100", v)
        self.assertTrue(ok_eliminata)
        self.assertEqual(len(v.visualizzaPatenti()), 0)

    def test_patente_di_un_altro_volontario_non_modificabile(self):
        v1 = self.nuovo_volontario("mario@cri.it")
        v2 = self.nuovo_volontario("luigi@cri.it", cf="VRDLGU80A01H501U")
        p = Patente()
        p.inserisciDatiPatente("P100", "CRI 5", date(2028, 1, 1), v1)

        # v2 prova a modificare o rimuovere la patente di v1
        dati_modifica = p.modificaPatente("P100", v2)
        self.assertEqual(dati_modifica, {})

        eliminata = p.eliminaPatente("P100", v2)
        self.assertFalse(eliminata)

    def test_validita(self):
        p = Patente()
        v = self.nuovo_volontario()
        p.inserisciDatiPatente("P100", "CRI 5", date(2026, 11, 5), v)
        self.assertTrue(p.verificaValidita(date(2026, 11, 4)))
        self.assertTrue(p.verificaValidita(date(2026, 11, 5)))
        self.assertFalse(p.verificaValidita(date(2026, 11, 6)))


if __name__ == "__main__":
    unittest.main()
