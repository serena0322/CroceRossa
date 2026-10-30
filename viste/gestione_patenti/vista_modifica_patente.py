"""VistaModificaPatente (GestionePatenti) secondo le specifiche del PDF e mockup (pag. 8)."""
from datetime import date
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDateEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QDate
from utenti.patente import Patente


class VistaModificaPatente(QWidget):
    def __init__(self, patente: Patente, callback, parent=None):
        super(VistaModificaPatente, self).__init__(parent)
        self.patente = patente
        self.callback = callback

        self.setWindowTitle("Modifica patente")
        self.resize(360, 220)

        d = self.patente.getDati()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>Codice:</b> {d['codice']}"))
        layout.addWidget(QLabel(f"<b>Tipo:</b> {d['tipo']}"))

        layout.addWidget(QLabel("Nuova data di scadenza:"))
        self.data_scadenza = QDateEdit(self)
        dt = d["dataScadenza"]
        self.data_scadenza.setDate(QDate(dt.year, dt.month, dt.day))
        self.data_scadenza.setCalendarPopup(True)
        layout.addWidget(self.data_scadenza)

        btn = QPushButton("Salva modifiche")
        btn.clicked.connect(self.salva_modifiche_click)
        layout.addWidget(btn)

        self.setLayout(layout)

    def salva_modifiche_click(self) -> None:
        qd = self.data_scadenza.date()
        scadenza = date(qd.year(), qd.month(), qd.day())
        Patente().inserisciModifiche(self.patente, scadenza)
        QMessageBox.information(self, "Modifica patente", "Data di scadenza aggiornata con successo.")
        if self.callback:
            self.callback()
        self.close()
