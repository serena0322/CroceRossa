"""VistaModificaTurno (GestioneTurni) secondo le specifiche del PDF e mockup (pag. 9)."""
from datetime import date, time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QTimeEdit, QPushButton,
    QMessageBox
)
from PyQt5.QtCore import QDate, QTime
from attivita.turno import Turno


class VistaModificaTurno(QWidget):
    def __init__(self, turno: Turno, callback, parent=None):
        super(VistaModificaTurno, self).__init__(parent)
        self.turno = turno
        self.callback = callback
        self.qlines: dict[str, QLineEdit] = {}

        d = self.turno.getDati()
        self.setWindowTitle(f"Modifica turno {d['codice']}")
        self.resize(460, 520)

        self.v_layout = QVBoxLayout(self)
        self.v_layout.addWidget(QLabel(f"<b>Codice:</b> {d['codice']}"))

        self.add_info_text("datiPaziente", "Dati paziente (se presente)")
        self.qlines["datiPaziente"].setText(d.get("datiPaziente", ""))

        self.v_layout.addWidget(QLabel("Data:"))
        self.data = QDateEdit(self)
        dt = d["data"]
        self.data.setDate(QDate(dt.year, dt.month, dt.day))
        self.data.setCalendarPopup(True)
        self.v_layout.addWidget(self.data)

        self.v_layout.addWidget(QLabel("Ora inizio:"))
        self.ora_inizio = QTimeEdit(self)
        ti = d["oraInizio"]
        self.ora_inizio.setTime(QTime(ti.hour, ti.minute))
        self.v_layout.addWidget(self.ora_inizio)

        self.v_layout.addWidget(QLabel("Ora fine:"))
        self.ora_fine = QTimeEdit(self)
        tf = d["oraFine"]
        self.ora_fine.setTime(QTime(tf.hour, tf.minute))
        self.v_layout.addWidget(self.ora_fine)

        self.add_info_text("luogo", "Luogo")
        self.qlines["luogo"].setText(d.get("luogo", ""))

        self.v_layout.addWidget(QLabel("Tipo di servizio:"))
        self.combo = QComboBox(self)
        self.combo.addItems(["Trasporto infermi", "Emergenza 118", "Assistenza manifestazioni", "Protezione Civile"])
        self.combo.setCurrentText(d.get("tipoServizio", "Trasporto infermi"))
        self.v_layout.addWidget(self.combo)

        self.add_info_text("postiTotali", "Numero di posti")
        self.qlines["postiTotali"].setText(str(d.get("postiTotali", 3)))

        self.v_layout.addWidget(QLabel("Patente richiesta:"))
        self.combo_patente = QComboBox(self)
        self.combo_patente.addItems(["Nessuna", "CRI 1", "CRI 2", "CRI 3", "CRI 4", "CRI 5", "B"])
        self.combo_patente.setCurrentText(d.get("patenteRichiesta") or "Nessuna")
        self.v_layout.addWidget(self.combo_patente)

        self.add_info_text("corsiRichiesti", "Corsi richiesti")
        self.qlines["corsiRichiesti"].setText(d.get("corsiRichiesti", ""))

        self.add_info_text("mezzo", "Mezzo previsto")
        self.qlines["mezzo"].setText(d.get("mezzo", ""))

        self.add_info_text("materialeNecessario", "Materiale necessario")
        self.qlines["materialeNecessario"].setText(d.get("materialeNecessario", ""))

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
        paziente = self.qlines["datiPaziente"].text().strip()
        qd = self.data.date()
        d = date(qd.year(), qd.month(), qd.day())
        qi = self.ora_inizio.time()
        qf = self.ora_fine.time()
        ora_i = time(qi.hour(), qi.minute())
        ora_f = time(qf.hour(), qf.minute())
        luogo = self.qlines["luogo"].text().strip()
        tipo_servizio = self.combo.currentText()
        try:
            posti = int(self.qlines["postiTotali"].text().strip())
        except ValueError:
            QMessageBox.critical(self, "Errore", "Il numero di posti deve essere un numero intero positivo.")
            return

        patente = self.combo_patente.currentText()
        if patente == "Nessuna":
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
                QMessageBox.information(self, "Modifiche salvate", "Turno aggiornato e volontari notificati.")
                if self.callback:
                    self.callback()
                self.close()
            else:
                QMessageBox.critical(self, "Errore", "Posti inferiori ai Volontari già prenotati.")
        except ValueError as e:
            QMessageBox.critical(self, "Errore", str(e))
