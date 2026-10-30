"""VistaGestisciPatenti (GestionePatenti) secondo le specifiche del PDF e mockup (pag. 7)."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListView, QPushButton, QMessageBox
)
from PyQt5.QtCore import QStringListModel
from utenti.volontario import Volontario
from utenti.patente import Patente


class VistaGestisciPatenti(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaGestisciPatenti, self).__init__(parent)
        self.volontario = volontario
        self.patenti: list[Patente] = []
        self.vista_inserisci = None
        self.vista_modifica = None

        self.setWindowTitle("Le mie patenti")
        self.resize(500, 380)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Elenco patenti:</b>"))

        self.list_view = QListView(self)
        layout.addWidget(self.list_view)

        codice_row = QHBoxLayout()
        codice_row.addWidget(QLabel("Codice patente:"))
        self.codice = QLineEdit(self)
        self.codice.textChanged.connect(self.update_ui)
        codice_row.addWidget(self.codice)
        layout.addLayout(codice_row)

        btn_row = QHBoxLayout()
        self.btn_ins = QPushButton("Inserisci")
        self.btn_ins.clicked.connect(self.show_new)
        btn_row.addWidget(self.btn_ins)

        self.btn_mod = QPushButton("Modifica")
        self.btn_mod.clicked.connect(self.show_modifica)
        btn_row.addWidget(self.btn_mod)

        self.btn_rim = QPushButton("Rimuovi")
        self.btn_rim.clicked.connect(self.rimuovi_patente)
        btn_row.addWidget(self.btn_rim)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.load_patenti()

    def load_patenti(self) -> None:
        self.patenti = self.volontario.visualizzaPatenti()
        self.update_ui()

    def update_ui(self) -> None:
        model = QStringListModel()
        righe = []
        for p in self.patenti:
            d = p.getDati()
            righe.append(f"{d['codice']} | Tipo: {d['tipo']} | Scadenza: {d['dataScadenza']:%d/%m/%Y}")
        model.setStringList(righe)
        self.list_view.setModel(model)

        ha_codice = bool(self.codice.text().strip())
        self.btn_ins.setEnabled(ha_codice)
        self.btn_mod.setEnabled(ha_codice)
        self.btn_rim.setEnabled(ha_codice)

    def show_new(self) -> None:
        cod = self.codice.text().strip()
        if not Patente().inserisciPatente(cod):
            QMessageBox.critical(self, "Errore", f"Patente {cod} già presente nel sistema.")
            return

        from viste.gestione_patenti.vista_inserisci_patente import VistaInserisciPatente
        self.vista_inserisci = VistaInserisciPatente(cod, self.volontario, self.load_patenti)
        self.vista_inserisci.show()

    def show_modifica(self) -> None:
        cod = self.codice.text().strip()
        dati_p = Patente().modificaPatente(cod, self.volontario)
        if not dati_p:
            QMessageBox.critical(self, "Errore", "Patente non trovata o non appartenente al tuo account.")
            return

        trovate = [p for p in self.patenti if p.getDati()["codice"] == cod]
        if not trovate:
            return
        from viste.gestione_patenti.vista_modifica_patente import VistaModificaPatente
        self.vista_modifica = VistaModificaPatente(trovate[0], self.load_patenti)
        self.vista_modifica.show()

    def rimuovi_patente(self) -> None:
        cod = self.codice.text().strip()
        ok = Patente().rimuoviPatente(cod, self.volontario)
        if ok:
            QMessageBox.information(self, "Rimozione", f"Patente {cod} rimossa con successo.")
            self.load_patenti()
        else:
            QMessageBox.critical(self, "Errore", "Patente non trovata o non rimovibile.")
