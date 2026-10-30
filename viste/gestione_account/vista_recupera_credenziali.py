"""VistaRecuperaCredenziali (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 4)."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from utenti.volontario import Volontario


class VistaRecuperaCredenziali(QWidget):
    def __init__(self, parent=None):
        super(VistaRecuperaCredenziali, self).__init__(parent)
        self.setWindowTitle("Recupero password")
        self.resize(360, 180)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Inserisci l'e-mail con cui ti sei registrato:"))
        self.email = QLineEdit(self)
        layout.addWidget(self.email)

        btn_invia = QPushButton("Invia nuova password")
        btn_invia.clicked.connect(self.invia_click)
        layout.addWidget(btn_invia)

        self.setLayout(layout)

    def invia_click(self) -> None:
        em = self.email.text().strip()
        if not em:
            QMessageBox.warning(self, "Attenzione", "Inserire un indirizzo e-mail.")
            return

        ok = Volontario().inserisciEmail(em)
        if ok:
            QMessageBox.information(self, "Recupero password", "Nuova password inviata via e-mail.")
            self.close()
        else:
            QMessageBox.critical(self, "Errore", "E-mail non registrata.")
