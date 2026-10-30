"""VistaPrenotazioni (PrenotazioneTurni) secondo le specifiche del PDF e mockup (pag. 13)."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListView,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import QStringListModel
from utenti.volontario import Volontario
from attivita.prenotazione import Prenotazione


class VistaPrenotazioni(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaPrenotazioni, self).__init__(parent)
        self.volontario = volontario
        self.prenotazioni: list[Prenotazione] = []

        self.setWindowTitle("Le mie prenotazioni")
        self.resize(500, 360)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Prenotazioni attive:</b>"))

        self.list_view = QListView(self)
        layout.addWidget(self.list_view)

        btn_annulla = QPushButton("Annulla prenotazione")
        btn_annulla.clicked.connect(self.annulla_prenotazione_click)
        layout.addWidget(btn_annulla)

        self.setLayout(layout)
        self.load_prenotazioni()

    def load_prenotazioni(self) -> None:
        self.prenotazioni = self.volontario.visualizzaPrenotazioni()
        self.update_ui()

    def update_ui(self) -> None:
        model = QStringListModel()
        righe = []
        for p in self.prenotazioni:
            d = p.getDatiTurno()
            righe.append(
                f"Data: {d['data']:%d/%m/%Y} | Ore: {d['oraInizio']:%H:%M}-{d['oraFine']:%H:%M} | "
                f"Codice turno: {d['codice']} | Luogo: {d['luogo']}"
            )
        model.setStringList(righe)
        self.list_view.setModel(model)

    def annulla_prenotazione_click(self) -> None:
        idx = self.list_view.currentIndex().row()
        if not (0 <= idx < len(self.prenotazioni)):
            QMessageBox.warning(self, "Attenzione", "Selezionare una prenotazione dall'elenco.")
            return

        prenotazione = self.prenotazioni[idx]
        ok = self.volontario.annullaPrenotazione(prenotazione)
        if ok:
            QMessageBox.information(self, "Annullamento", "Prenotazione annullata con successo.")
            self.load_prenotazioni()
        else:
            QMessageBox.critical(self, "Annullamento non consentito", "Non è possibile annullare una prenotazione a meno di 24 ore dall'inizio del turno.")
