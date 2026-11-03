"""VistaRegistrazioneReferente (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 104).
Layout a due colonne:
- Titolo 'Registrazione Referente'
- Campi:
    Settore gestito
    E-mail
    Telefono
    Comitato
    Password (con dicitura 'Almeno 6 caratteri alfanumerici')
    Codice autorizzazione
- Banner di errore (es. 'Codice di autorizzazione non valido.')
- Pulsante 'Registrati' centrato
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton
)
from utenti.referente import Referente
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaRegistrazioneReferente(QWidget):
    def __init__(self, parent=None):
        super(VistaRegistrazioneReferente, self).__init__(parent)
        self.setWindowTitle("Registrazione Referente")
        self.resize(520, 500)

        self.qlines: dict[str, QLineEdit] = {}
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Intestazione come mockup pag. 104: "Registrazione Referente"

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
            txt.setText(default_val)
            if is_pwd:
                txt.setEchoMode(QLineEdit.Password)
            self.qlines[key] = txt
            grid.addWidget(lbl, row, 0)
            grid.addWidget(txt, row, 1)
            row += 1

        add_row("settoreGestito", "Settore gestito", "Sanitario")
        add_row("email", "E-mail", "")
        add_row("telefono", "Telefono", "")
        add_row("comitato", "Comitato", "Ancona")
        add_row("password", "Password", "", is_pwd=True)
        add_row("codiceAutorizzazione", "Codice autorizzazione", "")

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
        settore = self.qlines["settoreGestito"].text().strip()
        em = self.qlines["email"].text().strip()
        tel = self.qlines["telefono"].text().strip()
        com = self.qlines["comitato"].text().strip()
        pwd = self.qlines["password"].text().strip()
        cod = self.qlines["codiceAutorizzazione"].text().strip()

        ok = Referente().inserisciInformazioni(settore, em, tel, com, pwd, cod)
        if ok:
            self.close()
        else:
            mostra_errore(self.lbl_errore, "Codice di autorizzazione non valido o informazioni non valide.")
