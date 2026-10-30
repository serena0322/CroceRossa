from __future__ import annotations
from typing import List, Callable, Optional, TYPE_CHECKING
from PyQt5.QtWidgets import (
    QWidget, QListView, QComboBox, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QStringListModel

if TYPE_CHECKING:
    from Volontario import Volontario
    from Corso import Corso
    from Iscrizione import Iscrizione


class VistaDettagliCorso(QWidget):
    """
    Vista UML: VistaDettagliCorso (in IscrizioneCorsi)
    Attributi UML:
        callback: Function (Callable)
    Metodi UML:
        __init__(Corso, Volontario, Function)
        iscrivi_click(Corso): void
    """
    def __init__(self, corso: Corso, volontario: Volontario, callback: Callable = None):
        super().__init__()
        self.corso = corso
        self.volontario = volontario
        self.callback = callback
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.label_info = QLabel(f"Dettagli Corso: {getattr(self.corso, 'nome', '')} ({getattr(self.corso, 'tipoCorso', '')})")
        layout.addWidget(self.label_info)
        btn_iscrivi = QPushButton("Iscriviti al Corso")
        btn_iscrivi.clicked.connect(lambda: self.iscrivi_click(self.corso))
        layout.addWidget(btn_iscrivi)

    def iscrivi_click(self, corso: Corso) -> None:
        """Esegue l'iscrizione del volontario al corso tramite controller (UML)."""
        from GestioneFormazioneController import GestioneFormazioneController
        ctrl = GestioneFormazioneController()
        cod = getattr(corso, "codice", getattr(corso, "id", ""))
        success = ctrl.iscriviCorso(self.volontario, cod)
        if self.callback:
            self.callback(success)


class VistaCatalogoCorsi(QWidget):
    """
    Vista UML: VistaCatalogoCorsi (in IscrizioneCorsi)
    Attributi UML:
        combo_tipo: QComboBox
        corsi: list<Corso>
        list_view: QListView
        volontario: Volontario
    Metodi UML:
        __init__(Volontario)
        filtra_corsi_click(): void
        load_corsi(): void
        show_selected_info(): void
        update_ui(): void
    """
    def __init__(self, volontario: Volontario):
        super().__init__()
        self.volontario = volontario
        self.corsi: List[Corso] = []
        self.combo_tipo = QComboBox(self)
        self.list_view = QListView(self)
        self.vista_dettagli: Optional[VistaDettagliCorso] = None
        self._init_ui()
        self.load_corsi()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        filtri_box = QHBoxLayout()
        filtri_box.addWidget(QLabel("Tipologia Corso:"))
        self.combo_tipo.addItems(["Tutti", "Sanitario", "Guida", "Protezione Civile", "BLSD"])
        filtri_box.addWidget(self.combo_tipo)
        btn_filtra = QPushButton("Filtra Corsi")
        btn_filtra.clicked.connect(self.filtra_corsi_click)
        filtri_box.addWidget(btn_filtra)
        layout.addLayout(filtri_box)

        layout.addWidget(self.list_view)
        btn_dettagli = QPushButton("Visualizza Dettagli Corso")
        btn_dettagli.clicked.connect(self.show_selected_info)
        layout.addWidget(btn_dettagli)

    def load_corsi(self) -> None:
        """Carica il catalogo corsi dal controller (UML)."""
        from GestioneFormazioneController import GestioneFormazioneController
        ctrl = GestioneFormazioneController()
        self.corsi = ctrl.visualizzaCatalogoCorsi()
        self.update_ui()

    def filtra_corsi_click(self) -> None:
        """Filtra i corsi per tipologia o criterio (UML)."""
        from GestioneFormazioneController import GestioneFormazioneController
        ctrl = GestioneFormazioneController()
        tipo = self.combo_tipo.currentText()
        crit = "" if tipo == "Tutti" else tipo
        self.corsi = ctrl.filtraCorsi(self.corsi, criterio=crit)
        self.update_ui()

    def show_selected_info(self) -> None:
        """Apre i dettagli del corso selezionato con VistaDettagliCorso (UML)."""
        idx = self.list_view.currentIndex().row()
        if 0 <= idx < len(self.corsi):
            c = self.corsi[idx]
            self.vista_dettagli = VistaDettagliCorso(c, self.volontario, callback=lambda ok: self.load_corsi())
            self.vista_dettagli.show()

    def update_ui(self) -> None:
        """Aggiorna il modello di visualizzazione della QListView (UML)."""
        model = QStringListModel()
        items = [f"{getattr(c, 'nome', '')} ({getattr(c, 'dataInizio', '')} - {getattr(c, 'dataFine', '')}) [Posti: {getattr(c, 'postiLiberi', '')}]" for c in self.corsi]
        model.setStringList(items)
        self.list_view.setModel(model)


class VistaIscrizioni(QWidget):
    """
    Vista UML: VistaIscrizioni (in IscrizioneCorsi)
    Attributi UML:
        iscrizioni: list<Iscrizione>
        list_view: QListView
        volontario: Volontario
    Metodi UML:
        __init__(Volontario)
        annulla_iscrizione_click(Iscrizione): void
        load_iscrizioni(): void
        update_ui(): void
    """
    def __init__(self, volontario: Volontario):
        super().__init__()
        self.volontario = volontario
        self.iscrizioni: list = []
        self.list_view = QListView(self)
        self._init_ui()
        self.load_iscrizioni()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Mie Iscrizioni Corsi:"))
        layout.addWidget(self.list_view)
        btn_annulla = QPushButton("Annulla Iscrizione Selezionata")
        btn_annulla.clicked.connect(self._on_annulla_click)
        layout.addWidget(btn_annulla)

    def load_iscrizioni(self) -> None:
        """Carica l'elenco delle iscrizioni del volontario (UML)."""
        if self.volontario:
            self.iscrizioni = list(getattr(self.volontario, "iscrizioni", []))
        self.update_ui()

    def _on_annulla_click(self) -> None:
        idx = self.list_view.currentIndex().row()
        if 0 <= idx < len(self.iscrizioni):
            iscr = self.iscrizioni[idx]
            self.annulla_iscrizione_click(iscr)

    def annulla_iscrizione_click(self, iscrizione: Iscrizione) -> None:
        """Annulla l'iscrizione selezionata al corso formativo (UML)."""
        from GestioneFormazioneController import GestioneFormazioneController
        ctrl = GestioneFormazioneController()
        c = getattr(iscrizione, "corso", None)
        cod = getattr(c, "codice", getattr(c, "id", ""))
        if cod and self.volontario:
            ctrl.annullaIscrizioneCorso(self.volontario, cod)
            self.load_iscrizioni()

    def update_ui(self) -> None:
        """Aggiorna i corsi visualizzati nel modello della QListView (UML)."""
        model = QStringListModel()
        items = []
        for i in self.iscrizioni:
            c = getattr(i, "corso", None)
            stato_superato = "Superato" if getattr(i, "superato", False) else "In Corso"
            items.append(f"{getattr(c, 'nome', '')} - Esito: {stato_superato}")
        model.setStringList(items)
        self.list_view.setModel(model)


class IscrizioneCorsi(QWidget):
    """Contenitore per le viste di iscrizione ai corsi."""
    def __init__(self, volontario: Volontario = None):
        super().__init__()
        layout = QVBoxLayout(self)
        if volontario:
            self.catalogo = VistaCatalogoCorsi(volontario)
            self.iscrizioni = VistaIscrizioni(volontario)
            layout.addWidget(self.catalogo)
            layout.addWidget(self.iscrizioni)
