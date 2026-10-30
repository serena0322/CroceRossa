"""VistaPrenotatiTurno (GestioneTurni) secondo le specifiche del PDF e mockup (pag. 10)."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView, QMessageBox
from PyQt5.QtCore import QStringListModel
from attivita.turno import Turno


class VistaPrenotatiTurno(QWidget):
    def __init__(self, turno: Turno, parent=None):
        super(VistaPrenotatiTurno, self).__init__(parent)
        self.turno = turno
        self.list_prenotati = QListView(self)

        d = self.turno.getDati()
        self.setWindowTitle(f"Prenotati al turno {d['codice']}")
        self.resize(500, 360)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>Volontari prenotati per il turno {d['codice']}:</b>"))
        layout.addWidget(self.list_prenotati)

        self.setLayout(layout)
        self.load_prenotati()

    def load_prenotati(self) -> None:
        prenotati = Turno().visualizzaPrenotatiTurno(self.turno)
        model = QStringListModel()
        righe = []
        for v in prenotati:
            d = v.getDati()
            righe.append(f"{d.get('nome', '')} {d.get('cognome', '')} | {d.get('email', '')} | Tel: {d.get('telefono', '')}")
        if not righe:
            righe = ["Nessun volontario prenotato."]
        model.setStringList(righe)
        self.list_prenotati.setModel(model)
