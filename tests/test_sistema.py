import unittest
from datetime import datetime, timedelta
import sys
import os

# Aggiungi root al path per gli import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Sistema import Sistema
from Volontario import Volontario
from Referente import Referente
from UtenteFactory import costruisci_utente
from Turno import Turno
from Mezzo import Mezzo
from Corso import Corso
from Checklist import Checklist
from Report import Report
from EmailService import EmailService
from GestioneTurniController import GestioneTurniController
from GestioneFlottaController import GestioneFlottaController
from GestioneFormazioneController import GestioneFormazioneController


class TestModelli(unittest.TestCase):
    def test_volontario_creation_and_hours(self):
        v = Volontario(
            cod_fiscale="RSSMRA85M01H501Z",
            nome="Mario",
            cognome="Rossi",
            email="mario.rossi@cri.it",
            patenti=["B", "C1"],
            qualifiche=["Soccorritore 118"]
        )
        self.assertEqual(v.cod_fiscale, "RSSMRA85M01H501Z")
        self.assertEqual(v.getNomeCompleto(), "Mario Rossi")
        self.assertIn("B", v.patenti)
        self.assertEqual(v.getMonteOre(), 0)

        v.aggiungiOreServizio(12)
        self.assertEqual(v.getMonteOre(), 12)
        self.assertEqual(v.getMonteOre(), 12.0)

    def test_ruoli_ammessi_solo_volontario_e_referente(self):
        # Verifica che il sistema ammetta solo Volontario e Referente e che OperatoreSanitario sia rimosso
        u_vol = costruisci_utente({"cod_fiscale": "RSSMRA85M01H501Z", "nome": "Mario", "cognome": "Rossi", "email": "mario@cri.it", "ruolo": "volontario"})
        self.assertIsInstance(u_vol, Volontario)
        self.assertEqual(u_vol.ruolo, "volontario")

        u_ref = costruisci_utente({"cod_fiscale": "VRDGPP75C10H501K", "nome": "Giuseppe", "cognome": "Verdi", "email": "giuseppe@cri.it", "ruolo": "referente"})
        self.assertIsInstance(u_ref, Referente)
        self.assertEqual(u_ref.ruolo, "referente")

        # Qualsiasi tentativo di richiedere operatore_sanitario deve essere ricondotto in fallback pulito a Volontario
        u_op = costruisci_utente({"cod_fiscale": "BNCLRA90A41H501A", "nome": "Laura", "cognome": "Bianchi", "email": "laura@cri.it", "ruolo": "operatore_sanitario"})
        self.assertIsInstance(u_op, Volontario)
        self.assertEqual(u_op.ruolo, "volontario")

    def test_referente(self):
        ref = Referente(
            cod_fiscale="VRDGPP75C10H501K",
            nome="Giuseppe",
            cognome="Verdi",
            email="giuseppe.verdi@cri.it",
            settoreGestito="Formazione & Flotta"
        )
        self.assertEqual(ref.ruolo, "referente")
        self.assertEqual(ref.settoreGestito, "Formazione & Flotta")

    def test_turno_and_checklist(self):
        t = Turno(
            id="T_100",
            data="2026-10-15",
            oraInizio="08:00",
            oraFine="14:00",
            luogoDestinazione="Ospedale Regionale",
            patenteRichiesta="C1",
            personeRichieste=2,
            tipoServizio="Emergenza 118"
        )
        self.assertEqual(t.fascia_oraria, "08:00 - 14:00")
        self.assertEqual(t.patenteRichiesta, "C1")
        self.assertEqual(t.personeRichieste, 2)


class TestSistema(unittest.TestCase):
    def setUp(self):
        self.sistema = Sistema()
        self.volontario = Volontario(
            cod_fiscale="RSSMRA85M01H501Z",
            nome="Mario",
            cognome="Rossi",
            email="mario@cri.it",
            patenti=["B"]
        )
        self.sistema.aggiungi_volontario(self.volontario)

    def test_get_volontario_case_insensitive(self):
        v = self.sistema.get_volontario("rssmra85m01h501z")
        self.assertIsNotNone(v)
        self.assertEqual(v.nome, "Mario")

    def test_prenota_e_annulla_turno(self):
        turno = Turno(
            id="T_200",
            data="2026-10-20",
            oraInizio="14:00",
            oraFine="20:00",
            tipoServizio="Trasporto Sanitario"
        )
        self.sistema.aggiungi_turno(turno)

        # Assegna turno
        self.sistema.assegna_turno(self.volontario.cod_fiscale, turno)
        self.assertIn(turno, self.volontario.turni_assegnati)
        self.assertIn(self.volontario, turno.volontari_assegnati)

        # Annulla turno (verifica che non sollevi AttributeError)
        self.sistema.annulla_turno(self.volontario.cod_fiscale, turno)
        self.assertNotIn(turno, self.volontario.turni_assegnati)
        self.assertNotIn(self.volontario, turno.volontari_assegnati)

    def test_notifiche_e_avvisi_sistema(self):
        # Turno scoperto
        turno_scoperto = Turno(
            id="T_SCOPERTO",
            data="2026-11-01",
            oraInizio="07:00",
            oraFine="13:00",
            personeRichieste=2,
            tipoServizio="Emergenza"
        )
        self.sistema.aggiungi_turno(turno_scoperto)

        avvisi_turni = self.sistema.notifica_turni_scoperti()
        self.assertTrue(len(avvisi_turni) > 0)
        self.assertEqual(avvisi_turni[0]["tipo"], "turno")

        # Mezzo con assicurazione scaduta
        mezzo = Mezzo(
            targa="CRI123AB",
            tipo="Ambulanza",
            dataScadenzaAssicurazione="2020-01-01"
        )
        self.sistema.aggiungi_mezzo(mezzo)

        tutti_avvisi = self.sistema.get_avvisi_sistema()
        self.assertTrue(any(a["tipo"] == "mezzo" for a in tutti_avvisi))

    def test_stampa_report_volontario(self):
        report_txt = self.sistema.stampa_report_volontario(self.volontario.cod_fiscale)
        self.assertIn("REPORT VOLONTARIO", report_txt)
        self.assertIn(self.volontario.nome, report_txt)
        self.assertIn(self.volontario.cod_fiscale, report_txt)

        # Verifica con turno assegnato e ore registrate
        t = Turno(codice="T_REP_1", data="2026-11-01", fascia_oraria="08:00 - 14:00", tipoServizio="118")
        self.volontario.turni_assegnati.append(t)
        self.volontario.compila_report_turno(t, 6.0)
        report_con_turni = self.sistema.stampa_report_volontario(self.volontario.cod_fiscale)
        self.assertIn("Turni assegnati:", report_con_turni)
        self.assertIn("Ore: 6.00", report_con_turni)


