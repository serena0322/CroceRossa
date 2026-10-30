"""VistaIscrizioni (IscrizioneCorsi) secondo le specifiche del PDF e mockup (pag. 14)."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListView,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import QStringListModel
from utenti.volontario import Volontario
from attivita.iscrizione import Iscrizione


class VistaIscrizioni(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaIscrizioni, self).__init__(parent)
        self.volontario = volontario
        self.iscrizioni: list[Iscrizione] = []

        self.setWindowTitle("Le mie iscrizioni")
        self.resize(500, 360)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Iscrizioni attive ai corsi:</b>"))

        self.list_view = QListView(self)
        layout.addWidget(self.list_view)

        btn_annulla = QPushButton("Annulla iscrizione")
        btn_annulla.clicked.connect(self.annulla_iscrizione_click)
        layout.addWidget(btn_annulla)

        self.setLayout(layout)
        self.load_iscrizioni()

    def load_iscrizioni(self) -> None:
        self.iscrizioni = self.volontario.visualizzaIscrizioni()
        self.update_ui()

    def update_ui(self) -> None:
        model = QStringListModel()
        righe = []
        for i in self.iscrizioni:
            d = i.getDatiCorso()
            righe.append(f"{d['nome']} | Codice: {d['codice']} | Inizio: {d['dataInizio']:%d/%m/%Y} | Luogo: {d['luogo']}")
        model.setStringList(righe)
        self.list_view.setModel(model)

    def annulla_iscrizione_click(self) -> None:
        idx = self.list_view.currentIndex().row()
        if not (0 <= idx < len(self.iscrizioni)):
            QMessageBox.warning(self, "Attenzione", "Selezionare un'iscrizione dall'elenco.")
            return

        iscr = self.iscrizioni[idx]
        ok = self.volontario.annullaIscrizione(iscr)
        if ok:
            QMessageBox.information(self, "Annullamento", "Iscrizione annullata con successo.")
            self.load_iscrizioni()
        else:
            QMessageBox.critical(self, "Annullamento non consentito", "Non è possibile annullare l'iscrizione a meno di 2 giorni dall'inizio del corso.")
