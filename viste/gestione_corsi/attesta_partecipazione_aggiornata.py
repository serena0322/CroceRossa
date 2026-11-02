"""VistaAttestaPartecipazione (GestioneCorsi): AttestaPartecipazione."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView, QPushButton
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from attivita.corso import Corso


class VistaAttestaPartecipazione(QWidget):
    def __init__(self, corso: Corso, parent=None):        # create(Corso): void
        super(VistaAttestaPartecipazione, self).__init__(parent)
        self.corso = corso

        d = self.corso.getDati()
        self.setWindowTitle(f"Attesta partecipazione – {d['codice']}")
        self.resize(460, 380)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Seleziona i Volontari che hanno superato il corso:</b>"))

        self.list_iscritti = QListView(self)
        layout.addWidget(self.list_iscritti)

        btn_conferma = QPushButton("Conferma")
        btn_conferma.clicked.connect(self.conferma_superati_click)
        layout.addWidget(btn_conferma)

        self.setLayout(layout)
        self.load_iscritti()

    def load_iscritti(self) -> None:
        modello = QStandardItemModel(self.list_iscritti)
        for v in Corso().attestaPartecipazione(self.corso):
            d = v.getDati()
            item = QStandardItem(f"{d['nome']} {d['cognome']}")   # solo nome e cognome
            item.setCheckable(True)
            item.setCheckState(Qt.Unchecked)
            item.setEditable(False)
            item.setData(v, Qt.UserRole)                          # il Volontario della riga
            modello.appendRow(item)
        self.list_iscritti.setModel(modello)

    def conferma_superati_click(self) -> None:
        modello = self.list_iscritti.model()
        superati = []
        for row in range(modello.rowCount()):
            item = modello.item(row)
            if item.checkState() == Qt.Checked:
                superati.append(item.data(Qt.UserRole))

        Corso().selezionaSuperati(self.corso, superati)
        self.close()

