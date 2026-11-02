"""VistaRecuperaCredenziali (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 104).
Layout a due colonne:
- Titolo 'Recupero password'
- Istruzione: 'Riceverai una nuova password all'indirizzo indicato.'
- Riga form: E-mail [line edit]
- Banner di errore (es. 'E-mail non registrata.')
- Pulsante 'Invia nuova password' centrato
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton
)
from utenti.volontario import Volontario
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaRecuperaCredenziali(QWidget):
    def __init__(self, parent=None):
        super(VistaRecuperaCredenziali, self).__init__(parent)
        self.setWindowTitle("Recupero password")
        self.resize(500, 260)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Intestazione come mockup pag. 104: "Recupero password"

        lbl_info = QLabel("Riceverai una nuova password all'indirizzo indicato.")
        lbl_info.setStyleSheet("font-size: 13px; color: #4A5568;")
        main_layout.addWidget(lbl_info)

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

        main_layout.addLayout(grid)

        # Banner errore
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        # Pulsante centrato "Invia nuova password"
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_invia = QPushButton("Invia nuova password")
        btn_invia.setFixedWidth(200)
        btn_invia.clicked.connect(self.invia_click)
        btn_layout.addWidget(btn_invia)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def invia_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        em = self.email.text().strip()
        if not em:
            mostra_errore(self.lbl_errore, "Inserire un indirizzo e-mail.")
            return

        ok = Volontario().inserisciEmail(em)
        if ok:
            self.close()
        else:
            mostra_errore(self.lbl_errore, "E-mail non registrata.")
