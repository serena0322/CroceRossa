"""VistaGestisciCorsi (GestioneCorsi) secondo le specifiche del PDF e mockup (pag. 10)."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListView, QPushButton, QMessageBox
)
from PyQt5.QtCore import QStringListModel
from attivita.corso import Corso


class VistaGestisciCorsi(QWidget):
    def __init__(self, parent=None):
        super(VistaGestisciCorsi, self).__init__(parent)
        self.corsi: list[Corso] = []
        self.vista_iscritti = None
        self.vista_attesta = None
        self.vista_inserisci = None
        self.vista_modifica = None

        self.setWindowTitle("Gestione corsi")
        self.resize(580, 420)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Elenco corsi di formazione:</b>"))

        self.list_view = QListView(self)
        layout.addWidget(self.list_view)

        row_azioni = QHBoxLayout()
        btn_iscritti = QPushButton("Visualizza iscritti")
        btn_iscritti.clicked.connect(self.show_selected_info)
        row_azioni.addWidget(btn_iscritti)

        btn_attesta = QPushButton("Attesta partecipazione")
        btn_attesta.clicked.connect(self.attesta_partecipazione_click)
        row_azioni.addWidget(btn_attesta)
        layout.addLayout(row_azioni)

        codice_row = QHBoxLayout()
        codice_row.addWidget(QLabel("Codice corso:"))
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
        self.btn_rim.clicked.connect(self.rimuovi_corso)
        btn_row.addWidget(self.btn_rim)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.load_corsi()

    def load_corsi(self) -> None:
        self.corsi = Corso().visualizzaCorsi()
        self.update_ui()

    def update_ui(self) -> None:
        model = QStringListModel()
        righe = []
        for c in self.corsi:
            d = c.getDati()
            righe.append(
                f"{d['codice']} | {d['nome']} | Inizio: {d['dataInizio']:%d/%m/%Y} | "
                f"Stato: {c.getStato().value} | Posti liberi: {d['postiLiberi']}"
            )
        model.setStringList(righe)
        self.list_view.setModel(model)

        ha_codice = bool(self.codice.text().strip())
        self.btn_ins.setEnabled(ha_codice)
        self.btn_mod.setEnabled(ha_codice)
        self.btn_rim.setEnabled(ha_codice)

    def _get_selected_corso(self) -> Corso | None:
        idx = self.list_view.currentIndex().row()
        if 0 <= idx < len(self.corsi):
            return self.corsi[idx]
        return None

    def show_selected_info(self) -> None:
        corso = self._get_selected_corso()
        if not corso:
            QMessageBox.warning(self, "Attenzione", "Selezionare un corso dall'elenco.")
            return
        from viste.gestione_corsi.vista_iscritti_corso import VistaIscrittiCorso
        self.vista_iscritti = VistaIscrittiCorso(corso)
        self.vista_iscritti.show()

    def attesta_partecipazione_click(self) -> None:
        corso = self._get_selected_corso()
        if not corso:
            QMessageBox.warning(self, "Attenzione", "Selezionare un corso dall'elenco.")
            return
        iscritti = Corso().attestaPartecipazione(corso)
        if not iscritti:
            QMessageBox.critical(self, "Errore", "Corso non concluso o senza iscritti.")
            return

        from viste.gestione_corsi.vista_attesta_partecipazione import VistaAttestaPartecipazione
        self.vista_attesta = VistaAttestaPartecipazione(corso, self.load_corsi)
        self.vista_attesta.show()

    def show_new(self) -> None:
        cod = self.codice.text().strip()
        if not Corso().inserisciCorso(cod):
            QMessageBox.critical(self, "Errore", f"Corso {cod} già presente.")
            return

        from viste.gestione_corsi.vista_inserisci_corso import VistaInserisciCorso
        self.vista_inserisci = VistaInserisciCorso(cod, self.load_corsi)
        self.vista_inserisci.show()

    def show_modifica(self) -> None:
        cod = self.codice.text().strip()
        dati_c = Corso().modificaCorso(cod)
        if not dati_c:
            QMessageBox.critical(self, "Errore", "Corso non trovato o non programmato.")
            return

        trovati = [c for c in self.corsi if c.getDati()["codice"] == cod]
        if not trovati:
            return
        from viste.gestione_corsi.vista_modifica_corso import VistaModificaCorso
        self.vista_modifica = VistaModificaCorso(trovati[0], self.load_corsi)
        self.vista_modifica.show()

    def rimuovi_corso(self) -> None:
        cod = self.codice.text().strip()
        ok = Corso().rimuoviCorso(cod)
        if ok:
            QMessageBox.information(self, "Rimozione", f"Corso {cod} rimosso con successo.")
            self.load_corsi()
        else:
            QMessageBox.critical(self, "Errore", "Corso non trovato o non programmato.")
