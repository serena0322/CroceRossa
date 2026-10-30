from __future__ import annotations
from typing import List, Callable, Optional, TYPE_CHECKING
from PyQt5.QtWidgets import (
    QWidget, QListView, QComboBox, QDateEdit, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QLineEdit
)
from PyQt5.QtCore import QDate, QStringListModel

if TYPE_CHECKING:
    from Volontario import Volontario
    from Patente import Patente


class VistaPatente(QWidget):
    """
    Vista UML: VistaPatente (in GestionePatenti)
    Attributi UML:
        data_scadenza: QDateEdit (o Integer)
        elimina_callback: Function
    Metodi UML:
        __init__(Patente, Volontario, Function)
        elimina_patente_click(Patente): void
        modifica_patente_click(Patente): void
    """
    def __init__(self, patente: Patente, volontario: Volontario, elimina_callback: Callable = None):
        super().__init__()
        self.patente = patente
        self.volontario = volontario
        self.elimina_callback = elimina_callback
        self.data_scadenza = QDateEdit(self)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Patente: {getattr(self.patente, 'tipo', '')} (Codice: {getattr(self.patente, 'codice', '')})"))
        scad = getattr(self.patente, "dataScadenza", "")
        if scad:
            try:
                self.data_scadenza.setDate(QDate.fromString(scad, "yyyy-MM-dd"))
            except Exception:
                self.data_scadenza.setDate(QDate.currentDate().addYears(5))
        layout.addWidget(QLabel("Nuova Scadenza:"))
        layout.addWidget(self.data_scadenza)

        btns = QHBoxLayout()
        btn_mod = QPushButton("Salva Modifica")
        btn_mod.clicked.connect(lambda: self.modifica_patente_click(self.patente))
        btns.addWidget(btn_mod)

        btn_del = QPushButton("Elimina Patente")
        btn_del.clicked.connect(lambda: self.elimina_patente_click(self.patente))
        btns.addWidget(btn_del)
        layout.addLayout(btns)

    def elimina_patente_click(self, patente: Patente) -> None:
        """Elimina la patente associata al volontario (UML CUDPatenti)."""
        from GestioneUtenteController import GestioneUtenteController
        ctrl = GestioneUtenteController()
        tipo = getattr(patente, "tipo", str(patente))
        ctrl.cudPatenti(self.volontario, "DELETE", {"tipo": tipo})
        if self.elimina_callback:
            self.elimina_callback()

    def modifica_patente_click(self, patente: Patente) -> None:
        """Modifica la data di scadenza della patente (UML CUDPatenti)."""
        from GestioneUtenteController import GestioneUtenteController
        ctrl = GestioneUtenteController()
        nuova_scad = self.data_scadenza.date().toString("yyyy-MM-dd")
        ctrl.cudPatenti(self.volontario, "UPDATE", {
            "tipo": getattr(patente, "tipo", ""),
            "codice": getattr(patente, "codice", ""),
            "scadenza_patente": nuova_scad,
            "dataScadenza": nuova_scad
        })
        if self.elimina_callback:
            self.elimina_callback()


