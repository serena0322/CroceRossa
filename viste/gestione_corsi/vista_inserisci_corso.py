"""VistaInserisciCorso (GestioneCorsi) secondo le specifiche del PDF e mockup (pag. 11)."""
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate
from attivita.corso import Corso


class VistaInserisciCorso(QWidget):
    def __init__(self, codice: str, callback, parent=None):
        super(VistaInserisciCorso, self).__init__(parent)
        self.codice = codice
        self.callback = callback
        self.qlines: dict[str, QLineEdit] = {}

        self.setWindowTitle("Nuovo corso")
        self.resize(460, 480)

        self.v_layout = QVBoxLayout(self)
        self.v_layout.addWidget(QLabel(f"<b>Codice corso:</b> {self.codice}"))

        self.add_info_text("nome", "Nome corso")
        self.add_info_text("descrizione", "Descrizione")
        self.add_info_text("direttoreCorso", "Direttore del corso")

        self.v_layout.addWidget(QLabel("Tipo di corso:"))
        self.combo = QComboBox(self)
        self.combo.addItems(["Base", "Sanitario", "Soccorso", "Protezione Civile"])
        self.v_layout.addWidget(self.combo)

        self.v_layout.addWidget(QLabel("Data di inizio:"))
        self.data_inizio = QDateEdit(self)
        self.data_inizio.setDate(QDate.currentDate().addDays(7))
        self.data_inizio.setCalendarPopup(True)
        self.v_layout.addWidget(self.data_inizio)

        self.v_layout.addWidget(QLabel("Data di fine:"))
        self.data_fine = QDateEdit(self)
        self.data_fine.setDate(QDate.currentDate().addDays(14))
        self.data_fine.setCalendarPopup(True)
        self.v_layout.addWidget(self.data_fine)

        self.add_info_text("orario", "Orario di svolgimento")
        self.qlines["orario"].setText("20:00 - 23:00")

        self.add_info_text("luogo", "Luogo di svolgimento")
        self.add_info_text("postiTotali", "Numero di posti")
        self.qlines["postiTotali"].setText("20")

        btn = QPushButton("Salva")
        btn.clicked.connect(self.aggiungi_corso)
        self.v_layout.addWidget(btn)

        self.setLayout(self.v_layout)

    def add_info_text(self, chiave: str, etichetta: str) -> None:
        self.v_layout.addWidget(QLabel(f"{etichetta}:"))
        txt = QLineEdit(self)
        self.qlines[chiave] = txt
        self.v_layout.addWidget(txt)

    def aggiungi_corso(self) -> None:
        nome = self.qlines["nome"].text().strip()
        desc = self.qlines["descrizione"].text().strip()
        direttore = self.qlines["direttoreCorso"].text().strip()
        tipo = self.combo.currentText()

        q_i = self.data_inizio.date()
        d_inizio = date(q_i.year(), q_i.month(), q_i.day())
        q_f = self.data_fine.date()
        d_fine = date(q_f.year(), q_f.month(), q_f.day())

        orario = self.qlines["orario"].text().strip()
        luogo = self.qlines["luogo"].text().strip()

        try:
            posti = int(self.qlines["postiTotali"].text().strip())
        except ValueError:
            QMessageBox.critical(self, "Errore", "Il numero di posti deve essere un numero intero positivo.")
            return

        try:
            Corso().inserisciDatiCorso(
                self.codice, nome, desc, direttore, tipo,
                d_inizio, d_fine, orario, luogo, posti
            )
            QMessageBox.information(self, "Corso creato", f"Corso {self.codice} creato con successo.")
            if self.callback:
                self.callback()
            self.close()
        except ValueError as e:
            QMessageBox.critical(self, "Errore", str(e))