class TestGestioneTurniController(unittest.TestCase):
    def setUp(self):
        self.controller = GestioneTurniController()
        self.volontario = Volontario(
            cod_fiscale="VRDGPP80A01H501R",
            nome="Giuseppe",
            patenti=["B", "C1"]
        )

    def test_valida_dati(self):
        t_valido = Turno(
            id="T_V",
            data="2026-10-10",
            oraInizio="08:00",
            oraFine="14:00",
            personeRichieste=1
        )
        self.assertTrue(self.controller.validaDati(t_valido))

        t_invalido = Turno(id="T_INV", data="", oraInizio="", oraFine="")
        self.assertFalse(self.controller.validaDati(t_invalido))

    def test_verifica_copertura_patente(self):
        t_richiede_c1 = Turno(id="T1", patenteRichiesta="C1")
        self.assertTrue(self.controller.verificaCoperturaPatente(self.volontario, t_richiede_c1))

        t_richiede_cRI4 = Turno(id="T2", patenteRichiesta="CRI Grado 4")
        self.assertFalse(self.controller.verificaCoperturaPatente(self.volontario, t_richiede_cRI4))

    def test_verifica_tempo_limite_sovrapposizione(self):
        t1 = Turno(id="T_M", data="2026-10-10", oraInizio="08:00", oraFine="14:00")
        t2_sovrapposto = Turno(id="T_SOVR", data="2026-10-10", oraInizio="12:00", oraFine="18:00")
        t3_distaccato = Turno(id="T_DIST", data="2026-10-10", oraInizio="15:00", oraFine="21:00")

        self.volontario.prenotaTurno(t1)

        # Sovrapposto: deve ritornare False
        self.assertFalse(self.controller.verificaTempoLimite(self.volontario, t2_sovrapposto))

        # Distaccato (orario successivo senza sovrapposizione): deve ritornare True
        self.assertTrue(self.controller.verificaTempoLimite(self.volontario, t3_distaccato))


class TestEmailService(unittest.TestCase):
    def test_tracking_e_storico_email(self):
        EmailService.clear_history()
        self.assertEqual(len(EmailService.get_sent_emails()), 0)

        esito = EmailService.inviaMail(
            destinatario="volontario@cri.it",
            messaggio="Conferma turno di servizio per domani ore 08:00.",
            oggetto="Conferma Turno CRI"
        )
        self.assertTrue(esito)
        storico = EmailService.get_sent_emails()
        self.assertEqual(len(storico), 1)
        self.assertEqual(storico[0]["destinatario"], "volontario@cri.it")
        self.assertIn("Conferma turno", storico[0]["messaggio"])


class TestControllersInMemory(unittest.TestCase):
    def test_flotta_controller_visualizza_mezzi(self):
        sistema = Sistema()
        m = Mezzo(targa="CRI555ZZ", tipo="Ambulanza")
        sistema.aggiungi_mezzo(m)

        flotta_ctrl = GestioneFlottaController()
        mezzi = flotta_ctrl.visualizzaStatoMezzi(sistema=sistema)
        self.assertEqual(len(mezzi), 1)
        self.assertEqual(mezzi[0].targa, "CRI555ZZ")

    def test_formazione_controller_visualizza_catalog(self):
        sistema = Sistema()
        c = Corso(id="C_BLSD", titolo="BLSD Operativo", nome="BLSD Operativo")
        sistema.aggiungi_corso(c)

        formazione_ctrl = GestioneFormazioneController()
        corsi = formazione_ctrl.visualizzaCatalog(sistema=sistema)
        self.assertEqual(len(corsi), 1)
        self.assertEqual(corsi[0].titolo, "BLSD Operativo")


class TestSessionManager(unittest.TestCase):
    def setUp(self):
        from session_manager import clear_session
        clear_session()

    def tearDown(self):
        from session_manager import clear_session
        clear_session()

    def test_save_load_and_clear_session(self):
        from session_manager import save_session, load_session, clear_session
        self.assertIsNone(load_session())

        user = Volontario(
            cod_fiscale="RSSMRA85M01H501Z",
            nome="Mario",
            cognome="Rossi",
            email="mario.rossi@cri.it",
            ruolo="volontario"
        )
        saved = save_session(user)
        self.assertTrue(saved)

        session = load_session()
        self.assertIsNotNone(session)
        self.assertEqual(session.get("cod_fiscale"), "RSSMRA85M01H501Z")
        self.assertEqual(session.get("email"), "mario.rossi@cri.it")

        cleared = clear_session()
        self.assertTrue(cleared)
        self.assertIsNone(load_session())


