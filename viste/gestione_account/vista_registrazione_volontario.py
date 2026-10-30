"""VistaRegistrazioneVolontario (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 5)."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from utenti.volontario import Volontario


class VistaRegistrazioneVolontario(QWidget):
    def __init__(self, parent=None):
        super(VistaRegistrazioneVolontario, self).__init__(parent)
        self.setWindowTitle("Registrazione Volontario")
        self.resize(400, 380)

        self.qlines: dict[str, QLineEdit] = {}
        self.v_layout = QVBoxLayout(self)

        self.add_info_text("nome", "Nome")
        self.add_info_text("cognome", "Cognome")
        self.add_info_text("codiceFiscale", "Codice fiscale")
        self.add_info_text("email", "E-mail")
        self.add_info_text("telefono", "Telefono")
        self.add_info_text("comitato", "Comitato")
        self.add_info_text("password", "Password (almeno 6 caratteri alfanumerici)")

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
        nome = self.qlines["nome"].text().strip()
        cognome = self.qlines["cognome"].text().strip()
        cf = self.qlines["codiceFiscale"].text().strip()
        em = self.qlines["email"].text().strip()
        tel = self.qlines["telefono"].text().strip()
        com = self.qlines["comitato"].text().strip()
        pwd = self.qlines["password"].text().strip()

        ok = Volontario().inserisciInformazioni(nome, cognome, cf, em, tel, com, pwd)
        if ok:
            QMessageBox.information(self, "Registrazione", "Account Volontario creato con successo.")
            self.close()
        else:
            QMessageBox.critical(self, "Errore", "Informazioni non valide (verificare dati, formato CF/email, password o e-mail già usata).")
