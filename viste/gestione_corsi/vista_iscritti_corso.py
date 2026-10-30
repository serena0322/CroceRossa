"""VistaIscrittiCorso (GestioneCorsi) secondo le specifiche del PDF e mockup (pag. 12)."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView
from PyQt5.QtCore import QStringListModel
from attivita.corso import Corso


class VistaIscrittiCorso(QWidget):
    def __init__(self, corso: Corso, parent=None):
        super(VistaIscrittiCorso, self).__init__(parent)
        self.corso = corso
        self.list_iscritti = QListView(self)

        d = self.corso.getDati()
        self.setWindowTitle(f"Iscritti al corso {d['codice']}")
        self.resize(500, 360)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>Iscritti al corso {d['nome']} ({d['codice']}):</b>"))
        layout.addWidget(self.list_iscritti)

        self.setLayout(layout)
        self.load_iscritti()

    def load_iscritti(self) -> None:
        iscritti = Corso().visualizzaIscrittiCorso(self.corso)
        model = QStringListModel()
        righe = []
        for v in iscritti:
            d = v.getDati()
            righe.append(f"{d.get('nome', '')} {d.get('cognome', '')} | {d.get('email', '')} | Tel: {d.get('telefono', '')}")
        if not righe:
            righe = ["Nessun volontario iscritto."]
        model.setStringList(righe)
        self.list_iscritti.setModel(model)
