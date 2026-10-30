"""VistaInserisciPatente (GestionePatenti) secondo le specifiche del PDF e mockup (pag. 7)."""
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QDateEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate
from utenti.patente import Patente
from utenti.volontario import Volontario


class VistaInserisciPatente(QWidget):
    def __init__(self, codice: str, volontario: Volontario, callback, parent=None):
        super(VistaInserisciPatente, self).__init__(parent)
        self.codice = codice
        self.volontario = volontario
        self.callback = callback

        self.setWindowTitle("Nuova patente")
        self.resize(360, 240)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>Codice patente:</b> {self.codice}"))

        layout.addWidget(QLabel("Tipo patente:"))
        self.combo = QComboBox(self)
        self.combo.addItems(["CRI 1", "CRI 2", "CRI 3", "CRI 4", "CRI 5", "B", "C", "D"])
        layout.addWidget(self.combo)

        layout.addWidget(QLabel("Data di scadenza:"))
        self.data_scadenza = QDateEdit(self)
        self.data_scadenza.setDate(QDate.currentDate().addYears(5))
        self.data_scadenza.setCalendarPopup(True)
        layout.addWidget(self.data_scadenza)

        btn_salva = QPushButton("Salva")
        btn_salva.clicked.connect(self.aggiungi_patente)
        layout.addWidget(btn_salva)

        self.setLayout(layout)

    def aggiungi_patente(self) -> None:
        tipo = self.combo.currentText()
        qd = self.data_scadenza.date()
        scadenza = date(qd.year(), qd.month(), qd.day())

        Patente().inserisciDatiPatente(self.codice, tipo, scadenza, self.volontario)
        QMessageBox.information(self, "Nuova patente", "Patente inserita con successo.")
        if self.callback:
            self.callback()
        self.close()
