"""VistaAttestaPartecipazione (GestioneCorsi) secondo le specifiche del PDF e mockup (pag. 12)."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from attivita.corso import Corso


class VistaAttestaPartecipazione(QWidget):
    def __init__(self, corso: Corso, callback=None, parent=None):
        super(VistaAttestaPartecipazione, self).__init__(parent)
        self.corso = corso
        self.callback = callback
        self.iscritti = []

        d = self.corso.getDati()
        self.setWindowTitle(f"Attesta partecipazione – {d['codice']}")
        self.resize(460, 380)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Seleziona i Volontari che hanno superato il corso:</b>"))

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        btn_conferma = QPushButton("Conferma")
        btn_conferma.clicked.connect(self.conferma_superati_click)
        layout.addWidget(btn_conferma)

        self.setLayout(layout)
        self.load_iscritti()

    def load_iscritti(self) -> None:
        self.iscritti = Corso().attestaPartecipazione(self.corso)
        self.list_widget.clear()
        for v in self.iscritti:
            d = v.getDati()
            item = QListWidgetItem(f"{d.get('nome', '')} {d.get('cognome', '')} ({d.get('email', '')})")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)

    def conferma_superati_click(self) -> None:
        superati = []
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item.checkState() == Qt.Checked:
                superati.append(self.iscritti[row])

        Corso().selezionaSuperati(self.corso, superati)
        QMessageBox.information(
            self, "Attestazione",
            f"Attestazione registrata per {len(superati)} volontari superati su {len(self.iscritti)}."
        )
        if self.callback:
            self.callback()
        self.close()
