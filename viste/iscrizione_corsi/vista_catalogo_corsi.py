"""VistaCatalogoCorsi (IscrizioneCorsi) secondo le specifiche del PDF e mockup (pag. 14)."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QListView, QPushButton, QMessageBox
)
from PyQt5.QtCore import QStringListModel
from utenti.volontario import Volontario
from attivita.corso import Corso
from attivita.iscrizione import Iscrizione


class VistaCatalogoCorsi(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaCatalogoCorsi, self).__init__(parent)
        self.volontario = volontario
        self.corsi: list[Corso] = []
        self.vista_dettagli = None

        self.setWindowTitle("Catalogo corsi")
        self.resize(550, 400)

        layout = QVBoxLayout(self)

        filtro_row = QHBoxLayout()
        filtro_row.addWidget(QLabel("Tipo di corso:"))
        self.combo_tipo = QComboBox(self)
        self.combo_tipo.addItems(["Tutti", "Base", "Sanitario", "Soccorso", "Protezione Civile"])
        filtro_row.addWidget(self.combo_tipo)

        btn_filtra = QPushButton("Filtra")
        btn_filtra.clicked.connect(self.filtra_corsi_click)
        filtro_row.addWidget(btn_filtra)
        layout.addLayout(filtro_row)

        self.list_view = QListView(self)
        layout.addWidget(self.list_view)

        btn_row = QHBoxLayout()
        btn_dett = QPushButton("Dettagli")
        btn_dett.clicked.connect(self.show_selected_info)
        btn_row.addWidget(btn_dett)

        btn_iscr = QPushButton("Iscriviti")
        btn_iscr.clicked.connect(self.iscrivi_click)
        btn_row.addWidget(btn_iscr)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.load_corsi()

    def load_corsi(self) -> None:
        self.corsi = Corso().visualizzaCatalogoCorsi()
        self.update_ui()

    def filtra_corsi_click(self) -> None:
        tipo = self.combo_tipo.currentText()
        if tipo == "Tutti":
            self.corsi = Corso().visualizzaCatalogoCorsi()
        else:
            self.corsi = Corso().filtraCorsi(tipo)
        if not self.corsi:
            QMessageBox.information(self, "Catalogo corsi", "Nessun corso trovato con il filtro specificato.")
        self.update_ui()

    def update_ui(self) -> None:
        model = QStringListModel()
        righe = []
        for c in self.corsi:
            d = c.getDati()
            righe.append(
                f"{d['codice']} | {d['nome']} ({d['tipoCorso']}) | "
                f"Dal {d['dataInizio']:%d/%m/%Y} al {d['dataFine']:%d/%m/%Y} | Posti liberi: {d['postiLiberi']}"
            )
        model.setStringList(righe)
        self.list_view.setModel(model)

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
        from viste.iscrizione_corsi.vista_dettagli_corso import VistaDettagliCorso
        self.vista_dettagli = VistaDettagliCorso(corso)
        self.vista_dettagli.show()

    def iscrivi_click(self) -> None:
        corso = self._get_selected_corso()
        if not corso:
            QMessageBox.warning(self, "Attenzione", "Selezionare un corso dall'elenco.")
            return

        ok = Iscrizione().iscriviCorso(corso, self.volontario)
        if ok:
            QMessageBox.information(self, "Iscrizione", "Iscrizione al corso completata con successo.")
            self.load_corsi()
        else:
            QMessageBox.critical(self, "Errore", "Impossibile iscriversi: già iscritto o nessun posto libero.")
