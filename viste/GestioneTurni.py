from __future__ import annotations
from typing import List, Callable, Optional, TYPE_CHECKING
from PyQt5.QtWidgets import (
    QWidget, QListView, QComboBox, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QLineEdit, QDateEdit
)
from PyQt5.QtCore import QStringListModel, QDate

if TYPE_CHECKING:
    from Turno import Turno
    from Volontario import Volontario


class VistaModificaTurno(QWidget):
    """Vista per la modifica di un turno esistente (UML CUDTurno)."""
    def __init__(self, turno: Turno, callback: Callable = None):
        super().__init__()
        self.turno = turno
        self.callback = callback
        self.qlines: dict[str, QLineEdit] = {}
        self.v_layout = QVBoxLayout(self)
        self._init_ui()

    def _init_ui(self):
        self.v_layout.addWidget(QLabel(f"Modifica Turno: {getattr(self.turno, 'codice', '')}"))
        self.add_info_text("data", "Data (YYYY-MM-DD)")
        self.add_info_text("oraInizio", "Ora Inizio (HH:MM)")
        self.add_info_text("oraFine", "Ora Fine (HH:MM)")
        self.add_info_text("luogo", "Luogo")
        self.add_info_text("tipoServizio", "Tipo Servizio")
        self.add_info_text("postiTotali", "Posti Totali")

        if self.turno:
            for k in ["data", "oraInizio", "oraFine", "luogo", "tipoServizio", "postiTotali"]:
                if k in self.qlines:
                    self.qlines[k].setText(str(getattr(self.turno, k, "")))

        btn_salva = QPushButton("Salva Modifiche")
        btn_salva.clicked.connect(self.salva_modifiche)
        self.v_layout.addWidget(btn_salva)

    def add_info_text(self, chiave: str, etichetta: str) -> None:
        lbl = QLabel(f"{etichetta}:")
        txt = QLineEdit(self)
        self.qlines[chiave] = txt
        self.v_layout.addWidget(lbl)
        self.v_layout.addWidget(txt)

    def salva_modifiche(self) -> None:
        from GestioneTurniController import GestioneTurniController
        ctrl = GestioneTurniController()
        cod = getattr(self.turno, "codice", "")
        dati = {
            "data": self.qlines.get("data", QLineEdit()).text().strip(),
            "oraInizio": self.qlines.get("oraInizio", QLineEdit()).text().strip(),
            "oraFine": self.qlines.get("oraFine", QLineEdit()).text().strip(),
            "luogo": self.qlines.get("luogo", QLineEdit()).text().strip(),
            "tipoServizio": self.qlines.get("tipoServizio", QLineEdit()).text().strip(),
            "postiTotali": int(self.qlines.get("postiTotali", QLineEdit()).text().strip() or 1)
        }
        ctrl.cudTurno("MODIFICA", cod, dati=dati)
        if self.callback:
            self.callback()


