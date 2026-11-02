"""VistaRegistrazioneVolontario (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 104).
Layout a due colonne:
- Titolo 'Registrazione Volontario'
- Campi:
    Nome
    Cognome
    Codice fiscale
    E-mail
    Telefono
    Comitato
    Password (con dicitura 'Almeno 6 caratteri alfanumerici')
- Banner di errore (es. 'E-mail già usata da un altro account.')
- Pulsante 'Registrati' centrato
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton
)
from utenti.volontario import Volontario
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaRegistrazioneVolontario(QWidget):
    def __init__(self, parent=None):
        super(VistaRegistrazioneVolontario, self).__init__(parent)
        self.setWindowTitle("Registrazione Volontario")
        self.resize(520, 500)

        self.qlines: dict[str, QLineEdit] = {}
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Intestazione come mockup pag. 104: "Registrazione Volontario"

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(8)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        row = 0

        def add_row(key: str, label_text: str, default_val: str = "", is_pwd: bool = False):
            nonlocal row
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 13px; font-weight: 500;")
            txt = QLineEdit(self)
            txt.setText(str(default_val))
            if is_pwd:
                txt.setEchoMode(QLineEdit.Password)
            self.qlines[key] = txt
            grid.addWidget(lbl, row, 0)
            grid.addWidget(txt, row, 1)
            row += 1

        add_row("nome", "Nome", "")
        add_row("cognome", "Cognome", "")
        add_row("codiceFiscale", "Codice fiscale", "")
        add_row("email", "E-mail", "")
        add_row("telefono", "Telefono", "")
        add_row("comitato", "Comitato", "Ancona")
        add_row("password", "Password", "", is_pwd=True)

        main_layout.addLayout(grid)

        lbl_sotto_pwd = QLabel("Almeno 6 caratteri alfanumerici.")
        lbl_sotto_pwd.setStyleSheet("font-size: 11px; color: #718096;")
        main_layout.addWidget(lbl_sotto_pwd)

        # Banner errore
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        # Pulsante centrato "Registrati"
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn = QPushButton("Registrati")
        btn.setFixedWidth(200)
        btn.clicked.connect(self.registra_click)
        btn_layout.addWidget(btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def registra_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        nome = self.qlines["nome"].text().strip()
        cognome = self.qlines["cognome"].text().strip()
        cf = self.qlines["codiceFiscale"].text().strip()
        em = self.qlines["email"].text().strip()
        tel = self.qlines["telefono"].text().strip()
        com = self.qlines["comitato"].text().strip()
        pwd = self.qlines["password"].text().strip()

        ok = Volontario().inserisciInformazioni(nome, cognome, cf, em, tel, com, pwd)
        if ok:
            self.close()
        else:
            mostra_errore(self.lbl_errore, "E-mail già usata da un altro account o dati non validi.")
