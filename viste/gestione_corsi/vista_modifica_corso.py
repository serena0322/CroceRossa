"""VistaModificaCorso (GestioneCorsi) secondo le specifiche del PDF e mockup (pag. 11)."""
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate
from attivita.corso import Corso


class VistaModificaCorso(QWidget):
    def __init__(self, corso: Corso, callback, parent=None):
        super(VistaModificaCorso, self).__init__(parent)
        self.corso = corso
        self.callback = callback
        self.qlines: dict[str, QLineEdit] = {}

        d = self.corso.getDati()
        self.setWindowTitle(f"Modifica corso {d['codice']}")
        self.resize(460, 480)

        self.v_layout = QVBoxLayout(self)
        self.v_layout.addWidget(QLabel(f"<b>Codice corso:</b> {d['codice']}"))

        self.add_info_text("nome", "Nome corso")
        self.qlines["nome"].setText(d.get("nome", ""))

        self.add_info_text("descrizione", "Descrizione")
        self.qlines["descrizione"].setText(d.get("descrizione", ""))

        self.add_info_text("direttoreCorso", "Direttore del corso")
        self.qlines["direttoreCorso"].setText(d.get("direttoreCorso", ""))

        self.v_layout.addWidget(QLabel("Tipo di corso:"))
        self.combo = QComboBox(self)
        self.combo.addItems(["Base", "Sanitario", "Soccorso", "Protezione Civile"])
        self.combo.setCurrentText(d.get("tipoCorso", "Base"))
        self.v_layout.addWidget(self.combo)

        self.v_layout.addWidget(QLabel("Data di inizio:"))
        self.data_inizio = QDateEdit(self)
        di = d["dataInizio"]
        self.data_inizio.setDate(QDate(di.year, di.month, di.day))
        self.data_inizio.setCalendarPopup(True)
        self.v_layout.addWidget(self.data_inizio)

        self.v_layout.addWidget(QLabel("Data di fine:"))
        self.data_fine = QDateEdit(self)
        df = d["dataFine"]
        self.data_fine.setDate(QDate(df.year, df.month, df.day))
        self.data_fine.setCalendarPopup(True)
        self.v_layout.addWidget(self.data_fine)

        self.add_info_text("orario", "Orario di svolgimento")
        self.qlines["orario"].setText(d.get("orario", ""))

        self.add_info_text("luogo", "Luogo di svolgimento")
        self.qlines["luogo"].setText(d.get("luogo", ""))

        self.add_info_text("postiTotali", "Numero di posti")
        self.qlines["postiTotali"].setText(str(d.get("postiTotali", 20)))

        btn = QPushButton("Salva modifiche")
        btn.clicked.connect(self.salva_modifiche)
        self.v_layout.addWidget(btn)

        self.setLayout(self.v_layout)

    def add_info_text(self, chiave: str, etichetta: str) -> None:
        self.v_layout.addWidget(QLabel(f"{etichetta}:"))
        txt = QLineEdit(self)
        self.qlines[chiave] = txt
        self.v_layout.addWidget(txt)

    def salva_modifiche(self) -> None:
        nome = self.qlines["nome"].text().strip()
        desc = self.qlines["descrizione"].text().strip()
        direttore = self.qlines["direttoreCorso"].text().strip()
        tipo = self.combo.currentText()

        q_i = self.data_inizio.date()
        d_inizio = date(q_i.year(), q_i.month(), q_i.day())
        q_f = self.data_fine.date()
        d_fine = date(q_f.year(), q_f.month(), q_f.day())

        orario = self.qlines["orario"].text().strip()
        luogo = self.qlines["luogo"].text().strip()

        try:
            posti = int(self.qlines["postiTotali"].text().strip())
        except ValueError:
            QMessageBox.critical(self, "Errore", "Il numero di posti deve essere un numero intero positivo.")
            return

        try:
            ok = Corso().inserisciModifiche(
                self.corso, nome, desc, direttore, tipo,
                d_inizio, d_fine, orario, luogo, posti
            )
            if ok:
                QMessageBox.information(self, "Modifiche salvate", "Corso aggiornato e iscritti notificati.")
                if self.callback:
                    self.callback()
                self.close()
            else:
                QMessageBox.critical(self, "Errore", "Posti inferiori ai Volontari già iscritti.")
        except ValueError as e:
            QMessageBox.critical(self, "Errore", str(e))
