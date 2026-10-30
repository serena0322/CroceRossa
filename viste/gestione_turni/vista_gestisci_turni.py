"""VistaGestisciTurni (GestioneTurni) secondo le specifiche del PDF e mockup (pag. 8)."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListView, QPushButton, QMessageBox
)
from PyQt5.QtCore import QStringListModel
from attivita.turno import Turno
from attivita.stato_attivita import StatoAttivita


class VistaGestisciTurni(QWidget):
    def __init__(self, parent=None):
        super(VistaGestisciTurni, self).__init__(parent)
        self.turni: list[Turno] = []
        self.vista_prenotati = None
        self.vista_inserisci = None
        self.vista_modifica = None

        self.setWindowTitle("Gestione turni")
        self.resize(580, 420)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Elenco turni operativi:</b>"))

        self.list_view = QListView(self)
        layout.addWidget(self.list_view)

        btn_prenotati = QPushButton("Visualizza prenotati")
        btn_prenotati.clicked.connect(self.show_selected_info)
        layout.addWidget(btn_prenotati)

        codice_row = QHBoxLayout()
        codice_row.addWidget(QLabel("Codice turno:"))
        self.codice = QLineEdit(self)
        self.codice.textChanged.connect(self.update_ui)
        codice_row.addWidget(self.codice)
        layout.addLayout(codice_row)

        btn_row = QHBoxLayout()
        self.btn_ins = QPushButton("Inserisci")
        self.btn_ins.clicked.connect(self.show_new)
        btn_row.addWidget(self.btn_ins)

        self.btn_mod = QPushButton("Modifica")
        self.btn_mod.clicked.connect(self.show_modifica)
        btn_row.addWidget(self.btn_mod)

        self.btn_rim = QPushButton("Rimuovi")
        self.btn_rim.clicked.connect(self.rimuovi_turno)
        btn_row.addWidget(self.btn_rim)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.load_turni()

    def load_turni(self) -> None:
        self.turni = Turno().visualizzaTurni()
        self.update_ui()

    def update_ui(self) -> None:
        model = QStringListModel()
        righe = []
        for t in self.turni:
            d = t.getDati()
            pat_ok = "Sì" if t.verificaPatentePrenotati() else "No"
            righe.append(
                f"{d['codice']} | Data: {d['data']:%d/%m} {d['oraInizio']:%H:%M}-{d['oraFine']:%H:%M} | "
                f"{d['luogo']} | Mezzo: {d['mezzo']} | Stato: {t.getStato().value} | Patente ok: {pat_ok}"
            )
        model.setStringList(righe)
        self.list_view.setModel(model)

        ha_codice = bool(self.codice.text().strip())
        self.btn_ins.setEnabled(ha_codice)
        self.btn_mod.setEnabled(ha_codice)
        self.btn_rim.setEnabled(ha_codice)

    def show_selected_info(self) -> None:
        idx = self.list_view.currentIndex().row()
        if not (0 <= idx < len(self.turni)):
            QMessageBox.warning(self, "Attenzione", "Selezionare un turno dall'elenco.")
            return
        turno = self.turni[idx]
        from viste.gestione_turni.vista_prenotati_turno import VistaPrenotatiTurno
        self.vista_prenotati = VistaPrenotatiTurno(turno)
        self.vista_prenotati.show()

    def show_new(self) -> None:
        cod = self.codice.text().strip()
        if not Turno().inserisciTurno(cod):
            QMessageBox.critical(self, "Errore", f"Turno {cod} già presente.")
            return

        from viste.gestione_turni.vista_inserisci_turno import VistaInserisciTurno
        self.vista_inserisci = VistaInserisciTurno(cod, self.load_turni)
        self.vista_inserisci.show()

    def show_modifica(self) -> None:
        cod = self.codice.text().strip()
        dati_t = Turno().modificaTurno(cod)
        if not dati_t:
            QMessageBox.critical(self, "Errore", "Turno non trovato o non programmato.")
            return

        trovati = [t for t in self.turni if t.getDati()["codice"] == cod]
        if not trovati:
            return
        from viste.gestione_turni.vista_modifica_turno import VistaModificaTurno
        self.vista_modifica = VistaModificaTurno(trovati[0], self.load_turni)
        self.vista_modifica.show()

    def rimuovi_turno(self) -> None:
        cod = self.codice.text().strip()
        ok = Turno().rimuoviTurno(cod)
        if ok:
            QMessageBox.information(self, "Rimozione", f"Turno {cod} rimosso con successo.")
            self.load_turni()
        else:
            QMessageBox.critical(self, "Errore", "Turno non trovato o non programmato (non rimovibile).")
