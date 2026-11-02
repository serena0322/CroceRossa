"""VistaModificaPatente (GestionePatenti) secondo le specifiche del PDF e mockup (pag. 104).
Layout a due colonne:
- Titolo 'Modifica patente'
- Codice (QLineEdit in sola lettura)
- Tipo (QLineEdit)
- Data di scadenza (QDateEdit)
- Pulsante 'Salva modifiche' centrato
- Banner di errore
"""
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QDateEdit, QPushButton
)
from PyQt5.QtCore import QDate
from utenti.patente import Patente
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaModificaPatente(QWidget):
    def __init__(self, patente: Patente, callback, parent=None):
        super(VistaModificaPatente, self).__init__(parent)
        self.patente = patente
        self.callback = callback

        d = self.patente.getDati()
        codice = d.get("codice", "")
        self.setWindowTitle(f"Modifica patente {codice}")
        self.resize(500, 280)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Intestazione come mockup pag. 104: "Modifica patente"

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        # Riga Codice (in sola lettura)
        lbl_cod = QLabel("Codice")
        lbl_cod.setStyleSheet("font-size: 13px; font-weight: 500;")
        self.txt_codice = QLineEdit(self)
        self.txt_codice.setText(codice)
        self.txt_codice.setReadOnly(True)
        grid.addWidget(lbl_cod, 0, 0)
        grid.addWidget(self.txt_codice, 0, 1)

        # Riga Tipo
        lbl_tipo = QLabel("Tipo")
        lbl_tipo.setStyleSheet("font-size: 13px; font-weight: 500;")
        self.txt_tipo = QLineEdit(self)
        self.txt_tipo.setText(d.get("tipo", ""))
        self.txt_tipo.setReadOnly(True)
        grid.addWidget(lbl_tipo, 1, 0)
        grid.addWidget(self.txt_tipo, 1, 1)

        # Riga Data di scadenza
        lbl_scad = QLabel("Data di scadenza")
        lbl_scad.setStyleSheet("font-size: 13px; font-weight: 500;")
        self.data_scadenza = QDateEdit(self)
        dt = d["dataScadenza"]
        self.data_scadenza.setDate(QDate(dt.year, dt.month, dt.day))
        self.data_scadenza.setCalendarPopup(True)
        grid.addWidget(lbl_scad, 2, 0)
        grid.addWidget(self.data_scadenza, 2, 1)

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
        qd = self.data_scadenza.date()
        scadenza = date(qd.year(), qd.month(), qd.day())
        Patente().inserisciModifiche(self.patente, scadenza)
        if self.callback:
            self.callback()
        self.close()
