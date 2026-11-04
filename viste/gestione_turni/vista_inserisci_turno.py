"""VistaInserisciTurno (GestioneTurni) secondo le specifiche del PDF e mockup (pag. 104).
Layout a due colonne:
- Titolo 'Nuovo turno'
- Form:
  - Codice
  - Data (QDateEdit)
  - Ora inizio | Ora fine affiancati (QTimeEdit)
  - Luogo
  - Tipo di servizio
  - Numero posti
  - Patente richiesta
  - Corsi richiesti
  - Mezzo previsto
  - Materiale necessario
  - Dati paziente
- Banner errore
- Pulsante 'Inserisci turno' centrato
"""
from datetime import date, time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QDateEdit, QTimeEdit, QPushButton
)
from PyQt5.QtCore import QDate, QTime
from attivita.turno import Turno
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaInserisciTurno(QWidget):
    def __init__(self, codice: str, callback, parent=None):
        super(VistaInserisciTurno, self).__init__(parent)
        self.codice = codice
        self.callback = callback
        self.qlines: dict[str, QLineEdit] = {}

        self.setWindowTitle(f"Nuovo turno {self.codice}")
        self.resize(520, 580)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Intestazione come mockup pag. 104: "Nuovo turno"

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(8)
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

        # Codice
        add_row("codice", "Codice", self.codice)
        self.qlines["codice"].setReadOnly(True)

        # Data
        lbl_data = QLabel("Data")
        lbl_data.setStyleSheet("font-size: 13px; font-weight: 500;")
        grid.addWidget(lbl_data, row, 0)

        self.data = QDateEdit(self)
        self.data.setDate(QDate.currentDate().addDays(1))
        self.data.setCalendarPopup(True)
        grid.addWidget(self.data, row, 1)
        row += 1

        # Ora inizio & Ora fine affiancati
        lbl_orari = QLabel("Ora inizio")
        lbl_orari.setStyleSheet("font-size: 13px; font-weight: 500;")
        grid.addWidget(lbl_orari, row, 0)

        orari_layout = QHBoxLayout()
        orari_layout.setSpacing(12)

        self.ora_inizio = QTimeEdit(self)
        self.ora_inizio.setTime(QTime(8, 0))
        orari_layout.addWidget(self.ora_inizio, 1)

        lbl_fine = QLabel("Ora fine")
        lbl_fine.setStyleSheet("font-size: 13px; font-weight: 500;")
        orari_layout.addWidget(lbl_fine)

        self.ora_fine = QTimeEdit(self)
        self.ora_fine.setTime(QTime(14, 0))
        orari_layout.addWidget(self.ora_fine, 1)

        grid.addLayout(orari_layout, row, 1)
        row += 1

        add_row("luogo", "Luogo", "")
        add_row("tipoServizio", "Tipo di servizio", "Trasporto sanitario")
        add_row("postiTotali", "Numero posti", "3")
        add_row("patenteRichiesta", "Patente richiesta", "")
        add_row("corsiRichiesti", "Corsi richiesti", "")
        add_row("mezzo", "Mezzo previsto", "")
        add_row("materialeNecessario", "Materiale necessario", "")
        add_row("datiPaziente", "Dati paziente", "")

        main_layout.addLayout(grid)

        # Banner errore
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        # Pulsante centrato "Inserisci turno"
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn = QPushButton("Inserisci turno")
        btn.setFixedWidth(200)
        btn.clicked.connect(self.aggiungi_turno_click)
        btn_layout.addWidget(btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def aggiungi_turno_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        codice_effettivo = self.qlines["codice"].text().strip() or self.codice
        paziente = self.qlines["datiPaziente"].text().strip()
        qd = self.data.date()
        d = date(qd.year(), qd.month(), qd.day())
        qi = self.ora_inizio.time()
        qf = self.ora_fine.time()
        ora_i = time(qi.hour(), qi.minute())
        ora_f = time(qf.hour(), qf.minute())
        luogo = self.qlines["luogo"].text().strip()
        tipo_servizio = self.qlines["tipoServizio"].text().strip()
        try:
            posti = int(self.qlines["postiTotali"].text().strip())
        except ValueError:
            mostra_errore(self.lbl_errore, "Il numero di posti deve essere un numero intero positivo.")
            return

        patente = self.qlines["patenteRichiesta"].text().strip()
        if patente.lower() == "nessuna":
            patente = ""

        corsi = self.qlines["corsiRichiesti"].text().strip()
        mezzo = self.qlines["mezzo"].text().strip()
        materiale = self.qlines["materialeNecessario"].text().strip()

        try:
            Turno().inserisciDatiTurno(
                codice_effettivo, paziente, d, ora_i, ora_f, luogo,
                tipo_servizio, posti, patente, corsi, mezzo, materiale
            )
            if self.callback:
                self.callback()
            self.close()
        except ValueError as e:
            mostra_errore(self.lbl_errore, str(e))
