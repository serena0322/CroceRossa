"""VistaLogin (GestioneAccount) conforme alle specifiche del PDF e diagrammi sequence."""
from __future__ import annotations
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from utenti.utente import Utente
from utenti.volontario import Volontario
from utenti.referente import Referente


class VistaLogin(QWidget):
    def __init__(self, parent=None):
        super(VistaLogin, self).__init__(parent)
        self.setWindowTitle("Croce Rossa Italiana - Login")
        self.resize(380, 260)

        self.vista_home = None
        self.vista_recupero = None
        self.vista_reg_vol = None
        self.vista_reg_ref = None

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Accedi alla piattaforma")
        title.setProperty("heading", "true")
        layout.addWidget(title)

        layout.addWidget(QLabel("E-mail"))
        self.txt_email = QLineEdit(self)
        self.txt_email.setPlaceholderText("mario.rossi@email.it")
        layout.addWidget(self.txt_email)

        layout.addWidget(QLabel("Password"))
        self.txt_password = QLineEdit(self)
        self.txt_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.txt_password)

        row_login = QHBoxLayout()
        self.btn_login = QPushButton("Accedi")
        self.btn_login.clicked.connect(self.login_click)
        row_login.addWidget(self.btn_login)

        self.btn_recupera = QPushButton("Password dimenticata?")
        self.btn_recupera.clicked.connect(self.recupera_credenziali_click)
        row_login.addWidget(self.btn_recupera)
        layout.addLayout(row_login)

        layout.addSpacing(10)
        lbl_non_hai = QLabel("Non hai un account?")
        lbl_non_hai.setStyleSheet("color: #718096; font-size: 12px;")
        layout.addWidget(lbl_non_hai)

        reg_layout = QHBoxLayout()
        self.btn_reg_vol = QPushButton("Registrati come Volontario")
        self.btn_reg_vol.clicked.connect(self.registrazione_volontario_click)
        reg_layout.addWidget(self.btn_reg_vol)

        self.btn_reg_ref = QPushButton("Registrati come Referente")
        self.btn_reg_ref.clicked.connect(self.registrazione_referente_click)
        reg_layout.addWidget(self.btn_reg_ref)
        layout.addLayout(reg_layout)

        self.setLayout(layout)

    def login_click(self) -> None:
        email = self.txt_email.text().strip()
        pwd = self.txt_password.text().strip()
        if not email or not pwd:
            QMessageBox.warning(self, "Attenzione", "Inserire e-mail e password.")
            return

        utente = Volontario().inserisciCredenziali(email, pwd)
        if utente is None:
            QMessageBox.critical(self, "Errore", "Credenziali non valide.")
            return

        # Apri home in base al tipo di utente
        if isinstance(utente, Referente):
            from viste.gestione_account.vista_home_referente import VistaHomeReferente
            self.vista_home = VistaHomeReferente(utente)
        else:
            from viste.gestione_account.vista_home_volontario import VistaHomeVolontario
            self.vista_home = VistaHomeVolontario(utente)

        self.vista_home.show()
        self.close()

    def recupera_credenziali_click(self) -> None:
        from viste.gestione_account.vista_recupera_credenziali import VistaRecuperaCredenziali
        self.vista_recupero = VistaRecuperaCredenziali()
        self.vista_recupero.show()

    def registrazione_volontario_click(self) -> None:
        from viste.gestione_account.vista_registrazione_volontario import VistaRegistrazioneVolontario
        self.vista_reg_vol = VistaRegistrazioneVolontario()
        self.vista_reg_vol.show()

    def registrazione_referente_click(self) -> None:
        from viste.gestione_account.vista_registrazione_referente import VistaRegistrazioneReferente
        self.vista_reg_ref = VistaRegistrazioneReferente()
        self.vista_reg_ref.show()
