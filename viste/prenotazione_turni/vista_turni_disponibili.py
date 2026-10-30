"""VistaTurniDisponibili (PrenotazioneTurni) secondo le specifiche del PDF e mockup (pag. 12)."""
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QComboBox, QDateEdit, QListView,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate, QStringListModel
from attivita.turno import Turno
from attivita.prenotazione import Prenotazione
from utenti.volontario import Volontario


class VistaTurniDisponibili(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaTurniDisponibili, self).__init__(parent)
        self.volontario = volontario
        self.turni: list[Turno] = []
        self.vista_dettagli = None

        self.setWindowTitle("Turni disponibili")
        self.resize(550, 420)

        layout = QVBoxLayout(self)

        filtro_layout = QHBoxLayout()
        self.check_data = QCheckBox("Filtra per data", self)
        filtro_layout.addWidget(self.check_data)

        filtro_layout.addWidget(QLabel("Data:"))
        self.data_filtro = QDateEdit(self)
        self.data_filtro.setDate(QDate.currentDate())
        self.data_filtro.setCalendarPopup(True)
        filtro_layout.addWidget(self.data_filtro)

        filtro_layout.addWidget(QLabel("Tipo di servizio:"))
        self.combo_tipo = QComboBox(self)
        self.combo_tipo.addItems(["Tutti", "Emergenza", "Trasporto sanitario", "Assistenza eventi", "Protezione civile"])
        filtro_layout.addWidget(self.combo_tipo)

        btn_filtra = QPushButton("Filtra")
        btn_filtra.clicked.connect(self.filtra_turni_click)
        filtro_layout.addWidget(btn_filtra)
        layout.addLayout(filtro_layout)

        self.list_view = QListView(self)
        layout.addWidget(self.list_view)

        btn_row = QHBoxLayout()
        btn_dettagli = QPushButton("Dettagli")
        btn_dettagli.clicked.connect(self.show_selected_info)
        btn_row.addWidget(btn_dettagli)

        btn_prenota = QPushButton("Prenota")
        btn_prenota.clicked.connect(self.prenota_turno_click)
        btn_row.addWidget(btn_prenota)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.load_turni()

    def load_turni(self) -> None:
        self.turni = Turno().visualizzaTurniDisponibili()
        self.update_ui()

    def filtra_turni_click(self) -> None:
        d = None
        if self.check_data.isChecked():
            qd = self.data_filtro.date()
            d = date(qd.year(), qd.month(), qd.day())

        tipo = self.combo_tipo.currentText()
        if tipo == "Tutti":
            tipo = ""

        self.turni = Turno().filtraTurni(d, tipo)
        if not self.turni:
            QMessageBox.information(self, "Ricerca turni", "Nessun turno trovato con i criteri selezionati.")
        self.update_ui()

    def update_ui(self) -> None:
        model = QStringListModel()
        righe = []
        for t in self.turni:
            d = t.getDati()
            righe.append(
                f"{d['codice']} | {d['data']:%d/%m} {d['oraInizio']:%H:%M}-{d['oraFine']:%H:%M} | "
                f"{d['tipoServizio']} | Posti liberi: {d['postiLiberi']}"
            )
        model.setStringList(righe)
        self.list_view.setModel(model)

    def _get_selected_turno(self) -> Turno | None:
        idx = self.list_view.currentIndex().row()
        if 0 <= idx < len(self.turni):
            return self.turni[idx]
        return None

    def show_selected_info(self) -> None:
        turno = self._get_selected_turno()
        if not turno:
            QMessageBox.warning(self, "Attenzione", "Selezionare un turno dall'elenco.")
            return
        from viste.prenotazione_turni.vista_dettagli_turno import VistaDettagliTurno
        self.vista_dettagli = VistaDettagliTurno(turno)
        self.vista_dettagli.show()

    def prenota_turno_click(self) -> None:
        turno = self._get_selected_turno()
        if not turno:
            QMessageBox.warning(self, "Attenzione", "Selezionare un turno dall'elenco.")
            return

        errore = Prenotazione().prenotaTurno(turno, self.volontario)
        if errore:
            QMessageBox.critical(self, "Prenotazione non possibile", errore)
            return

        QMessageBox.information(self, "Prenotazione", "Prenotazione registrata con successo.")
        self.load_turni()
