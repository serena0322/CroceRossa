"""VistaDettagliCorso (IscrizioneCorsi).
Layout:
- Intestazione: 'Dettagli corso <codice>'
- Form a due colonne in sola lettura:
  - Codice
  - Nome
  - Descrizione
  - Direttore del corso
  - Tipo di corso
  - Data inizio / fine
  - Luogo
  - Orario
  - Posti totali / liberi
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from attivita.corso import Corso


class VistaDettagliCorso(QWidget):
    def __init__(self, corso: Corso, parent=None):
        super(VistaDettagliCorso, self).__init__(parent)
        self.corso = corso
        d = Corso().visualizzaDettagliCorso(corso)
        codice = d.get("codice", "")

        self.setWindowTitle(f"Dettagli corso {codice}")
        self.resize(500, 420)

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
            ("Nome", d.get("nome", "")),
            ("Descrizione", d.get("descrizione", "")),
            ("Direttore del corso", d.get("direttoreCorso", "")),
            ("Tipo di corso", d.get("tipoCorso", "")),
            ("Data inizio / fine", f"{d['dataInizio']:%d/%m/%Y} - {d['dataFine']:%d/%m/%Y}"),
            ("Luogo", d.get("luogo", "")),
            ("Orario", d.get("orario", "")),
            ("Posti totali / liberi", f"{d.get('postiTotali', 0)} / {d.get('postiLiberi', 0)}")
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
