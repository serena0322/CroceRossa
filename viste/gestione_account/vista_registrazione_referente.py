"""VistaRegistrazioneReferente (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 5)."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from utenti.referente import Referente


class VistaRegistrazioneReferente(QWidget):
    def __init__(self, parent=None):
        super(VistaRegistrazioneReferente, self).__init__(parent)
        self.setWindowTitle("Registrazione Referente")
        self.resize(400, 380)

        self.qlines: dict[str, QLineEdit] = {}
        self.v_layout = QVBoxLayout(self)

        self.add_info_text("settoreGestito", "Settore gestito")
        self.add_info_text("email", "E-mail")
        self.add_info_text("telefono", "Telefono")
        self.add_info_text("comitato", "Comitato")
        self.add_info_text("password", "Password")
        self.add_info_text("codiceAutorizzazione", "Codice di autorizzazione fornito dal Comitato")

        btn = QPushButton("Registrati")
        btn.clicked.connect(self.registra_click)
        self.v_layout.addWidget(btn)

        self.setLayout(self.v_layout)

    def add_info_text(self, chiave: str, etichetta: str) -> None:
        self.v_layout.addWidget(QLabel(f"{etichetta}:"))
        txt = QLineEdit(self)
        if chiave == "password":
            txt.setEchoMode(QLineEdit.Password)
        self.qlines[chiave] = txt
        self.v_layout.addWidget(txt)

    def registra_click(self) -> None:
        settore = self.qlines["settoreGestito"].text().strip()
        em = self.qlines["email"].text().strip()
        tel = self.qlines["telefono"].text().strip()
        com = self.qlines["comitato"].text().strip()
        pwd = self.qlines["password"].text().strip()
        cod = self.qlines["codiceAutorizzazione"].text().strip()

        ok = Referente().inserisciInformazioni(settore, em, tel, com, pwd, cod)
        if ok:
            QMessageBox.information(self, "Registrazione", "Account Referente creato con successo.")
            self.close()
        else:
            QMessageBox.critical(self, "Errore", "Informazioni non valide o codice di autorizzazione non presente.")
