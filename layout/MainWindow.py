# main_window.py
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QTextEdit
from Sistema import Sistema
from Referente import Referente
from Volontario import Volontario
from Mezzo import Mezzo
from Turno import Turno
from layout.modifica_dati_dialog import ModificaDatiDialog

# contiene tutta la logica dell’interfaccia e la creazione del sistema
class MainWindow(QWidget):
    def __init__(self, sistema):
        super().__init__()
        self.sistema = sistema

        # --- Estetica finestra ---
        self.setWindowTitle("🚑 Gestione Volontari - Croce Rossa Italiana")
        self.resize(600, 500)  # larghezza x altezza

        # --- Styling globale (tema scuro) ---
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: "Helvetica Neue", Arial;
                font-size: 14px;
            }
            QPushButton {
                background-color: #444;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QTextEdit {
                background-color: #2e2e2e;
                border: 1px solid #666;
                padding: 4px;
            }
        """)

        # --- Layout ---
        layout = QVBoxLayout()

        self.label = QLabel("🔧 Sistema CRI inizializzato.\n📌 Clicca un'operazione per iniziare.")
        layout.addWidget(self.label)

        btn_riepilogo = QPushButton("📋 Stampa Riepilogo")
        btn_riepilogo.clicked.connect(self.stampa_riepilogo)
        layout.addWidget(btn_riepilogo)

        btn_report = QPushButton("🧾 Report Volontario")
        btn_report.clicked.connect(self.stampa_report_volontario)
        layout.addWidget(btn_report)

        btn_modifica_dati = QPushButton("✏️ Modifica Dati Personali")
        btn_modifica_dati.clicked.connect(self.modifica_dati_volontario)
        layout.addWidget(btn_modifica_dati)

        self.riepilogo_box = QTextEdit()
        self.riepilogo_box.setReadOnly(True)
        layout.addWidget(self.riepilogo_box)

        self.setLayout(layout)

    def setup_sistema(self):
        sistema = Sistema()

        referente = Referente(
            cod_fiscale=1,
            nome="Luca",
            cognome="Rossi",
            email="luca.rossi@example.com",
            nascita="1980-03-15",
            telefono="1234567890",
            curriculum="curriculum.pdf",
            patenti=["B"],
            formazione=[],
            compagnia_appartenenza="CRI Roma",
            disponibilita=["Lunedì", "Venerdì"],
            area_gestita="Formazione"
        )

        volontario = Volontario(
            cod_fiscale=2,
            nome="Anna",
            cognome="Verdi",
            email="anna.verdi@example.com",
            nascita="1995-07-10",
            telefono="0987654321",
            curriculum="cv_anna.pdf",
            patenti=["B"],
            formazione=[],
            compagnia_appartenenza="CRI Roma",
            disponibilita=["Lunedì", "Mercoledì"],
            ruolo="volontario"
        )

        sistema.assegna_referente(volontario.cod_fiscale, referente.cod_fiscale)
        sistema.aggiungi_volontario(referente)
        sistema.aggiungi_volontario(volontario)

        mezzo = Mezzo(
            targa="AB123CD",
            tipo="Ambulanza",
            chilometraggio=50000,
            stato=["Pulito", "Revisione OK"],
            dispositivi_richiesti=["Defibrillatore", "Barelle"],
            checklist=["Controllo olio", "Presenza DPI"]
        )
        sistema.aggiungi_mezzo(mezzo)

        from Corso import Corso
        corso = Corso(
            id="C01",
            nome="Trauma Base",
            dataInizio="2025-09-01",
            esito=False,
            dataFine="2025-09-15",
            checklist=[
                {"item": "Materiale consegnato", "completato": False},
                {"item": "Firma partecipanti", "completato": False}
            ],
            titolo="Corso Base Trauma",
            scadenza="2026-09-01"
        )
        sistema.aggiungi_corso(corso)
        sistema.carica_corso_al_volontario(volontario.cod_fiscale, corso)
        referente.attesta_partecipazione(volontario, corso)

        turno = Turno(
            id_turno=301,
            data="2025-09-10",
            fascia_oraria="08:00 - 14:00",
            tipoServizio="A",
            personeRichieste="1",
            checklist=False,
            luogo="CRI Roma",
            paziente="Mario Rossi",
            tempoExtra="30 min",
            dispositivi_richiesti=["Defibrillatore"],
            corso_richiesto="Trauma Base"
        )
        sistema.aggiungi_turno(turno)
        sistema.assegna_turno(volontario.cod_fiscale, turno)
        sistema.assegna_mezzo_a_turno(mezzo, turno)
        turno.completa_checklist()
        turno.cambia_stato("Confermato")
        volontario.compila_report_turno(turno, 6.0)

        return sistema

    def stampa_riepilogo(self):
        testo = self.sistema.riepilogo_testuale()
        self.riepilogo_box.setText(testo)

    def stampa_report_volontario(self):
        volontario = self.sistema.get_volontario(2)
        if volontario:
            testo = self.sistema.stampa_report_volontario(volontario.cod_fiscale)
            self.riepilogo_box.setText(testo)
        else:
            QMessageBox.warning(self, "Errore", "Volontario non trovato.")

    def modifica_dati_volontario(self):
        volontario = self.sistema.get_volontario(2)  # ID hardcoded per ora

        if not volontario:
            QMessageBox.warning(self, "Errore", "Volontario non trovato.")
            return

        dialog = ModificaDatiDialog(volontario)
        if dialog.exec_():
            volontario.aggiorna_firestore()
            QMessageBox.information(self, "Successo", "✅ Dati aggiornati.")