class VistaInserisciPatente(QWidget):
    """
    Vista UML: VistaInserisciPatente (in GestionePatenti)
    Attributi UML:
        callback: Function
        combo: QComboBox
        qlines: dict
        v_layout: QVBoxLayout
    Metodi UML:
        __init__(Volontario, Function)
        add_info_text(str, str): void
        aggiungi_patente(): void
        onChanged(str): void
    """
    def __init__(self, volontario: Volontario, callback: Callable = None):
        super().__init__()
        self.volontario = volontario
        self.callback = callback
        self.combo = QComboBox(self)
        self.qlines: dict[str, QLineEdit] = {}
        self.v_layout = QVBoxLayout(self)
        self._init_ui()

    def _init_ui(self):
        self.v_layout.addWidget(QLabel("Inserisci Nuova Patente"))
        self.combo.addItems(["B", "C1", "C", "D1", "D", "BE", "CE"])
        self.combo.currentTextChanged.connect(self.onChanged)
        self.v_layout.addWidget(QLabel("Categoria:"))
        self.v_layout.addWidget(self.combo)

        self.add_info_text("codice", "Numero/Codice Patente")
        self.add_info_text("dataScadenza", "Data Scadenza (YYYY-MM-DD)")

        btn_add = QPushButton("Aggiungi Patente")
        btn_add.clicked.connect(self.aggiungi_patente)
        self.v_layout.addWidget(btn_add)

    def add_info_text(self, chiave: str, etichetta: str) -> None:
        """Aggiunge un campo di testo QLineEdit al layout (UML)."""
        lbl = QLabel(f"{etichetta}:")
        txt = QLineEdit(self)
        self.qlines[chiave] = txt
        self.v_layout.addWidget(lbl)
        self.v_layout.addWidget(txt)

    def onChanged(self, val: str) -> None:
        """Gestisce il cambio categoria patente nella combo box (UML)."""
        pass

    def aggiungi_patente(self) -> None:
        """Registra la nuova patente tramite il controller (UML CUDPatenti)."""
        from GestioneUtenteController import GestioneUtenteController
        ctrl = GestioneUtenteController()
        tipo = self.combo.currentText()
        cod = self.qlines.get("codice", QLineEdit()).text().strip()
        scad = self.qlines.get("dataScadenza", QLineEdit()).text().strip() or "2030-01-01"
        ctrl.cudPatenti(self.volontario, "CREATE", {
            "tipo": tipo,
            "codice": cod,
            "numero_patente": cod,
            "scadenza_patente": scad,
            "dataScadenza": scad
        })
        if self.callback:
            self.callback()


class VistaGestisciPatenti(QWidget):
    """
    Vista UML: VistaGestisciPatenti (in GestionePatenti)
    Attributi UML:
        list_view: QListView
        patenti: list<Patente>
        volontario: Volontario
    Metodi UML:
        __init__(Volontario)
        load_patenti(): void
        show_new(): void
        show_selected_info(): void
        update_ui(): void
    """
    def __init__(self, volontario: Volontario):
        super().__init__()
        self.volontario = volontario
        self.patenti: list = []
        self.list_view = QListView(self)
        self.vista_inserisci: Optional[VistaInserisciPatente] = None
        self.vista_patente: Optional[VistaPatente] = None
        self._init_ui()
        self.load_patenti()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Gestione Patenti Volontario:"))
        layout.addWidget(self.list_view)

        btns = QHBoxLayout()
        btn_new = QPushButton("Aggiungi Nuova Patente")
        btn_new.clicked.connect(self.show_new)
        btns.addWidget(btn_new)

        btn_info = QPushButton("Dettaglio / Modifica Selezionata")
        btn_info.clicked.connect(self.show_selected_info)
        btns.addWidget(btn_info)
        layout.addLayout(btns)

    def load_patenti(self) -> None:
        """Carica l'elenco patenti del volontario (UML VisualizzaPatenti)."""
        from GestioneUtenteController import GestioneUtenteController
        ctrl = GestioneUtenteController()
        if self.volontario:
            self.patenti = ctrl.visualizzaPatenti(self.volontario)
        self.update_ui()

    def show_new(self) -> None:
        """Apre la vista di inserimento nuova patente (UML)."""
        self.vista_inserisci = VistaInserisciPatente(self.volontario, callback=self.load_patenti)
        self.vista_inserisci.show()

    def show_selected_info(self) -> None:
        """Apre la vista di dettaglio della patente selezionata (UML)."""
        idx = self.list_view.currentIndex().row()
        if 0 <= idx < len(self.patenti):
            p = self.patenti[idx]
            from Patente import Patente
            p_obj = p if isinstance(p, Patente) else Patente(tipo=str(p))
            self.vista_patente = VistaPatente(p_obj, self.volontario, elimina_callback=self.load_patenti)
            self.vista_patente.show()

    def update_ui(self) -> None:
        """Aggiorna gli elementi nella QListView (UML)."""
        model = QStringListModel()
        items = []
        for p in self.patenti:
            if hasattr(p, "tipo"):
                items.append(f"Patente {p.tipo} - Scad: {getattr(p, 'dataScadenza', 'N/D')}")
            else:
                items.append(f"Patente {p}")
        model.setStringList(items)
        self.list_view.setModel(model)


class GestionePatenti(QWidget):
    """Contenitore per la gestione patenti."""
    def __init__(self, volontario: Volontario = None):
        super().__init__()
        layout = QVBoxLayout(self)
        if volontario:
            self.vista_gestisci = VistaGestisciPatenti(volontario)
            layout.addWidget(self.vista_gestisci)