class VistaInserisciTurno(QWidget):
    """Vista per l'inserimento di un nuovo turno operativo (UML CUDTurno)."""
    def __init__(self, callback: Callable = None):
        super().__init__()
        self.callback = callback
        self.combo = QComboBox(self)
        self.qlines: dict[str, QLineEdit] = {}
        self.v_layout = QVBoxLayout(self)
        self._init_ui()

    def _init_ui(self):
        self.v_layout.addWidget(QLabel("Nuovo Turno Operativo"))
        self.combo.addItems(["Emergenza 118", "Trasporto Sanitario Ordinario", "Guardia Medica"])
        self.v_layout.addWidget(QLabel("Tipologia Servizio:"))
        self.v_layout.addWidget(self.combo)

        self.add_info_text("codice", "Codice Turno")
        self.add_info_text("data", "Data (YYYY-MM-DD)")
        self.add_info_text("oraInizio", "Ora Inizio (HH:MM)")
        self.add_info_text("oraFine", "Ora Fine (HH:MM)")
        self.add_info_text("luogo", "Luogo")
        self.add_info_text("postiTotali", "Posti Totali")

        btn_add = QPushButton("Crea Turno")
        btn_add.clicked.connect(self.aggiungi_turno)
        self.v_layout.addWidget(btn_add)

    def add_info_text(self, chiave: str, etichetta: str) -> None:
        lbl = QLabel(f"{etichetta}:")
        txt = QLineEdit(self)
        self.qlines[chiave] = txt
        self.v_layout.addWidget(lbl)
        self.v_layout.addWidget(txt)

    def aggiungi_turno(self) -> None:
        from GestioneTurniController import GestioneTurniController
        ctrl = GestioneTurniController()
        dati = {
            "codice": self.qlines.get("codice", QLineEdit()).text().strip(),
            "data": self.qlines.get("data", QLineEdit()).text().strip() or "2026-12-01",
            "oraInizio": self.qlines.get("oraInizio", QLineEdit()).text().strip() or "08:00",
            "oraFine": self.qlines.get("oraFine", QLineEdit()).text().strip() or "14:00",
            "luogo": self.qlines.get("luogo", QLineEdit()).text().strip() or "Sede CRI",
            "tipoServizio": self.combo.currentText(),
            "postiTotali": int(self.qlines.get("postiTotali", QLineEdit()).text().strip() or 2)
        }
        ctrl.cudTurno("INSERISCI", None, dati=dati)
        if self.callback:
            self.callback()


class VistaGestisciTurni(QWidget):
    """Vista per il referente per la consultazione e gestione dei turni (UML VisualizzaTurni / CUDTurno)."""
    def __init__(self):
        super().__init__()
        self.turni: list = []
        self.list_view = QListView(self)
        self.vista_new: Optional[VistaInserisciTurno] = None
        self.vista_mod: Optional[VistaModificaTurno] = None
        self._init_ui()
        self.load_turni()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Gestione Turni di Servizio (Referente):"))
        layout.addWidget(self.list_view)

        btns = QHBoxLayout()
        btn_new = QPushButton("Crea Nuovo Turno")
        btn_new.clicked.connect(self.show_new)
        btns.addWidget(btn_new)

        btn_mod = QPushButton("Modifica Turno Selezionato")
        btn_mod.clicked.connect(self.show_modifica)
        btns.addWidget(btn_mod)

        btn_del = QPushButton("Elimina Turno Selezionato")
        btn_del.clicked.connect(self.elimina_turno_click)
        btns.addWidget(btn_del)
        layout.addLayout(btns)

    def load_turni(self) -> None:
        from GestioneTurniController import GestioneTurniController
        ctrl = GestioneTurniController()
        self.turni = ctrl.visualizzaTurni()
        self.update_ui()

    def show_new(self) -> None:
        self.vista_new = VistaInserisciTurno(callback=self.load_turni)
        self.vista_new.show()

    def show_modifica(self) -> None:
        idx = self.list_view.currentIndex().row()
        if 0 <= idx < len(self.turni):
            t = self.turni[idx]
            self.vista_mod = VistaModificaTurno(t, callback=self.load_turni)
            self.vista_mod.show()

    def elimina_turno_click(self) -> None:
        idx = self.list_view.currentIndex().row()
        if 0 <= idx < len(self.turni):
            t = self.turni[idx]
            from GestioneTurniController import GestioneTurniController
            ctrl = GestioneTurniController()
            ctrl.cudTurno("RIMUOVI", getattr(t, "codice", ""))
            self.load_turni()

    def update_ui(self) -> None:
        model = QStringListModel()
        items = [f"{getattr(t, 'codice', '')} - {getattr(t, 'data', '')} ({getattr(t, 'oraInizio', '')}-{getattr(t, 'oraFine', '')}) - {getattr(t, 'tipoServizio', '')}" for t in self.turni]
        model.setStringList(items)
        self.list_view.setModel(model)


class GestioneTurni(QWidget):
    """Contenitore per la gestione turni referente."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.vista_gestisci = VistaGestisciTurni()
        layout.addWidget(self.vista_gestisci)
