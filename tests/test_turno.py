"""Test di CUDTurno, Tempo e Persistenza (RF11, RF12, RF32, RF36, NF5)."""
import unittest
from datetime import date, datetime, time, timedelta
from tests.base import TestBase
from attivita.turno import Turno
from attivita.stato_attivita import StatoAttivita
from attivita.prenotazione import Prenotazione
from dati.gestore_dati import GestoreDati


class TestCUDTurno(TestBase):
    def test_inserimento_turno_programmato_con_posti_liberi_pari_ai_totali(self):
        t = self.nuovo_turno("T1", posti=5)
        dati = t.getDati()
        self.assertEqual(dati["stato"], StatoAttivita.PROGRAMMATO)
        self.assertEqual(dati["postiTotali"], 5)
        self.assertEqual(dati["postiLiberi"], 5)
        self.assertIn("T1", GestoreDati().carica()["turni"])

    def test_codice_gia_presente(self):
        self.nuovo_turno("T1")
        self.assertFalse(Turno().inserisciTurno("T1"))

    def test_data_passata_rifiutata(self):
        t = Turno()
        with self.assertRaises(ValueError) as ctx:
            t.inserisciDatiTurno("T_PASSATO", "", date(2026, 11, 1), time(8, 0), time(12, 0),
                                 "Ancona", "Trasporto", 3, "", "", "Ambulanza 1", "")
        self.assertIn("passati", str(ctx.exception))

    def test_fine_prima_di_inizio_rifiutata(self):
        t = Turno()
        with self.assertRaises(ValueError) as ctx:
            t.inserisciDatiTurno("T_ERR", "", date(2026, 11, 5), time(12, 0), time(8, 0),
                                 "Ancona", "Trasporto", 3, "", "", "Ambulanza 1", "")
        self.assertIn("successivo", str(ctx.exception))

    def test_posti_non_positivi_rifiutati(self):
        t = Turno()
        with self.assertRaises(ValueError) as ctx:
            t.inserisciDatiTurno("T_ERR_POSTI", "", date(2026, 11, 5), time(8, 0), time(12, 0),
                                 "Ancona", "Trasporto", 0, "", "", "Ambulanza 1", "")
        self.assertIn("positivo", str(ctx.exception))

    def test_modifica_con_posti_inferiori_ai_prenotati(self):
        t = self.nuovo_turno("T1", posti=3)
        v1 = self.nuovo_volontario("v1@cri.it", cf="AAAAAA80A01H501U")
        v2 = self.nuovo_volontario("v2@cri.it", cf="BBBBBB80A01H501U")
        Prenotazione().prenotaTurno(t, v1)
        Prenotazione().prenotaTurno(t, v2)
        self.assertEqual(len(t.getPrenotazioni()), 2)

        # Modifica con postiTotali = 1 (< 2 prenotati)
        ok = Turno().inserisciModifiche(t, "", date(2026, 11, 5), time(8, 0), time(12, 0),
                                        "Ancona", "Trasporto", 1, "", "", "Mezzo", "")
        self.assertFalse(ok)

    def test_modifica_ricalcola_posti_e_avvisa_i_prenotati(self):
        t = self.nuovo_turno("T1", posti=3)
        v = self.nuovo_volontario("v@cri.it")
        Prenotazione().prenotaTurno(t, v)
        self.assertEqual(t.getDati()["postiLiberi"], 2)
        self.email.clear()

        ok = Turno().inserisciModifiche(t, "", date(2026, 11, 6), time(9, 0), time(13, 0),
                                        "Ancona", "Emergenza", 4, "", "", "Ambulanza 2", "")
        self.assertTrue(ok)
        self.assertEqual(t.getDati()["postiTotali"], 4)
        self.assertEqual(t.getDati()["postiLiberi"], 3)  # 4 - 1
        self.assertEqual(len(self.email), 1)
        self.assertIn("modificato", self.email[0][1])

    def test_rimozione_avvisa_e_toglie_le_prenotazioni(self):
        t = self.nuovo_turno("T1", posti=3)
        v = self.nuovo_volontario("v@cri.it")
        Prenotazione().prenotaTurno(t, v)
        self.email.clear()

        ok = Turno().rimuoviTurno("T1")
        self.assertTrue(ok)
        self.assertNotIn("T1", GestoreDati().carica()["turni"])
        self.assertEqual(len(v.visualizzaPrenotazioni()), 0)
        self.assertEqual(len(self.email), 1)
        self.assertIn("eliminato", self.email[0][1])

    def test_turno_in_corso_non_rimovibile(self):
        # turno non ancora iniziato
        self.vai_a(datetime(2026, 11, 2, 7, 0))
        t = self.nuovo_turno("T1", giorno=date(2026, 11, 2), inizio=time(8, 0), fine=time(12, 0))
        # il turno risulta in corso
        self.vai_a(datetime(2026, 11, 2, 9, 0))
        Turno().aggiornaStatoTurni()
        self.assertEqual(t.getStato(), StatoAttivita.IN_CORSO)

        ok = Turno().rimuoviTurno("T1")
        self.assertFalse(ok)

    def test_visualizza_prenotati_turno(self):
        t = self.nuovo_turno("T1", posti=3)
        # Inizialmente nessun prenotato: restituisce lista vuota
        self.assertEqual(Turno().visualizzaPrenotatiTurno(t), [])

        # Primo volontario
        self.vai_a(datetime(2026, 11, 2, 9, 0))
        v1 = self.nuovo_volontario("v1@cri.it", cf="AAAAAA80A01H501U")
        Prenotazione().prenotaTurno(t, v1)

        # Secondo volontario
        self.vai_a(datetime(2026, 11, 3, 10, 0))
        v2 = self.nuovo_volontario("v2@cri.it", cf="BBBBBB80A01H501U")
        Prenotazione().prenotaTurno(t, v2)

        prenotati = Turno().visualizzaPrenotatiTurno(t)
        self.assertEqual(len(prenotati), 2)
        # Ordine crescente di dataPrenotazione
        self.assertEqual(prenotati[0]["email"], "v1@cri.it")
        self.assertEqual(prenotati[0]["dataPrenotazione"], date(2026, 11, 2))
        self.assertEqual(prenotati[1]["email"], "v2@cri.it")
        self.assertEqual(prenotati[1]["dataPrenotazione"], date(2026, 11, 3))

        # Verifica che il dizionario originale del Volontario non venga inquinato
        self.assertNotIn("dataPrenotazione", v1.getDati())
        self.assertNotIn("dataPrenotazione", v2.getDati())


