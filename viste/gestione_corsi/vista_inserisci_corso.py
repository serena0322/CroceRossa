"""VistaInserisciCorso (GestioneCorsi) secondo le specifiche del PDF e mockup (pag. 108).
Layout a due colonne:
- Intestazione 'Nuovo corso'
- Campo 'Codice' (mostra il codice generato)
- 'Nome', 'Descrizione', 'Direttore del corso', 'Tipo di corso'
- 'Inizio' e 'Fine' affiancati con date picker
- 'Orario' (testo libero, es. '20:30 - 23:00')
- 'Luogo'
- 'Numero posti'
- Banner di errore
- Pulsante 'Inserisci corso' centrato
"""
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QDateEdit, QPushButton
)
from PyQt5.QtCore import QDate
from attivita.corso import Corso
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaInserisciCorso(QWidget):
    def __init__(self, codice: str, callback, parent=None):
        super(VistaInserisciCorso, self).__init__(parent)
        self.codice = codice
        self.callback = callback
        self.qlines: dict[str, QLineEdit] = {}

        self.setWindowTitle(f"Nuovo corso {self.codice}")
        self.resize(520, 500)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Intestazione come nel mockup di pagina 108: "Nuovo corso"

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        row = 0

        def add_row(key: str, label_text: str, default_val: str = "", read_only: bool = False):
            nonlocal row
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 13px; font-weight: 500;")
            txt = QLineEdit(self)
            txt.setText(default_val)
            if read_only:
                txt.setReadOnly(True)
            self.qlines[key] = txt
            grid.addWidget(lbl, row, 0)
            grid.addWidget(txt, row, 1)
            row += 1

        # Riga Codice (nel mockup di pagina 108 c'è la riga "Codice" con dentro es. C-032)
        add_row("codice", "Codice", self.codice, read_only=True)

        add_row("nome", "Nome", "")
        add_row("descrizione", "Descrizione", "")
        add_row("direttoreCorso", "Direttore del corso", "")
        add_row("tipoCorso", "Tipo di corso", "Base")

        # Inizio e Fine affiancati
        lbl_inizio = QLabel("Inizio")
        lbl_inizio.setStyleSheet("font-size: 13px; font-weight: 500;")
        grid.addWidget(lbl_inizio, row, 0)

        date_row_layout = QHBoxLayout()
        date_row_layout.setSpacing(12)

        self.data_inizio = QDateEdit(self)
        self.data_inizio.setDate(QDate.currentDate().addDays(7))
        self.data_inizio.setCalendarPopup(True)
        date_row_layout.addWidget(self.data_inizio, 1)

        lbl_fine = QLabel("Fine")
        lbl_fine.setStyleSheet("font-size: 13px; font-weight: 500;")
        date_row_layout.addWidget(lbl_fine)

        self.data_fine = QDateEdit(self)
        self.data_fine.setDate(QDate.currentDate().addDays(14))
        self.data_fine.setCalendarPopup(True)
        date_row_layout.addWidget(self.data_fine, 1)

        grid.addLayout(date_row_layout, row, 1)
        row += 1

        add_row("orario", "Orario", "20:30 - 23:00")
        add_row("luogo", "Luogo", "")
        add_row("postiTotali", "Numero posti", "20")

        main_layout.addLayout(grid)

        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        # Pulsante centrato "Inserisci corso" come da mockup pag. 108
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn = QPushButton("Inserisci corso")
        btn.setFixedWidth(200)
        btn.clicked.connect(self.aggiungi_corso_click)
        btn_layout.addWidget(btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def aggiungi_corso_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        codice_effettivo = self.qlines["codice"].text().strip() or self.codice
        nome = self.qlines["nome"].text().strip()
        desc = self.qlines["descrizione"].text().strip()
        direttore = self.qlines["direttoreCorso"].text().strip()
        tipo = self.qlines["tipoCorso"].text().strip()

        q_i = self.data_inizio.date()
        d_inizio = date(q_i.year(), q_i.month(), q_i.day())
        q_f = self.data_fine.date()
        d_fine = date(q_f.year(), q_f.month(), q_f.day())

        orario = self.qlines["orario"].text().strip()
        luogo = self.qlines["luogo"].text().strip()

        try:
            posti = int(self.qlines["postiTotali"].text().strip())
        except ValueError:
            mostra_errore(self.lbl_errore, "Il numero di posti deve essere un numero intero positivo.")
            return

        try:
            Corso().inserisciDatiCorso(
                codice_effettivo, nome, desc, direttore, tipo,
                d_inizio, d_fine, orario, luogo, posti
            )
            if self.callback:
                self.callback()
            self.close()
        except ValueError as e:
            mostra_errore(self.lbl_errore, str(e))
