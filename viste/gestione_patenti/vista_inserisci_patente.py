"""VistaInserisciPatente (GestionePatenti) secondo le specifiche del PDF e mockup (pag. 104).
Layout a due colonne:
- Titolo 'Nuova patente'
- Codice (QLineEdit precompilato)
- Tipo (QLineEdit)
- Data di scadenza (QDateEdit)
- Pulsante 'Inserisci patente' centrato
- Banner di errore
"""
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QDateEdit, QPushButton
)
from PyQt5.QtCore import QDate
from utenti.patente import Patente
from utenti.volontario import Volontario
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaInserisciPatente(QWidget):
    def __init__(self, codice: str, volontario: Volontario, callback, parent=None):
        super(VistaInserisciPatente, self).__init__(parent)
        self.codice = codice
        self.volontario = volontario
        self.callback = callback

        self.setWindowTitle(f"Nuova patente {self.codice}")
        self.resize(500, 280)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Intestazione come mockup pag. 104: "Nuova patente"

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        # Riga Codice
        lbl_cod = QLabel("Codice")
        lbl_cod.setStyleSheet("font-size: 13px; font-weight: 500;")
        self.txt_codice = QLineEdit(self)
        self.txt_codice.setText(self.codice)
        grid.addWidget(lbl_cod, 0, 0)
        grid.addWidget(self.txt_codice, 0, 1)

        # Riga Tipo
        lbl_tipo = QLabel("Tipo")
        lbl_tipo.setStyleSheet("font-size: 13px; font-weight: 500;")
        self.txt_tipo = QLineEdit(self)
        self.txt_tipo.setPlaceholderText("Es. Patente 5")
        grid.addWidget(lbl_tipo, 1, 0)
        grid.addWidget(self.txt_tipo, 1, 1)

        # Riga Data di scadenza
        lbl_scad = QLabel("Data di scadenza")
        lbl_scad.setStyleSheet("font-size: 13px; font-weight: 500;")
        self.data_scadenza = QDateEdit(self)
        self.data_scadenza.setDate(QDate.currentDate().addYears(5))
        self.data_scadenza.setCalendarPopup(True)
        grid.addWidget(lbl_scad, 2, 0)
        grid.addWidget(self.data_scadenza, 2, 1)

        main_layout.addLayout(grid)

        # Banner errore
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        # Pulsante centrato "Inserisci patente"
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_salva = QPushButton("Inserisci patente")
        btn_salva.setFixedWidth(200)
        btn_salva.clicked.connect(self.aggiungi_patente)
        btn_layout.addWidget(btn_salva)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def aggiungi_patente(self) -> None:
        nascondi_errore(self.lbl_errore)
        codice_effettivo = self.txt_codice.text().strip() or self.codice
        tipo = self.txt_tipo.text().strip()
        if not tipo:
            mostra_errore(self.lbl_errore, "Specificare il tipo di patente.")
            return

        qd = self.data_scadenza.date()
        scadenza = date(qd.year(), qd.month(), qd.day())

        Patente().inserisciDatiPatente(codice_effettivo, tipo, scadenza, self.volontario)
        if self.callback:
            self.callback()
        self.close()