class TestTempo(TestBase):
    def test_aggiorna_stato_programmato_in_corso_concluso(self):
        # Alle 7:00 inseriamo entrambi i turni futuri
        self.vai_a(datetime(2026, 11, 2, 7, 0))
        t1 = self.nuovo_turno("T1", giorno=date(2026, 11, 2), inizio=time(8, 0), fine=time(10, 0))
        t2 = self.nuovo_turno("T2", giorno=date(2026, 11, 2), inizio=time(10, 0), fine=time(12, 0))

        # Alle 9:00: t1 e' iniziato (in corso), t2 ancora programmato
        self.vai_a(datetime(2026, 11, 2, 9, 0))
        Turno().aggiornaStatoTurni()
        self.assertEqual(t1.getStato(), StatoAttivita.IN_CORSO)
        self.assertEqual(t2.getStato(), StatoAttivita.PROGRAMMATO)

        # Sposta avanti a ore 13:00 -> entrambi conclusi
        self.vai_a(datetime(2026, 11, 2, 13, 0))
        Turno().aggiornaStatoTurni()
        self.assertEqual(t1.getStato(), StatoAttivita.CONCLUSO)
        self.assertEqual(t2.getStato(), StatoAttivita.CONCLUSO)

    def test_ore_di_servizio_aggiunte_ai_prenotati(self):
        self.vai_a(datetime(2026, 11, 2, 7, 0))
        t = self.nuovo_turno("T1", giorno=date(2026, 11, 2), inizio=time(8, 0), fine=time(12, 0))
        v = self.nuovo_volontario()
        Prenotazione().prenotaTurno(t, v)
        self.assertEqual(v.getDati()["oreServizio"], 0.0)

        # Sposta a fine turno
        self.vai_a(datetime(2026, 11, 2, 12, 30))
        Turno().aggiornaStatoTurni()
        self.assertEqual(t.getStato(), StatoAttivita.CONCLUSO)
        self.assertEqual(v.getDati()["oreServizio"], 4.0)

    def test_promemoria_solo_ai_turni_di_domani(self):
        t_domani = self.nuovo_turno("T_DOMANI", giorno=date(2026, 11, 3))
        t_dopodomani = self.nuovo_turno("T_DOPO", giorno=date(2026, 11, 4))
        v = self.nuovo_volontario()
        Prenotazione().prenotaTurno(t_domani, v)
        Prenotazione().prenotaTurno(t_dopodomani, v)
        self.email.clear()

        Turno().inviaPromemoriaTurni()
        self.assertEqual(len(self.email), 1)
        self.assertEqual(self.email[0][0], "mario@cri.it")
        self.assertIn("Promemoria turno", self.email[0][1])
        self.assertIn("T_DOMANI", self.email[0][2])


class TestPersistenza(TestBase):
    def test_i_riferimenti_condivisi_sopravvivono_al_salvataggio(self):
        t = self.nuovo_turno("T1")
        v = self.nuovo_volontario()
        Prenotazione().prenotaTurno(t, v)

        # Ricarica da pickle (simulando nuova istanza / sessione)
        gestore = GestoreDati()
        # azzeriamo la variabile di cache globale per forzare rilettura dal file
        import dati.gestore_dati as gd
        gd._dati = None
        dati_ricaricati = gestore.carica()

        t_ricaricato = dati_ricaricati["turni"]["T1"]
        v_ricaricato = dati_ricaricati["utenti"]["mario@cri.it"]
        p_ricaricata = dati_ricaricati["prenotazioni"][list(dati_ricaricati["prenotazioni"].keys())[0]]

        # Verifica che il riferimento nella lista del turno e nel volontario sia identico
        self.assertIs(t_ricaricato.getPrenotazioni()[0], p_ricaricata)
        self.assertIs(p_ricaricata.getVolontario(), v_ricaricato)


if __name__ == "__main__":
    unittest.main()
