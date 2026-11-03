"""VistaModificaTurno (GestioneTurni) secondo le specifiche del PDF e mockup (pag. 105).
Layout a due colonne:
- Titolo 'Modifica turno <codice>'
- Form:
  - Data (QDateEdit)
  - Ora inizio (QTimeEdit) | Ora fine (QTimeEdit) affiancati
  - Luogo
  - Tipo di servizio
  - Numero posti
  - Patente richiesta
  - Corsi richiesti
  - Mezzo previsto
  - Materiale necessario
  - Dati paziente
- Banner errore (es. 'Il numero di posti è inferiore ai Volontari prenotati (X).')
- Pulsante 'Salva modifiche' centrato in basso
"""
from datetime import date, time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QDateEdit, QTimeEdit, QPushButton
)
from PyQt5.QtCore import QDate, QTime
from attivita.turno import Turno
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaModificaTurno(QWidget):
    def __init__(self, turno: Turno, callback, parent=None):
        super(VistaModificaTurno, self).__init__(parent)
        self.turno = turno
        self.callback = callback
        self.qlines: dict[str, QLineEdit] = {}

        d = self.turno.getDati()
        codice = d.get("codice", "")
        self.setWindowTitle(f"Modifica turno {codice}")
        self.resize(520, 560)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Intestazione come mockup pag. 105: "Modifica turno T-170"

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

        # Data
        lbl_data = QLabel("Data")
        lbl_data.setStyleSheet("font-size: 13px; font-weight: 500;")
        grid.addWidget(lbl_data, row, 0)

        self.data = QDateEdit(self)
        dt = d["data"]
        self.data.setDate(QDate(dt.year, dt.month, dt.day))
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
        ti = d["oraInizio"]
        self.ora_inizio.setTime(QTime(ti.hour, ti.minute))
        orari_layout.addWidget(self.ora_inizio, 1)

        lbl_fine = QLabel("Ora fine")
        lbl_fine.setStyleSheet("font-size: 13px; font-weight: 500;")
        orari_layout.addWidget(lbl_fine)

        self.ora_fine = QTimeEdit(self)
        tf = d["oraFine"]
        self.ora_fine.setTime(QTime(tf.hour, tf.minute))
        orari_layout.addWidget(self.ora_fine, 1)

        grid.addLayout(orari_layout, row, 1)
        row += 1

        add_row("luogo", "Luogo", d.get("luogo", ""))
        add_row("tipoServizio", "Tipo di servizio", d.get("tipoServizio", ""))
        add_row("postiTotali", "Numero posti", str(d.get("postiTotali", 3)))
        add_row("patenteRichiesta", "Patente richiesta", d.get("patenteRichiesta") or "")
        add_row("corsiRichiesti", "Corsi richiesti", d.get("corsiRichiesti", ""))
        add_row("mezzo", "Mezzo previsto", d.get("mezzo", ""))
        add_row("materialeNecessario", "Materiale necessario", d.get("materialeNecessario", ""))
        add_row("datiPaziente", "Dati paziente", d.get("datiPaziente", ""))

        main_layout.addLayout(grid)

        # Banner errore
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        # Pulsante centrato "Salva modifiche"
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn = QPushButton("Salva modifiche")
        btn.setFixedWidth(200)
        btn.clicked.connect(self.salva_modifiche_click)
        btn_layout.addWidget(btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def salva_modifiche_click(self) -> None:
        nascondi_errore(self.lbl_errore)
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
            ok = Turno().inserisciModifiche(
                self.turno, paziente, d, ora_i, ora_f, luogo,
                tipo_servizio, posti, patente, corsi, mezzo, materiale
            )
            if ok:
                if self.callback:
                    self.callback()
                self.close()
            else:
                prenotati = len(self.turno.getPrenotazioni()) if hasattr(self.turno, 'getPrenotazioni') else 0
                msg = f"Il numero di posti è inferiore ai Volontari prenotati ({prenotati})." if prenotati else "Posti inferiori ai Volontari già prenotati."
                mostra_errore(self.lbl_errore, msg)
        except ValueError as e:
            mostra_errore(self.lbl_errore, str(e))
