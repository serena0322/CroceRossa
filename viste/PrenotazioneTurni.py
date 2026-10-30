from __future__ import annotations
from typing import List, Callable, Optional, TYPE_CHECKING
from PyQt5.QtWidgets import (
    QWidget, QListView, QComboBox, QDateEdit, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDate, QStringListModel

if TYPE_CHECKING:
    from Volontario import Volontario
    from Turno import Turno
    from Prenotazione import Prenotazione


class VistaDettagliTurno(QWidget):
    """
    Vista UML: VistaDettagliTurno (in PrenotazioneTurni)
    Attributi UML:
        callback: Function (Callable)
    Metodi UML:
        __init__(Turno, Volontario, Function)
        prenota_turno_click(Turno): void
    """
    def __init__(self, turno: Turno, volontario: Volontario, callback: Callable = None):
        super().__init__()
        self.turno = turno
        self.volontario = volontario
        self.callback = callback
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.label_info = QLabel(f"Dettagli Turno: {getattr(self.turno, 'codice', '')} - {getattr(self.turno, 'tipoServizio', '')}")
        layout.addWidget(self.label_info)
        btn_prenota = QPushButton("Prenota Turno")
        btn_prenota.clicked.connect(lambda: self.prenota_turno_click(self.turno))
        layout.addWidget(btn_prenota)

    def prenota_turno_click(self, turno: Turno) -> None:
        """Esegue la prenotazione del turno richiamando il controller (UML)."""
        from GestioneTurniController import GestioneTurniController
        ctrl = GestioneTurniController()
        cod = getattr(turno, "codice", "")
        cf = getattr(self.volontario, "cod_fiscale", "")
        success = ctrl.prenotaTurno(cod, cf)
        if self.callback:
            self.callback(success)


class VistaTurniDisponibili(QWidget):
    """
    Vista UML: VistaTurniDisponibili (in PrenotazioneTurni)
    Attributi UML:
        combo_tipo: QComboBox
        data_filtro: QDateEdit
        list_view: QListView
        turni: list<Turno>
        volontario: Volontario
    Metodi UML:
        __init__(Volontario)
        filtra_turni_click(): void
        load_turni(): void
        show_selected_info(): void
        update_ui(): void
    """
    def __init__(self, volontario: Volontario):
        super().__init__()
        self.volontario = volontario
        self.turni: List[Turno] = []
        self.combo_tipo = QComboBox(self)
        self.data_filtro = QDateEdit(self)
        self.data_filtro.setDate(QDate.currentDate())
        self.list_view = QListView(self)
        self.vista_dettagli: Optional[VistaDettagliTurno] = None
        self._init_ui()
        self.load_turni()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        filtri_box = QHBoxLayout()
        filtri_box.addWidget(QLabel("Tipo Servizio:"))
        self.combo_tipo.addItems(["Tutti", "Emergenza 118", "Trasporto Ordinario", "Guardia Medica"])
        filtri_box.addWidget(self.combo_tipo)
        filtri_box.addWidget(QLabel("Data:"))
        filtri_box.addWidget(self.data_filtro)
        btn_filtra = QPushButton("Filtra Turni")
        btn_filtra.clicked.connect(self.filtra_turni_click)
        filtri_box.addWidget(btn_filtra)
        layout.addLayout(filtri_box)

        layout.addWidget(self.list_view)
        btn_dettagli = QPushButton("Visualizza Dettagli Turno")
        btn_dettagli.clicked.connect(self.show_selected_info)
        layout.addWidget(btn_dettagli)

    def load_turni(self) -> None:
        """Carica l'elenco dei turni disponibili dal controller (UML)."""
        from GestioneTurniController import GestioneTurniController
        ctrl = GestioneTurniController()
        self.turni = ctrl.visualizzaTurniDisponibili()
        self.update_ui()

    def filtra_turni_click(self) -> None:
        """Filtra i turni disponibili secondo tipo servizio e data selezionata (UML)."""
        from GestioneTurniController import GestioneTurniController
        ctrl = GestioneTurniController()
        tipo = self.combo_tipo.currentText()
        data_str = self.data_filtro.date().toString("yyyy-MM-dd")
        crit = "" if tipo == "Tutti" else tipo
        self.turni = ctrl.filtraTurni(self.turni, criterio=f"{data_str} {crit}".strip())
        self.update_ui()

    def show_selected_info(self) -> None:
        """Mostra i dettagli del turno selezionato tramite VistaDettagliTurno (UML)."""
        idx = self.list_view.currentIndex().row()
        if 0 <= idx < len(self.turni):
            t = self.turni[idx]
            self.vista_dettagli = VistaDettagliTurno(t, self.volontario, callback=lambda ok: self.load_turni())
            self.vista_dettagli.show()

    def update_ui(self) -> None:
        """Aggiorna la visualizzazione degli elementi nella QListView (UML)."""
        model = QStringListModel()
        items = [f"{getattr(t, 'codice', '')} - {getattr(t, 'data', '')} ({getattr(t, 'oraInizio', '')}-{getattr(t, 'oraFine', '')}) - {getattr(t, 'tipoServizio', '')} [Liberi: {getattr(t, 'postiLiberi', '')}]" for t in self.turni]
        model.setStringList(items)
        self.list_view.setModel(model)


class VistaPrenotazioni(QWidget):
    """
    Vista UML: VistaPrenotazioni (in PrenotazioneTurni)
    Attributi UML:
        list_view: QListView
        prenotazioni: list<Prenotazioni>
        volontario: Volontario
    Metodi UML:
        __init__(Volontario)
        annulla_prenotazione_click(Prenotazione): void
        load_prenotazioni(): void
        update_ui(): void
    """
    def __init__(self, volontario: Volontario):
        super().__init__()
        self.volontario = volontario
        self.prenotazioni: list = []
        self.list_view = QListView(self)
        self._init_ui()
        self.load_prenotazioni()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Mie Prenotazioni Turni:"))
        layout.addWidget(self.list_view)
        btn_annulla = QPushButton("Annulla Prenotazione Selezionata")
        btn_annulla.clicked.connect(self._on_annulla_click)
        layout.addWidget(btn_annulla)

    def load_prenotazioni(self) -> None:
        """Carica le prenotazioni del volontario dal controller (UML)."""
        if self.volontario:
            self.prenotazioni = list(getattr(self.volontario, "prenotazioni", []))
        self.update_ui()

    def _on_annulla_click(self) -> None:
        idx = self.list_view.currentIndex().row()
        if 0 <= idx < len(self.prenotazioni):
            pren = self.prenotazioni[idx]
            self.annulla_prenotazione_click(pren)

    def annulla_prenotazione_click(self, prenotazione: Prenotazione) -> None:
        """Annulla la prenotazione selezionata (UML act VisualizzaPrenotazioni)."""
        from GestioneTurniController import GestioneTurniController
        ctrl = GestioneTurniController()
        t = getattr(prenotazione, "turno", None)
        if t and self.volontario:
            ctrl.annullaPrenotazione(t, self.volontario)
            self.load_prenotazioni()

    def update_ui(self) -> None:
        """Aggiorna gli elementi mostrati nella QListView (UML)."""
        model = QStringListModel()
        items = []
        for p in self.prenotazioni:
            t = getattr(p, "turno", None)
            items.append(f"{getattr(p, 'codice', '')} - Turno: {getattr(t, 'codice', '')} del {getattr(t, 'data', '')}")
        model.setStringList(items)
        self.list_view.setModel(model)


class PrenotazioneTurni(QWidget):
    """Contenitore per le viste di prenotazione turni."""
    def __init__(self, volontario: Volontario = None):
        super().__init__()
        layout = QVBoxLayout(self)
        if volontario:
            self.vista_disponibili = VistaTurniDisponibili(volontario)
            self.vista_prenotazioni = VistaPrenotazioni(volontario)
            layout.addWidget(self.vista_disponibili)
            layout.addWidget(self.vista_prenotazioni)
