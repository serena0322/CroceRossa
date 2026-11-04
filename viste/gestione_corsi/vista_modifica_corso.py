"""VistaModificaCorso (GestioneCorsi) secondo le specifiche del PDF e mockup.
Layout a due colonne con:
- Titolo 'Modifica corso <codice>'
- Form con label a sinistra e campi a destra
- Riga date con 'Inizio' [date picker] e 'Fine' [date picker] affiancati
- Campo 'Orario' come testo libero (es. 'Giovedì 20:30 - 23:00')
- Banner di errore rosso/rosa a tutta larghezza
- Pulsante 'Salva modifiche' centrato
"""
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QDateEdit, QPushButton
)
from PyQt5.QtCore import QDate, Qt
from attivita.corso import Corso
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaModificaCorso(QWidget):
    def __init__(self, corso: Corso, callback, parent=None):
        super(VistaModificaCorso, self).__init__(parent)
        self.corso = corso
        self.callback = callback
        self.qlines: dict[str, QLineEdit] = {}

        d = self.corso.getDati()
        codice = d.get("codice", "")
        self.setWindowTitle(f"Modifica corso {codice}")
        self.resize(520, 480)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Intestazione mockup: "Modifica corso C-031"

        # Griglia del form a 2 colonne
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        row = 0

        def add_row(key: str, label_text: str, default_val: str = ""):
            nonlocal row
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 13px; font-weight: 500;")
            txt = QLineEdit(self)
            txt.setText(default_val)
            self.qlines[key] = txt
            grid.addWidget(lbl, row, 0)
            grid.addWidget(txt, row, 1)
            row += 1

        add_row("nome", "Nome", d.get("nome", ""))
        add_row("descrizione", "Descrizione", d.get("descrizione", ""))
        add_row("direttoreCorso", "Direttore del corso", d.get("direttoreCorso", ""))
        add_row("tipoCorso", "Tipo di corso", d.get("tipoCorso", "Base"))

        # Riga Inizio & Fine affiancati
        lbl_inizio = QLabel("Inizio")
        lbl_inizio.setStyleSheet("font-size: 13px; font-weight: 500;")
        grid.addWidget(lbl_inizio, row, 0)

        date_row_layout = QHBoxLayout()
        date_row_layout.setSpacing(12)

        self.data_inizio = QDateEdit(self)
        di = d["dataInizio"]
        self.data_inizio.setDate(QDate(di.year, di.month, di.day))
        self.data_inizio.setCalendarPopup(True)
        date_row_layout.addWidget(self.data_inizio, 1)

        lbl_fine = QLabel("Fine")
        lbl_fine.setStyleSheet("font-size: 13px; font-weight: 500;")
        date_row_layout.addWidget(lbl_fine)

        self.data_fine = QDateEdit(self)
        df = d["dataFine"]
        self.data_fine.setDate(QDate(df.year, df.month, df.day))
        self.data_fine.setCalendarPopup(True)
        date_row_layout.addWidget(self.data_fine, 1)

        grid.addLayout(date_row_layout, row, 1)
        row += 1

        # Orario (tipo dato: testo libero come da mockup "Giovedì 20:30 - 23:00")
        add_row("orario", "Orario", d.get("orario", ""))
        add_row("luogo", "Luogo", d.get("luogo", ""))
        add_row("postiTotali", "Numero posti", d.get("postiTotali", 20))

        main_layout.addLayout(grid)

        # Banner errore sotto i campi
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        # Pulsante "Salva modifiche" centrato
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_salva = QPushButton("Salva modifiche")
        btn_salva.setFixedWidth(200)
        btn_salva.clicked.connect(self.salva_modifiche_click)
        btn_layout.addWidget(btn_salva)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def salva_modifiche_click(self) -> None:
        nascondi_errore(self.lbl_errore)
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
            ok = Corso().inserisciModifiche(
                self.corso, nome, desc, direttore, tipo,
                d_inizio, d_fine, orario, luogo, posti
            )
            if ok:
                if self.callback:
                    self.callback()
                self.close()
            else:
                iscritti = len(self.corso.volontariIscritti) if hasattr(self.corso, 'volontariIscritti') else 0
                msg = f"Il numero di posti è inferiore ai Volontari iscritti ({iscritti})." if iscritti else "Posti inferiori ai Volontari già iscritti."
                mostra_errore(self.lbl_errore, msg)
        except ValueError as e:
            mostra_errore(self.lbl_errore, str(e))