class TestVolontarioPatentiPdf(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_volontario_patenti_pdf_to_dict(self):
        v = Volontario(
            cod_fiscale="RSSMRA85M01H501Z",
            nome="Mario",
            cognome="Rossi",
            email="mario@cri.it",
            patenti=["B", "C"],
            patenti_pdf={"B": "patenti_pdf/mario_B.pdf", "C": "patenti_pdf/mario_C.pdf"},
            patente_pdf_path="patenti_pdf/mario_B.pdf"
        )
        d = v.to_dict()
        self.assertIn("patenti_pdf", d)
        self.assertEqual(d["patenti_pdf"]["B"], "patenti_pdf/mario_B.pdf")
    def test_dialog_ha_pdf_valido_integration(self):
        from PyQt5.QtWidgets import QApplication
        from layout.modifica_dati_dialog import ModificaDatiDialog
        app = QApplication.instance() or QApplication([])

        # Volontario con patente ma senza file PDF
        v = Volontario(
            cod_fiscale="TSTCF100A01H501Z",
            nome="Test",
            cognome="User",
            email="test@cri.it",
            patenti=["B"]
        )
        dlg = ModificaDatiDialog(v)
        self.assertFalse(dlg.ha_pdf_valido("B"))

        # Crea un PDF valido e associalo
        valid_pdf_path = os.path.join(self.temp_dir.name, "valid_patente_b.pdf")
        with open(valid_pdf_path, "wb") as f:
            body = (b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
                    + (b"xref\n0 2\n0000000000 65535 f \n" * 15)
                    + b"trailer\n<< >>\nstartxref\n300\n%%EOF\n")
            f.write(body)
        dlg.patenti_pdf["B"] = valid_pdf_path
        self.assertTrue(dlg.ha_pdf_valido("B"))


class TestVerificaPatente(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_volontario_app_io_serialization(self):
        v = Volontario(
            cod_fiscale="RSSMRA85M01H501Z",
            nome="Mario",
            cognome="Rossi",
            email="mario@cri.it",
            patenti=["B", "C"],
            app_io_verificato=True,
            numero_patente="U110EA3FK",
            scadenza_patente="2034-10-25",
            app_io_certificato_id="IO-ITW-ABCDEF123456"
        )
        self.assertTrue(v.app_io_verificato)
        self.assertEqual(v.numero_patente, "U110EA3FK")
        d = v.to_dict()
        self.assertTrue(d["app_io_verificato"])
        self.assertEqual(d["numero_patente"], "U110EA3FK")
        self.assertEqual(d["scadenza_patente"], "2034-10-25")
        self.assertEqual(d["app_io_certificato_id"], "IO-ITW-ABCDEF123456")

    def test_dialog_pdf_valido_con_file(self):
        from PyQt5.QtWidgets import QApplication
        from layout.modifica_dati_dialog import ModificaDatiDialog
        app = QApplication.instance() or QApplication([])

        dummy_pdf = os.path.join(self.temp_dir.name, "test_patente.pdf")
        with open(dummy_pdf, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n" + (b" " * 600) + b"\ntrailer\n<< >>\n%%EOF\n")

        v = Volontario(
            cod_fiscale="GLNSRN03A62I156Z",
            nome="Serena",
            cognome="Giuliani",
            patenti=["B"],
            numero_patente="U1998877X",
            scadenza_patente="2034-10-25",
            patente_pdf_path=dummy_pdf
        )
        dlg = ModificaDatiDialog(v)
        self.assertTrue(dlg.ha_pdf_valido("B"))


class TestCalendarService(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()


    def test_turni_compatibili_filtro_controller(self):
        ctrl = GestioneTurniController()
        v_b = Volontario(
            cod_fiscale="VRDGPP80A01H501R",
            nome="Giuseppe",
            patenti=["B"]
        )
        t_b = Turno(id="T_B", patenteRichiesta="B")
        t_c = Turno(id="T_C", patenteRichiesta="C")
        t_none = Turno(id="T_NONE", patenteRichiesta="Nessuna")

        self.assertTrue(ctrl.verificaCoperturaPatente(v_b, t_b))
        self.assertFalse(ctrl.verificaCoperturaPatente(v_b, t_c))
        self.assertTrue(ctrl.verificaCoperturaPatente(v_b, t_none))

    def test_prenotazione_turno_regole_analisi(self):
        from PyQt5.QtWidgets import QApplication
        from layout.prenotazione_turno_dialog import PrenotazioneTurnoDialog
        app = QApplication.instance() or QApplication([])

        ctrl = GestioneTurniController()
        # Volontario con patente B
        v = Volontario(
            cod_fiscale="RSSMRA85M01H501Z",
            nome="Mario",
            cognome="Rossi",
            patenti=["B"]
        )

        # Turno con fabbisogno generico volontario: 2 e patente B
        t = Turno(
            id="T_REGOLE_1",
            data="2026-12-01",
            oraInizio="08:00",
            oraFine="14:00",
            patenteRichiesta="B",
            personeRichieste=2
        )
        dlg = PrenotazioneTurnoDialog(t, v, ctrl)
        ruoli = dlg.analizza_ruoli_disponibili()
        self.assertEqual(len(ruoli), 2)

        # Verifica ruolo Autista
        autista = next((r for r in ruoli if "Autista" in r["nome"]), None)
        self.assertIsNotNone(autista)
        self.assertEqual(autista["posti_totali"], 1)
        self.assertEqual(autista["posti_liberi"], 1)
        self.assertTrue(autista["ha_patente"])
        self.assertEqual(autista["richiede_patente"], "B")

        # Verifica ruolo Soccorritore
        socc = next((r for r in ruoli if "Soccorritore" in r["nome"]), None)
        self.assertIsNotNone(socc)
        self.assertEqual(socc["posti_totali"], 1)
        self.assertEqual(socc["posti_liberi"], 1)
        self.assertTrue(socc["ha_patente"])

        # Volontario senza patente B
        v_senza = Volontario(
            cod_fiscale="BNCLRA90A41H501A",
            nome="Laura",
            patenti=[]
        )
        dlg_senza = PrenotazioneTurnoDialog(t, v_senza, ctrl)
        ruoli_senza = dlg_senza.analizza_ruoli_disponibili()
        autista_senza = next((r for r in ruoli_senza if "Autista" in r["nome"]), None)
        self.assertIsNotNone(autista_senza)
        assert autista_senza is not None
        self.assertFalse(autista_senza["ha_patente"])

    def test_prenotazione_turno_dialog_sovrapposizione(self):
        from PyQt5.QtWidgets import QApplication
        from layout.prenotazione_turno_dialog import PrenotazioneTurnoDialog
        app = QApplication.instance() or QApplication([])

        ctrl = GestioneTurniController()
        v = Volontario(
            cod_fiscale="VRDGPP75C10H501K",
            nome="Giuseppe",
            patenti=["B"]
        )
        t_assegnato = Turno(
            id="T_OLD",
            data="2026-12-01",
            oraInizio="08:00",
            oraFine="14:00"
        )
        v.turni_assegnati.append(t_assegnato)

        # Turno nuovo sovrapposto
        t_nuovo = Turno(
            id="T_NEW_SOVRAPP",
            data="2026-12-01",
            oraInizio="10:00",
            oraFine="16:00",
            patenteRichiesta="B"
        )

        dlg = PrenotazioneTurnoDialog(t_nuovo, v, ctrl)
        self.assertTrue(dlg.ha_sovrapposizione)
        self.assertFalse(dlg.btn_conferma.isEnabled())


class TestGestioneCorsiMiei(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_corsi_suddivisi_effettuati_e_non(self):
        sistema = Sistema()
        ctrl = GestioneFormazioneController()

        v = Volontario(
            cod_fiscale="RSSMRA85M01H501Z",
            nome="Mario",
            cognome="Rossi",
            qualifiche=["Primo Soccorso Base"]
        )

        c1 = Corso(id="C_BASE", titolo="Primo Soccorso Base", nome="Primo Soccorso Base", mesiValidita=24)
        c2 = Corso(id="C_GUIDA", titolo="Guida Mezzi Emergenza", nome="Guida Mezzi Emergenza", mesiValidita=12)
        c3 = Corso(id="C_TRIAGE", titolo="Triage Maxi-Emergenze", nome="Triage Maxi-Emergenze", mesiValidita=36)

        sistema.aggiungi_corso(c1)
        sistema.aggiungi_corso(c2)
        sistema.aggiungi_corso(c3)

        # c2 è in formazione (iscritto, non ancora effettuato)
        v.formazione.append(c2)

        suddivisi = ctrl.ottieniCorsiSuddivisi(v, sistema)

        # c1 deve essere negli effettuati (perché possiede la qualifica)
        eff_ids = [c.id for c in suddivisi["effettuati"]]
        self.assertIn("C_BASE", eff_ids)

        # c2 deve essere in corso / da effettuare
        inc_ids = [c.id for c in suddivisi["in_corso"]]
        self.assertIn("C_GUIDA", inc_ids)

        # c3 deve essere tra i disponibili a catalogo
        disp_ids = [c.id for c in suddivisi["disponibili"]]
        self.assertIn("C_TRIAGE", disp_ids)

    def test_iscrizione_e_disiscrizione_corso(self):
        sistema = Sistema()
        ctrl = GestioneFormazioneController()

        v = Volontario(
            cod_fiscale="BNCLRA90A41H501A",
            nome="Laura",
            cognome="Bianchi"
        )
        c = Corso(id="C_DEFIB", titolo="BLSD - Defibrillatore", nome="BLSD - Defibrillatore")
        sistema.aggiungi_corso(c)

        # Inizialmente è disponibile
        res1 = ctrl.ottieniCorsiSuddivisi(v, sistema)
        self.assertEqual(len(res1["in_corso"]), 0)
        self.assertEqual(len(res1["disponibili"]), 1)

        # Iscrizione
        v.iscriviti_al_corso(c)
        res2 = ctrl.ottieniCorsiSuddivisi(v, sistema)
        self.assertEqual(len(res2["in_corso"]), 1)
        self.assertEqual(len(res2["disponibili"]), 0)

        # Disiscrizione / Rinuncia
        disiscritto = ctrl.disiscriviVolontario(v, "C_DEFIB")
        self.assertTrue(disiscritto)
        res3 = ctrl.ottieniCorsiSuddivisi(v, sistema)
        self.assertEqual(len(res3["in_corso"]), 0)
        self.assertEqual(len(res3["disponibili"]), 1)

    def test_attestazione_corso_completamento(self):
        sistema = Sistema()
        ctrl = GestioneFormazioneController()

        v = Volontario(
            cod_fiscale="VRDGPP75C10H501K",
            nome="Giuseppe",
            cognome="Verdi"
        )
        c = Corso(id="C_TRAUMA", titolo="Soccorso Traumi Avanzato", nome="Soccorso Traumi Avanzato", mesiValidita=12)
        sistema.aggiungi_corso(c)
        v.iscriviti_al_corso(c)

        # Prima dell'attestazione: in_corso
        res1 = ctrl.ottieniCorsiSuddivisi(v, sistema)
        self.assertEqual(len(res1["in_corso"]), 1)
        self.assertEqual(len(res1["effettuati"]), 0)

        # Il referente attesta la partecipazione
        v.corsi_frequentati.append(c)
        v.formazione.remove(c)
        v.aggiungiQualifica(c.titolo)
        v.aggiungiOreServizio(10)

        # Dopo l'attestazione: effettuato con qualifica e ore
        res2 = ctrl.ottieniCorsiSuddivisi(v, sistema)
        self.assertEqual(len(res2["effettuati"]), 1)
        self.assertEqual(len(res2["in_corso"]), 0)
        self.assertIn("Soccorso Traumi Avanzato", v.qualifiche)
        self.assertEqual(v.getMonteOre(), 10)

    def test_dettaglio_corso_dialog_component(self):
        from PyQt5.QtWidgets import QApplication, QLabel
        from layout.dettaglio_corso_dialog import DettaglioCorsoDialog
        app = QApplication.instance() or QApplication([])

        v = Volontario(cod_fiscale="RSSMRA85M01H501Z", nome="Mario", cognome="Rossi")
        c = Corso(id="C_TEST", titolo="Corso Manovre Salvavita", mesiValidita=24)

        # Dialog in stato effettuato
        dlg_eff = DettaglioCorsoDialog(c, v, "effettuato")
        self.assertEqual(dlg_eff.stato_tipo, "effettuato")

        # Dialog in stato in_corso
        dlg_inc = DettaglioCorsoDialog(c, v, "in_corso")
        self.assertEqual(dlg_inc.stato_tipo, "in_corso")

        # Dialog in stato disponibile
        dlg_disp = DettaglioCorsoDialog(c, v, "disponibile")
        self.assertEqual(dlg_disp.stato_tipo, "disponibile")


class TestGestioneUtenteController(unittest.TestCase):
    def setUp(self):
        from EmailService import EmailService
        EmailService.clear_history()

    def test_valida_formato(self):
        from GestioneUtenteController import GestioneUtenteController
        ctrl = GestioneUtenteController()
        self.assertTrue(ctrl.validaFormato("test@cri.it", "password123"))
        self.assertFalse(ctrl.validaFormato("invalid-email", "password123"))
        self.assertFalse(ctrl.validaFormato("test@cri.it", "123"))

    def test_recupera_credenziali_invio_email(self):
        from GestioneUtenteController import GestioneUtenteController
        from EmailService import EmailService
        ctrl = GestioneUtenteController()

        # Invio con email valida
        successo, msg = ctrl.recuperaCredenziali("volontario.test@cri.it")
        self.assertTrue(successo)
        self.assertIn("volontario.test@cri.it", msg)

        # Verifica che l'email sia stata registrata in EmailService
        sent = EmailService.get_sent_emails()
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0]["destinatario"], "volontario.test@cri.it")
        self.assertIn("Recupero Credenziali", sent[0]["oggetto"])
        self.assertIn("reimpostare la tua password", sent[0]["messaggio"])

        # Invio con stringa vuota o non valida
        fallito, err_msg = ctrl.recuperaCredenziali("")
        self.assertFalse(fallito)
        self.assertIn("Inserisci un indirizzo", err_msg)

    def test_recupero_credenziali_dialog(self):
        from PyQt5.QtWidgets import QApplication
        from layout.LoginWindow import RecuperoCredenzialiDialog
        app = QApplication.instance() or QApplication([])

        dlg = RecuperoCredenzialiDialog()
        dlg.txt_identificativo.setText("")
        dlg._invia_recupero()
        self.assertFalse(dlg.lbl_feedback.isHidden())

        dlg.txt_identificativo.setText("mario.rossi@cri.it")
        from unittest.mock import patch
        with patch("PyQt5.QtWidgets.QMessageBox.information"):
            dlg._invia_recupero()
        # Con email valida, il dialog accetta e invia l'email
        from EmailService import EmailService
        self.assertTrue(any(e["destinatario"] == "mario.rossi@cri.it" for e in EmailService.get_sent_emails()))

    def test_assegnazione_mezzo_a_turno(self):
        from Mezzo import Mezzo
        from Turno import Turno
        from GestioneFlottaController import GestioneFlottaController

        ctrl = GestioneFlottaController()
        m = Mezzo(targa="CRI 999 ZZ", tipo="Ambulanza Tipo A", chilometraggioTotale=15000, stato="Disponibile")
        t = Turno(id="T_TEST_MEZZO", data="2026-10-15", oraInizio="08:00", oraFine="14:00", tipoServizio="Emergenza")

        self.assertIsNone(t.mezzo)
        self.assertEqual(t.mezzo_targa, "")
        self.assertTrue(m.disponibile)

        # Assegna mezzo al turno
        res = ctrl.assegnaMezzoATurno(m, t)
        self.assertTrue(res)
        self.assertEqual(t.mezzo, m)
        self.assertEqual(t.mezzo_targa, "CRI 999 ZZ")
        self.assertIn(t, m.turni_assegnati)
        self.assertEqual(m.stato, "Assegnato")
        self.assertFalse(m.disponibile)

        # Rimuovi mezzo dal turno
        res_del = ctrl.assegnaMezzoATurno(None, t)
        self.assertTrue(res_del)
        self.assertIsNone(t.mezzo)
        self.assertEqual(t.mezzo_targa, "")
        self.assertNotIn(t, m.turni_assegnati)
        self.assertTrue(m.disponibile)
        self.assertEqual(m.stato, "Disponibile")

    def test_compila_checklist_dialog_initialization(self):
        from PyQt5.QtWidgets import QApplication
        from Checklist import Checklist
        from Turno import Turno
        from layout.MainWindow import CompilaChecklistDialog
        app = QApplication.instance() or QApplication([])

        c = Checklist(id="CL_TEST_DLG")
        t = Turno(id="T_DLG_1", data="2026-10-20")
        dlg = CompilaChecklistDialog(
            checklist=c,
            ruolo="Autista A (Emergenza)",
            utente_nome="Mario Rossi",
            targa="CRI 302 AJ",
            turno=t
        )
        self.assertIsNotNone(dlg.lbl_progresso)
        self.assertIn("Controllo 1 di", dlg.lbl_progresso.text())
        self.assertEqual(dlg.targa, "CRI 302 AJ")
        self.assertFalse(dlg.btn_indietro.isEnabled())

        # Test clic OK e avanzamento automatico
        dlg.btn_ok.click()
        self.assertEqual(dlg.risposte[dlg.controlli[0]["nome"]], "OK")
        self.assertIsNotNone(dlg._timer_avanzamento)
        self.assertTrue(dlg._timer_avanzamento.isActive())

        # Simula lo scatto del timer
        dlg._auto_avanza()
        self.assertEqual(dlg.current_index, 1)
        self.assertIn("Controllo 2 di", dlg.lbl_progresso.text())
        self.assertTrue(dlg.btn_indietro.isEnabled())

    def test_ruoli_volontari_in_turno(self):
        from Turno import Turno
        from Volontario import Volontario

        t = Turno(id="T_RUOLO_1", personeRichieste=2)
        v1 = Volontario(cod_fiscale="RSSMRA85M01H501Z", nome="Mario", cognome="Rossi")
        v2 = Volontario(cod_fiscale="GLNSRN03A62I156Z", nome="Serena", cognome="Giuliani")

        # Assegnazione volontario con ruolo
        t.aggiungiVolontario(v1, ruolo="Autista Tipo A")
        self.assertIn("RSSMRA85M01H501Z", t.volontari_ruoli)
        self.assertEqual(t.volontari_ruoli["RSSMRA85M01H501Z"], "Autista Tipo A")

        t.aggiungiVolontario(v2, ruolo="Soccorritore Tipo B")
        self.assertEqual(t.volontari_ruoli["GLNSRN03A62I156Z"], "Soccorritore Tipo B")
        self.assertEqual(len(t.volontari_assegnati), 2)

        # Rimozione volontario
        t.rimuoviVolontario(v1)
        self.assertNotIn("RSSMRA85M01H501Z", t.volontari_ruoli)
        self.assertIn("GLNSRN03A62I156Z", t.volontari_ruoli)

    def test_ruoli_in_tabella_turni_e_assenza_patente_header(self):
        from PyQt5.QtWidgets import QApplication
        from layout.MainWindow import MainWindow
        from Sistema import Sistema
        from Volontario import Volontario
        from Turno import Turno

        app = QApplication.instance() or QApplication([])
        sistema = Sistema()
        v = Volontario(cod_fiscale="GLNSRN03A62I156Z", nome="Serena", cognome="Giuliani", patenti=["B"])
        sistema.logged_user = v
        sistema.volontari = [v]

        t = Turno(id="T_RUOLO_2", data="2026-11-10", tipoServizio="Emergenza 118", personeRichieste=2)
        t.volontari_assegnati.append(v)
        v.turni_assegnati.append(t)
        t.volontari_ruoli["GLNSRN03A62I156Z"] = "Autista Tipo A"
        sistema.turni = [t]

        win = MainWindow(sistema)

        # 1. Verifica che nell'header in alto NON ci sia il badge della patente aggiunto
        self.assertFalse(win.lbl_badge_patente.isVisible())
        # Non deve essere presente nei widget attivi dell'header
        self.assertEqual(win.header_layout.indexOf(win.lbl_badge_patente), -1)

        # 2. Verifica che nella tabella dei turni assegnati ci sia la colonna "Il Tuo Ruolo"
        header_labels = [(it.text() if (it := win.tbl_miei_turni.horizontalHeaderItem(c)) else "") for c in range(win.tbl_miei_turni.columnCount())]
        self.assertIn("Il Tuo Ruolo", header_labels)
        col_idx = header_labels.index("Il Tuo Ruolo")

        # 3. Verifica che la cella mostri correttamente il ruolo che spetta al volontario
        self.assertGreater(win.tbl_miei_turni.rowCount(), 0)
        item_ruolo = win.tbl_miei_turni.item(0, col_idx)
        self.assertIsNotNone(item_ruolo)
        assert item_ruolo is not None
        self.assertIn("Autista Tipo A", item_ruolo.text())
        self.assertIn("🚗", item_ruolo.text())


    def test_compila_resoconto_km_risultanti(self):
        from PyQt5.QtWidgets import QApplication
        from layout.MainWindow import CompilaResocontoDialog
        from Mezzo import Mezzo
        from Turno import Turno

        app = QApplication.instance() or QApplication([])

        mezzo = Mezzo(targa="CRI 101 AA", tipo="Ambulanza", chilometraggioTotale=125400)
        turno = Turno(id="T_RES_01", data="2026-10-20", oraInizio="08:00", oraFine="14:00", tipoServizio="Emergenza 118")
        turno.assegna_mezzo(mezzo)

        dialog = CompilaResocontoDialog(turno=turno, mezzo=mezzo)

        # 1. Verifica che i chilometri iniziali siano letti dal mezzo
        self.assertEqual(dialog.km_iniziali, 125400)
        self.assertIsNotNone(dialog.spin_km_finali)
        assert dialog.spin_km_finali is not None
        self.assertEqual(dialog.spin_km_finali.value(), 125400)
        self.assertTrue(dialog.btn_salva.isEnabled())

        # 2. Inserimento chilometraggio inferiore: deve segnalare errore e disabilitare il salvataggio
        dialog.spin_km_finali.setValue(125300)
        self.assertFalse(dialog.btn_salva.isEnabled())
        self.assertIn("non possono essere inferiori", dialog.lbl_km_calc.text())

        # 3. Inserimento chilometraggio risultante a fine turno: 125.550 km (+150 km percorsi)
        dialog.spin_km_finali.setValue(125550)
        self.assertTrue(dialog.btn_salva.isEnabled())
        self.assertIn("+150 km", dialog.lbl_km_calc.text())

        # 4. Verifica dati restituiti da get_dati()
        km_finali, km_percorsi, ore, note = dialog.get_dati()
        self.assertEqual(km_finali, 125550)
        self.assertEqual(km_percorsi, 150)
        self.assertEqual(ore, 6.0)

        # 5. Verifica aggiornamento odometro del Mezzo
        mezzo.aggiornaKm(km_finali)
        self.assertEqual(mezzo.chilometraggioTotale, 125550)
        self.assertFalse(mezzo.isDismesso(400000))

    def test_controllo_checklist_gia_compilata(self):
        from unittest.mock import patch
        from PyQt5.QtWidgets import QApplication, QMessageBox
        from Sistema import Sistema
        from Volontario import Volontario
        from Turno import Turno
        from layout.MainWindow import MainWindow

        app = QApplication.instance() or QApplication([])
        sistema = Sistema()
        v = Volontario(cod_fiscale="RSSMRA85M01H501Z", nome="Mario", cognome="Rossi", email="mario.rossi@cri.it")
        t = Turno(id="T_CHK_BLOCKED", data="2026-10-25", fascia_oraria="08:00 - 14:00", checklist=True)
        t.aggiungiVolontario(v, ruolo="Autista Tipo A")
        v.turni_assegnati.append(t)
        sistema.volontari = [v]
        sistema.turni = [t]
        sistema.logged_user = v

        win = MainWindow(sistema)
        win.popola_tabelle_turni_volontario()

        # 1. Verifica che lo stato nella tabella indichi checklist OK
        item_stato = win.tbl_miei_turni.item(0, 7)
        self.assertIsNotNone(item_stato)
        assert item_stato is not None
        self.assertIn("Checklist OK", item_stato.text())

        # 2. Seleziona la riga del turno e verifica che il pulsante segnali che è già completata
        win.tbl_miei_turni.selectRow(0)
        self.assertEqual(win.btn_checklist.text(), "✅ Checklist Completata")

        # 3. Tentativo di avviare la compilazione: deve essere intercettato dal controllo bloccante
        with patch.object(QMessageBox, "information") as mock_info, \
             patch("layout.MainWindow.CompilaChecklistDialog") as mock_dlg:
            win.azione_compila_checklist()
            
            # QMessageBox.information deve essere stato chiamato
            mock_info.assert_called_once()
            args, _ = mock_info.call_args
            self.assertIn("Già Completata", args[1])
            
            # Il dialog di compilazione NON deve essere stato aperto
            mock_dlg.assert_not_called()

    def test_caricamento_pdf_e_layout_responsive(self):
        from PyQt5.QtWidgets import QApplication
        from layout.modifica_dati_dialog import ModificaDatiDialog
        from Volontario import Volontario
        from unittest.mock import patch

        app = QApplication.instance() or QApplication([])
        v = Volontario(
            cod_fiscale="GLNSRN03A62I156Z",
            nome="Serena",
            cognome="Giuliani",
            email="serena.giuliani@gmail.com",
            patenti=["B"]
        )

        tmp_pdf = os.path.abspath("test_patente_card_temp.pdf")
        with open(tmp_pdf, "wb") as f:
            f.write(b"%PDF-1.4\n")

        try:
            # 1. Test ModificaDatiDialog con Sticky Footer e ScrollArea
            dlg_modifica = ModificaDatiDialog(v)
            self.assertIsNotNone(dlg_modifica.salva_btn)
            self.assertEqual(dlg_modifica.salva_btn.text(), "💾 Salva Dati")
            self.assertTrue(dlg_modifica.salva_btn.isEnabled())

            # 2. Test caricamento file PDF patente
            with patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName", return_value=(tmp_pdf, "File PDF (*.pdf)")), \
                 patch("PyQt5.QtWidgets.QMessageBox.information"):
                successo_caricamento = dlg_modifica.carica_pdf_patente("B")
                self.assertTrue(successo_caricamento)

            self.assertTrue(dlg_modifica.ha_pdf_valido("B"))

            # 3. Test salvataggio dati
            with patch("PyQt5.QtWidgets.QMessageBox.information"), patch.object(v, "aggiorna_firestore"):
                dlg_modifica.salva_dati()
                self.assertIn("B", v.patenti)
        finally:
            if os.path.exists(tmp_pdf):
                os.remove(tmp_pdf)

    def test_turni_al_completo_esclusi_da_turni_disponibili(self):
        from PyQt5.QtWidgets import QApplication
        from layout.MainWindow import MainWindow
        from Sistema import Sistema
        from Turno import Turno

        app = QApplication.instance() or QApplication([])
        sistema = Sistema()

        user = Volontario(
            cod_fiscale="GLNSRN03A62I156Z",
            nome="Serena",
            cognome="Giuliani",
            patenti=["B"]
        )
        altro_v = Volontario(
            cod_fiscale="RSSMRA85M01H501Z",
            nome="Mario",
            cognome="Rossi",
            patenti=["B"]
        )

        # Turno 1: Completo (1 posto su 1 occupato da Mario)
        t_pieno = Turno(
            id="T_PIENO",
            data="2026-11-20",
            oraInizio="08:00",
            oraFine="14:00",
            personeRichieste=1,
            stato="Aperto"
        )
        t_pieno.aggiungiVolontario(altro_v)

        # Turno 2: Disponibile (2 posti richiesti, 1 occupato da Mario)
        t_libero = Turno(
            id="T_LIBERO",
            data="2026-11-21",
            oraInizio="08:00",
            oraFine="14:00",
            personeRichieste=2,
            stato="Aperto"
        )
        t_libero.aggiungiVolontario(altro_v)

        sistema.logged_user = user

        win = MainWindow(sistema)
        sistema.turni = [t_pieno, t_libero]
        win.popola_tabelle_turni_volontario()

        # Di default, solo t_libero deve comparire nei turni disponibili per l'iscrizione
        id_visibili = [(it.text() if (it := win.tbl_turni_disp.item(r, 0)) else "") for r in range(win.tbl_turni_disp.rowCount())]
        self.assertNotIn("T_PIENO", id_visibili, "I turni al completo non devono comparire nei turni disponibili!")
        self.assertIn("T_LIBERO", id_visibili)

        # Se l'utente spunta 'Mostra anche turni al completo', deve comparire anche T_PIENO
        win.chk_mostra_completi.setChecked(True)
        win.popola_tabelle_turni_volontario()
        id_visibili_con_completi = [(it.text() if (it := win.tbl_turni_disp.item(r, 0)) else "") for r in range(win.tbl_turni_disp.rowCount())]
        self.assertIn("T_PIENO", id_visibili_con_completi)
        self.assertIn("T_LIBERO", id_visibili_con_completi)

    def test_registrazione_account_referente(self):
        from PyQt5.QtWidgets import QApplication
        from layout.LoginWindow import LoginWindow
        from Referente import Referente
        from GestioneUtenteController import GestioneUtenteController
        from unittest.mock import patch

        app = QApplication.instance() or QApplication([])
        sistema = Sistema()
        ctrl = GestioneUtenteController()

        login_win = LoginWindow(sistema, lambda msg="": None)

        # Compila i campi di registrazione
        login_win._reg_email.setText("nuovo.referente@cri.it")
        login_win._reg_nome.setText("Alessandro")
        login_win._reg_cognome.setText("Manzoni")
        login_win._reg_cf.setText("MNZLSN80A01H501X")
        login_win._reg_dob.setText("01/01/1980")
        login_win._reg_tel.setText("3339988776")
        login_win._reg_pwd.setText("password123")

        # Seleziona esplicitamente il ruolo Referente e imposta il PIN corretto
        idx = login_win._reg_ruolo.findData("referente")
        login_win._reg_ruolo.setCurrentIndex(idx)
        login_win._reg_pin.setText("CRI2026")

        # Mock della chiamata Firestore/Auth
        with patch.object(login_win.controller, "registraAccount", return_value=True), \
             patch("PyQt5.QtWidgets.QMessageBox.information"):
            login_win._do_register()

        self.assertIsNotNone(sistema.logged_user)
        self.assertEqual(sistema.logged_user.ruolo, "referente")
        self.assertIsInstance(sistema.logged_user, Referente)
        self.assertEqual(sistema.logged_user.cod_fiscale, "MNZLSN80A01H501X")

    def test_registrazione_account_referente_pin_errato_bloccata(self):
        from PyQt5.QtWidgets import QApplication
        from layout.LoginWindow import LoginWindow
        from unittest.mock import patch

        app = QApplication.instance() or QApplication([])
        sistema = Sistema()

        login_win = LoginWindow(sistema, lambda msg="": None)
        login_win._reg_email.setText("falso.referente@cri.it")
        login_win._reg_nome.setText("Luigi")
        login_win._reg_cognome.setText("Falsi")
        login_win._reg_cf.setText("FLSLGU80A01H501Y")
        login_win._reg_dob.setText("01/01/1980")
        login_win._reg_tel.setText("3331122334")
        login_win._reg_pwd.setText("password123")

        idx = login_win._reg_ruolo.findData("referente")
        login_win._reg_ruolo.setCurrentIndex(idx)
        login_win._reg_pin.setText("PIN_ERRATO_123")

        with patch("PyQt5.QtWidgets.QMessageBox.critical") as mock_crit, \
             patch.object(login_win.controller, "registraAccount") as mock_reg:
            login_win._do_register()
            # La registrazione deve essere bloccata
            mock_reg.assert_not_called()
            mock_crit.assert_called_once()
            self.assertIn("PIN Referente Richiesto", mock_crit.call_args[0][1])


    def test_modifica_ruolo_in_profilo_dialog_con_e_senza_pin(self):
        from PyQt5.QtWidgets import QApplication
        from layout.modifica_dati_dialog import ModificaDatiDialog
        from Volontario import Volontario
        from Referente import Referente
        from unittest.mock import patch

        app = QApplication.instance() or QApplication([])
        v = Volontario(
            cod_fiscale="RSSPLA85M01H501Z",
            nome="Paolo",
            cognome="Rossi",
            email="paolo@cri.it",
            ruolo="volontario"
        )
        dlg = ModificaDatiDialog(v)
        
        # 1. Tentativo con PIN ERRATO: deve essere bloccato e il ruolo deve rimanere 'volontario'
        idx = dlg.ruolo_combo.findData("referente")
        dlg.ruolo_combo.setCurrentIndex(idx)

        with patch("PyQt5.QtWidgets.QInputDialog.getText", return_value=("PIN_SBAGLIATO", True)), \
             patch("PyQt5.QtWidgets.QMessageBox.critical") as mock_crit:
            dlg.salva_dati()
            mock_crit.assert_called_once()
            self.assertEqual(v.ruolo, "volontario")
            self.assertNotIsInstance(v, Referente)

        # 2. Tentativo con PIN CORRETTO (CRI2026): deve andare a buon fine
        dlg.ruolo_combo.setCurrentIndex(idx)
        with patch("PyQt5.QtWidgets.QInputDialog.getText", return_value=("CRI2026", True)), \
             patch("PyQt5.QtWidgets.QMessageBox.information"), \
             patch.object(v, "aggiorna_firestore"):
            dlg.salva_dati()
            self.assertEqual(v.ruolo, "referente")
            self.assertIsInstance(v, Referente)

    def test_soglia_km_mezzo_400k_rf16(self):
        """RF16 - Verifica che la soglia massima del ciclo vita dei mezzi sia 400.000 km."""
        m = Mezzo(targa="CRI 400 AA", tipo="Ambulanza", chilometraggioTotale=399000)
        self.assertFalse(m.isDismesso())
        m.chilometraggioTotale = 400000
        self.assertTrue(m.isDismesso())
        m.chilometraggioTotale = 450000
        self.assertTrue(m.isDismesso())

    def test_turno_luoghi_separati_e_dati_paziente_uc7(self):
        """UC 7 - Verifica separazione luogo prelevamento/destinazione e dati paziente/CF."""
        t = Turno(
            id="T_UC7_1",
            data="2026-11-20",
            oraInizio="08:00",
            oraFine="12:00",
            luogoPrelevamento="Ospedale San Camillo",
            luogoDestinazione="Clinica Villa Pia",
            paziente_nome="Mario",
            paziente_cognome="Verdi",
            paziente_cf="VRDMRA80A01H501Z"
        )
        self.assertEqual(t.luogoPrelevamento, "Ospedale San Camillo")
        self.assertEqual(t.luogoDestinazione, "Clinica Villa Pia")
        self.assertIn("Ospedale San Camillo", t.luogo)
        self.assertIn("Clinica Villa Pia", t.luogo)
        self.assertEqual(t.paziente_nome, "Mario")
        self.assertEqual(t.paziente_cognome, "Verdi")
        self.assertEqual(t.paziente_cf, "VRDMRA80A01H501Z")
        self.assertEqual(t.calcola_durata_ore(), 4.0)
        
        d = t.to_dict()
        self.assertEqual(d["luogoPrelevamento"], "Ospedale San Camillo")
        self.assertEqual(d["paziente_cf"], "VRDMRA80A01H501Z")

    def test_limite_ore_giornaliere_12h(self):
        """Regola di Business: Impedire a un volontario/referente turni che superino le 12 ore giornaliere."""
        ctrl = GestioneTurniController()
        v = Volontario(cod_fiscale="RSSMRA85M01H501Z", nome="Mario", cognome="Rossi")
        
        # Turno 1: 8 ore (08:00 - 16:00)
        t1 = Turno(id="T_12H_1", data="2026-11-25", oraInizio="08:00", oraFine="16:00", personeRichieste=2)
        # Turno 2: 5 ore (17:00 - 22:00) nella stessa data (8 + 5 = 13 > 12)
        t2 = Turno(id="T_12H_2", data="2026-11-25", oraInizio="17:00", oraFine="22:00", personeRichieste=2)
        # Turno 3: 3 ore (18:00 - 21:00) nella stessa data (8 + 3 = 11 <= 12)
        t3 = Turno(id="T_12H_3", data="2026-11-25", oraInizio="18:00", oraFine="21:00", personeRichieste=2)

        # Assegniamo turno 1 al volontario
        v.turni_assegnati.append(t1)
        t1.volontari_assegnati.append(v)

        # Verifica limite
        self.assertFalse(ctrl.verificaLimiteOreGiornaliere(v, t2))
        self.assertTrue(ctrl.verificaLimiteOreGiornaliere(v, t3))

        # Tentativo di prenotazione t2 deve essere bloccato
        sistema = Sistema()
        sistema.turni = [t1, t2]
        sistema.volontari = [v]
        ok_p = ctrl.prenotaTurno(t2.codice, v.cod_fiscale, sistema=sistema)
        self.assertFalse(ok_p)
        self.assertNotIn(v, t2.volontari_assegnati)

    def test_capacita_massima_corso_uc10(self):
        """UC 10 - Verifica dati estesi del corso e blocco iscrizione al raggiungimento di maxPartecipanti."""
        ctrl = GestioneFormazioneController()
        corso = Corso(
            id="C_CAP_1",
            titolo="Corso Trauma e Maxiemergenze",
            direttore="Dott.ssa Laura Galli",
            luogo="Aula Magna CRI Roma",
            orari="Sabato e Domenica 09:00 - 18:00",
            requisitiIscrizione="BLSD Base attivo",
            maxPartecipanti=2
        )
        self.assertEqual(corso.direttore, "Dott.ssa Laura Galli")
        self.assertEqual(corso.maxPartecipanti, 2)
        self.assertFalse(corso.isCompleto())

        v1 = Volontario(cod_fiscale="CF001", nome="V1", cognome="Uno")
        v2 = Volontario(cod_fiscale="CF002", nome="V2", cognome="Due")
        v3 = Volontario(cod_fiscale="CF003", nome="V3", cognome="Tre")

        self.assertTrue(ctrl.iscriviVolontario(v1, corso))
        self.assertTrue(ctrl.iscriviVolontario(v2, corso))
        self.assertTrue(corso.isCompleto())

        # Il 3° volontario non può iscriversi perché il corso è completo
        self.assertFalse(ctrl.iscriviVolontario(v3, corso))
        self.assertEqual(len(corso.partecipanti), 2)
        self.assertNotIn(v3, corso.partecipanti)

    def test_backup_periodico_rf23(self):
        """RF23 - Procedura di backup periodico del sistema e serializzazione stato."""
        from BackupService import BackupService
        import tempfile
        import shutil

        temp_backup_dir = tempfile.mkdtemp()
        try:
            service = BackupService(backup_dir=temp_backup_dir, max_backups=3)
            sistema = Sistema()
            success, filepath = service.crea_backup(sistema)
            self.assertTrue(success)
            self.assertTrue(os.path.isfile(filepath))
            self.assertTrue(os.path.getsize(filepath) > 0)

            # Test backup delegato da Sistema
            sistema.backup_service = service
            s_ok, s_path = sistema.esegui_backup()
            self.assertTrue(s_ok)
            self.assertTrue(os.path.exists(s_path))
        finally:
            shutil.rmtree(temp_backup_dir, ignore_errors=True)

    def test_promemoria_servizio_24h_rnf4(self):
        """RNF4 - Notifica Promemoria Servizio inviata 24 ore prima dell'inizio del turno."""
        from datetime import datetime, timedelta
        sistema = Sistema()
        v = Volontario(cod_fiscale="RSSMRA85M01H501Z", nome="Mario", cognome="Rossi", email="mario.rossi@cri.it")
        sistema.volontari = [v]

        domani = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        t_domani = Turno(
            id="T_NOTIF_24H",
            data=domani,
            oraInizio="10:00",
            oraFine="16:00",
            luogoPrelevamento="Sede Centrale",
            luogoDestinazione="Presidio Ospedaliero"
        )
        t_domani.aggiungiVolontario(v, "Soccorritore")
        sistema.turni = [t_domani]

        # Esecuzione invio promemoria
        notificati = sistema.invia_promemoria_servizi_24h()
        self.assertEqual(len(notificati), 1)
        self.assertEqual(notificati[0]["id_turno"], "T_NOTIF_24H")
        self.assertEqual(notificati[0]["volontario_cf"], "RSSMRA85M01H501Z")
        self.assertTrue(any("T_NOTIF_24H_RSSMRA85M01H501Z" in k for k in sistema.promemoria_inviati))

        # Chiamate successive non devono re-inviare notifiche duplicate
        duplicati = sistema.invia_promemoria_servizi_24h()
        self.assertEqual(len(duplicati), 0)

    def test_permessi_referente_turni_e_flotta(self):
        """Verifica che la creazione/eliminazione turni e l'aggiunta mezzi siano permesse solo ai referenti."""
        turni_ctrl = GestioneTurniController()
        flotta_ctrl = GestioneFlottaController()

        volontario = Volontario(cod_fiscale="CF_VOL_TEST", nome="Vol", cognome="Semplice")
        referente = Referente(cod_fiscale="CF_REF_TEST", nome="Ref", cognome="Coordinatore")

        t = Turno(id="T_PERM_1", data="2026-11-20")
        m = Mezzo(targa="CRI 777 XY", tipo="Ambulanza Tipo A")

        # Volontario semplice deve fallire
        self.assertFalse(turni_ctrl.creaTurno(t, utente=volontario))
        self.assertFalse(turni_ctrl.eliminaTurno(t.codice, utente=volontario))
        self.assertFalse(flotta_ctrl.aggiungiMezzo(m, utente=volontario))

        # Referente deve avere successo
        self.assertTrue(turni_ctrl.creaTurno(t, utente=referente))
        self.assertTrue(flotta_ctrl.aggiungiMezzo(m, utente=referente))
        self.assertTrue(turni_ctrl.eliminaTurno(t.codice, utente=referente))


if __name__ == "__main__":
    unittest.main()




