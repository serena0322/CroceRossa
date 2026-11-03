"""Viste/PrenotazioneTurni: VistaDettagliTurno (VisualizzaDettagliTurno).

- Titolo 'Dettagli turno <codice>'
- Form a 2 colonne in sola lettura:
  - Codice
  - Data
  - Orario
  - Luogo
  - Tipo di servizio
  - Posti totali / liberi (es. 3 / 1)
  - Patente richiesta
  - Corsi richiesti
  - Mezzo
  - Materiale necessario
  - Dati paziente
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from attivita.turno import Turno


class VistaDettagliTurno(QWidget):
    def __init__(self, turno: Turno, parent=None):
        super(VistaDettagliTurno, self).__init__(parent)
        self.turno = turno
        d = Turno().visualizzaDettagliTurno(turno)
        codice = d.get("codice", "")

        self.setWindowTitle(f"Dettagli turno {codice}")
        self.resize(500, 440)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(8)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        righe = [
            ("Codice", d.get("codice", "")),
            ("Data", f"{d['data']:%d/%m/%Y}"),
            ("Orario", f"{d['oraInizio']:%H:%M} - {d['oraFine']:%H:%M}"),
            ("Luogo", d.get("luogo", "")),
            ("Tipo di servizio", d.get("tipoServizio", "")),
            ("Posti totali / liberi", f"{d.get('postiTotali', 0)} / {d.get('postiLiberi', 0)}"),
            ("Patente richiesta", d.get("patenteRichiesta") or "nessuna"),
            ("Corsi richiesti", d.get("corsiRichiesti") or "nessuno"),
            ("Mezzo", d.get("mezzo") or "-"),
            ("Materiale necessario", d.get("materialeNecessario") or "-"),
            ("Dati paziente", d.get("datiPaziente") or "-")
        ]

        for row, (etichetta, valore) in enumerate(righe):
            lbl_key = QLabel(f"<b>{etichetta}</b>")
            lbl_key.setStyleSheet("font-size: 13px; color: #2D3748;")
            lbl_val = QLabel(str(valore))
            lbl_val.setStyleSheet("font-size: 13px; color: #4A5568;")
            grid.addWidget(lbl_key, row, 0)
            grid.addWidget(lbl_val, row, 1)

        main_layout.addLayout(grid)
        main_layout.addStretch()
        self.setLayout(main_layout)
