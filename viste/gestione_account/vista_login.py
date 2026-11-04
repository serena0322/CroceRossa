"""VistaLogin (GestioneAccount) conforme alle specifiche del PDF e mockup (pag. 104).
Layout:
- Intestazione 'Croce Rossa Ancona - Accesso'
- Titolo 'Accedi'
- Form a 2 colonne:
    E-mail
    Password
- Banner di errore (es. 'Credenziali non valide.')
- Pulsante 'Accedi' centrato
- Link / pulsante 'Password dimenticata?' centrato
- Separatore e riga orizzontale in basso con i due pulsanti:
    'Registrati come Volontario' e 'Registrati come Referente'
"""
from __future__ import annotations
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton
)
from utenti.volontario import Volontario
from utenti.referente import Referente
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaLogin(QWidget):
    def __init__(self, parent=None):
        super(VistaLogin, self).__init__(parent)
        self.setWindowTitle("Accedi")
        self.resize(520, 360)

        self.vista_home = None
        self.vista_recupero = None
        self.vista_reg_vol = None
        self.vista_reg_ref = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(12)

        # Titolo "Accedi"
        lbl_accedi = QLabel("<b>Accedi</b>")
        lbl_accedi.setStyleSheet("font-size: 18px; font-weight: bold; color: #1A202C; margin-bottom: 4px;")
        main_layout.addWidget(lbl_accedi)

        # Griglia E-mail e Password
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        lbl_email = QLabel("E-mail")
        lbl_email.setStyleSheet("font-size: 13px; font-weight: 500;")
        self.email = QLineEdit(self)
        self.email.setPlaceholderText("mario.rossi@gmail.com")
        grid.addWidget(lbl_email, 0, 0)
        grid.addWidget(self.email, 0, 1)

        lbl_pwd = QLabel("Password")
        lbl_pwd.setStyleSheet("font-size: 13px; font-weight: 500;")
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        grid.addWidget(lbl_pwd, 1, 0)
        grid.addWidget(self.password, 1, 1)

        main_layout.addLayout(grid)

        # Banner d'errore (es. 'Credenziali non valide.')
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        # Pulsante centrato "Accedi"
        btn_acc_layout = QHBoxLayout()
        btn_acc_layout.addStretch()
        btn_login = QPushButton("Accedi")
        btn_login.setFixedWidth(200)
        btn_login.clicked.connect(self.login_click)
        btn_acc_layout.addWidget(btn_login)
        btn_acc_layout.addStretch()
        main_layout.addLayout(btn_acc_layout)

        # Link "Password dimenticata?" centrato
        btn_rec_layout = QHBoxLayout()
        btn_rec_layout.addStretch()
        btn_recupera = QPushButton("Password dimenticata?")
        btn_recupera.setStyleSheet("background: transparent; border: none; color: #3182CE; font-weight: normal; text-decoration: underline;")
        btn_recupera.clicked.connect(self.recupera_credenziali_click)
        btn_rec_layout.addWidget(btn_recupera)
        btn_rec_layout.addStretch()
        main_layout.addLayout(btn_rec_layout)

        main_layout.addSpacing(8)
        
        reg_layout = QHBoxLayout()
        reg_layout.setSpacing(12)

        btn_reg_vol = QPushButton("Registrati come Volontario")
        btn_reg_vol.clicked.connect(self.registrazione_volontario_click)
        reg_layout.addWidget(btn_reg_vol, 1)

        btn_reg_ref = QPushButton("Registrati come Referente")
        btn_reg_ref.clicked.connect(self.registrazione_referente_click)
        reg_layout.addWidget(btn_reg_ref, 1)

        main_layout.addLayout(reg_layout)

        self.setLayout(main_layout)

    def login_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        email = self.email.text().strip()
        pwd = self.password.text().strip()
        if not email or not pwd:
            mostra_errore(self.lbl_errore, "Inserire e-mail e password.")
            return

        utente = Volontario().inserisciCredenziali(email, pwd)
        if utente is None:
            mostra_errore(self.lbl_errore, "Credenziali non valide.")
            return

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
