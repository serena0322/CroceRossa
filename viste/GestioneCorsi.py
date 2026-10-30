from __future__ import annotations
from typing import List, Callable, Optional, TYPE_CHECKING
from PyQt5.QtWidgets import (
    QWidget, QListView, QComboBox, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QLineEdit
)
from PyQt5.QtCore import QStringListModel

if TYPE_CHECKING:
    from Corso import Corso
    from Volontario import Volontario


class VistaAttestaPartecipazione(QWidget):
    """
    Vista UML: VistaAttestaPartecipazione (in GestioneCorsi)
    Attributi UML:
        corso: Corso
        list_iscritti: QListView
    Metodi UML:
        __init__(Corso)
        conferma_superati_click(): void
        load_iscritti(): void
    """
    def __init__(self, corso: Corso):
        super().__init__()
        self.corso = corso
        self.list_iscritti = QListView(self)
        self.iscritti: list = []
        self._init_ui()
        self.load_iscritti()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Registro Esiti Partecipazione: {getattr(self.corso, 'nome', '')}"))
        layout.addWidget(self.list_iscritti)
        btn_conferma = QPushButton("Attesta Superamento per Tutti gli Iscritti")
        btn_conferma.clicked.connect(self.conferma_superati_click)
        layout.addWidget(btn_conferma)

    def load_iscritti(self) -> None:
        """Carica la lista dei volontari iscritti al corso (UML)."""
        self.iscritti = list(getattr(self.corso, "partecipanti", []))
        model = QStringListModel()
        items = [f"{getattr(v, 'nome', '')} {getattr(v, 'cognome', '')} ({getattr(v, 'cod_fiscale', '')})" for v in self.iscritti]
        model.setStringList(items)
        self.list_iscritti.setModel(model)

    def conferma_superati_click(self) -> None:
        """Registra l'attestato di superamento per i partecipanti (UML AttestaPartecipazione)."""
        from GestioneFormazioneController import GestioneFormazioneController
        ctrl = GestioneFormazioneController()
        cod = getattr(self.corso, "codice", getattr(self.corso, "id", ""))
        ctrl.attestaPartecipazione(cod, self.iscritti)


class VistaModificaCorso(QWidget):
    """
    Vista UML: VistaModificaCorso (in GestioneCorsi)
    Attributi UML:
        callback: Function
        qlines: dict
        v_layout: QVBoxLayout
    Metodi UML:
        __init__(Corso, Function)
        add_info_text(str, str): void
        salva_modifiche(): void
    """
    def __init__(self, corso: Corso, callback: Callable = None):
        super().__init__()
        self.corso = corso
        self.callback = callback
        self.qlines: dict[str, QLineEdit] = {}
        self.v_layout = QVBoxLayout(self)
        self._init_ui()

    def _init_ui(self):
        self.v_layout.addWidget(QLabel(f"Modifica Corso: {getattr(self.corso, 'nome', '')}"))
        self.add_info_text("nome", "Nome Corso")
        self.add_info_text("luogo", "Luogo")
        self.add_info_text("orario", "Orario")
        self.add_info_text("postiTotali", "Posti Totali")

        if self.corso:
            if "nome" in self.qlines:
                self.qlines["nome"].setText(getattr(self.corso, "nome", ""))
            if "luogo" in self.qlines:
                self.qlines["luogo"].setText(getattr(self.corso, "luogo", ""))
            if "orario" in self.qlines:
                self.qlines["orario"].setText(getattr(self.corso, "orario", ""))
            if "postiTotali" in self.qlines:
                self.qlines["postiTotali"].setText(str(getattr(self.corso, "postiTotali", 20)))

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
        """Salva i dati aggiornati del corso (UML CUDCorso)."""
        from GestioneFormazioneController import GestioneFormazioneController
        ctrl = GestioneFormazioneController()
        cod = getattr(self.corso, "codice", getattr(self.corso, "id", ""))
        dati = {
            "nome": self.qlines.get("nome", QLineEdit()).text().strip(),
            "luogo": self.qlines.get("luogo", QLineEdit()).text().strip(),
            "orario": self.qlines.get("orario", QLineEdit()).text().strip(),
            "postiTotali": int(self.qlines.get("postiTotali", QLineEdit()).text().strip() or 20)
        }
        ctrl.cudCorso("MODIFICA", cod, dati=dati)
        if self.callback:
            self.callback()


class VistaCorso(QWidget):
    """
    Vista UML: VistaCorso (in GestioneCorsi)
    Attributi UML:
        elimina_callback: Function
        list_iscritti: QListView
    Metodi UML:
        __init__(Corso, Function)
        attesta_partecipazione_click(Corso): void
        elimina_corso_click(Corso): void
        load_iscritti(Corso): void
        modifica_corso_click(Corso): void
    """
    def __init__(self, corso: Corso, elimina_callback: Callable = None):
        super().__init__()
        self.corso = corso
        self.elimina_callback = elimina_callback
        self.list_iscritti = QListView(self)
        self.vista_attesta: Optional[VistaAttestaPartecipazione] = None
        self.vista_modifica: Optional[VistaModificaCorso] = None
        self._init_ui()
        self.load_iscritti(corso)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Scheda Corso: {getattr(self.corso, 'nome', '')}"))
        layout.addWidget(QLabel("Partecipanti:"))
        layout.addWidget(self.list_iscritti)

        btns = QHBoxLayout()
        btn_mod = QPushButton("Modifica Corso")
        btn_mod.clicked.connect(lambda: self.modifica_corso_click(self.corso))
        btns.addWidget(btn_mod)

        btn_attesta = QPushButton("Attesta Partecipazione")
        btn_attesta.clicked.connect(lambda: self.attesta_partecipazione_click(self.corso))
        btns.addWidget(btn_attesta)

        btn_del = QPushButton("Elimina Corso")
        btn_del.clicked.connect(lambda: self.elimina_corso_click(self.corso))
        btns.addWidget(btn_del)
        layout.addLayout(btns)

    def load_iscritti(self, corso: Corso) -> None:
        """Carica gli iscritti al corso (UML)."""
        model = QStringListModel()
        items = [f"{getattr(v, 'nome', '')} {getattr(v, 'cognome', '')}" for v in getattr(corso, "partecipanti", [])]
        model.setStringList(items)
        self.list_iscritti.setModel(model)

    def attesta_partecipazione_click(self, corso: Corso) -> None:
        """Apre la vista per attestare la partecipazione (UML)."""
        self.vista_attesta = VistaAttestaPartecipazione(corso)
        self.vista_attesta.show()

    def modifica_corso_click(self, corso: Corso) -> None:
        """Apre la vista di modifica del corso (UML)."""
        self.vista_modifica = VistaModificaCorso(corso, callback=lambda: self.load_iscritti(corso))
        self.vista_modifica.show()

    def elimina_corso_click(self, corso: Corso) -> None:
        """Elimina il corso dal sistema (UML CUDCorso)."""
        from GestioneFormazioneController import GestioneFormazioneController
        ctrl = GestioneFormazioneController()
        cod = getattr(corso, "codice", getattr(corso, "id", ""))
        ctrl.cudCorso("RIMUOVI", cod)
        if self.elimina_callback:
            self.elimina_callback()


class VistaInserisciCorso(QWidget):
    """
    Vista UML: VistaInserisciCorso (in GestioneCorsi - denominata VistaInserisciTurno nel diagramma per refuso grafico)
    Attributi UML:
        callback: Function
        combo: QComboBox
        qlines: dict
        v_layout: QVBoxLayout
    Metodi UML:
        __init__(Function)
        add_info_text(str, str): void
        aggiungi_corso(): void
        onChanged(str): void
    """
    def __init__(self, callback: Callable = None):
        super().__init__()
        self.callback = callback
        self.combo = QComboBox(self)
        self.qlines: dict[str, QLineEdit] = {}
        self.v_layout = QVBoxLayout(self)
        self._init_ui()

    def _init_ui(self):
        self.v_layout.addWidget(QLabel("Nuovo Corso di Formazione"))
        self.combo.addItems(["Sanitario", "Guida Emergenza", "Protezione Civile", "BLSD"])
        self.combo.currentTextChanged.connect(self.onChanged)
        self.v_layout.addWidget(QLabel("Tipologia:"))
        self.v_layout.addWidget(self.combo)

        self.add_info_text("codice", "Codice Corso")
        self.add_info_text("nome", "Nome / Titolo")
        self.add_info_text("dataInizio", "Data Inizio (YYYY-MM-DD)")
        self.add_info_text("dataFine", "Data Fine (YYYY-MM-DD)")
        self.add_info_text("luogo", "Luogo")
        self.add_info_text("postiTotali", "Posti Totali")

        btn_add = QPushButton("Crea Corso")
        btn_add.clicked.connect(self.aggiungi_corso)
        self.v_layout.addWidget(btn_add)

    def add_info_text(self, chiave: str, etichetta: str) -> None:
        lbl = QLabel(f"{etichetta}:")
        txt = QLineEdit(self)
        self.qlines[chiave] = txt
        self.v_layout.addWidget(lbl)
        self.v_layout.addWidget(txt)

    def onChanged(self, val: str) -> None:
        pass

    def aggiungi_corso(self) -> None:
        """Crea il nuovo corso registrandolo nel sistema (UML CUDCorso)."""
        from GestioneFormazioneController import GestioneFormazioneController
        ctrl = GestioneFormazioneController()
        dati = {
            "codice": self.qlines.get("codice", QLineEdit()).text().strip(),
            "nome": self.qlines.get("nome", QLineEdit()).text().strip(),
            "dataInizio": self.qlines.get("dataInizio", QLineEdit()).text().strip() or "2026-12-01",
            "dataFine": self.qlines.get("dataFine", QLineEdit()).text().strip() or "2026-12-02",
            "luogo": self.qlines.get("luogo", QLineEdit()).text().strip() or "Sede CRI",
            "tipoCorso": self.combo.currentText(),
            "postiTotali": int(self.qlines.get("postiTotali", QLineEdit()).text().strip() or 20)
        }
        ctrl.cudCorso("INSERISCI", None, dati=dati)
        if self.callback:
            self.callback()


# Alias con il nome visibile nel diagramma UML class Viste per esatta corrispondenza
VistaInserisciTurno = VistaInserisciCorso


class VistaGestisciCorsi(QWidget):
    """
    Vista UML: VistaGestisciCorsi (in GestioneCorsi)
    Attributi UML:
        corsi: list<Corso>
        list_view: QListView
    Metodi UML:
        __init__()
        load_corsi(): void
        show_new(): void
        show_selected_info(): void
        update_ui(): void
    """
    def __init__(self):
        super().__init__()
        self.corsi: list = []
        self.list_view = QListView(self)
        self.vista_new: Optional[VistaInserisciCorso] = None
        self.vista_dettaglio: Optional[VistaCorso] = None
        self._init_ui()
        self.load_corsi()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Gestione Corsi di Formazione (Referente):"))
        layout.addWidget(self.list_view)

        btns = QHBoxLayout()
        btn_new = QPushButton("Crea Nuovo Corso")
        btn_new.clicked.connect(self.show_new)
        btns.addWidget(btn_new)

        btn_info = QPushButton("Dettaglio Corso Selezionato")
        btn_info.clicked.connect(self.show_selected_info)
        btns.addWidget(btn_info)
        layout.addLayout(btns)

    def load_corsi(self) -> None:
        """Carica tutti i corsi presenti nel sistema (UML VisualizzaCorsi)."""
        from GestioneFormazioneController import GestioneFormazioneController
        ctrl = GestioneFormazioneController()
        self.corsi = ctrl.visualizzaCorsi()
        self.update_ui()

    def show_new(self) -> None:
        """Apre la schermata di creazione corso (UML)."""
        self.vista_new = VistaInserisciCorso(callback=self.load_corsi)
        self.vista_new.show()

    def show_selected_info(self) -> None:
        """Apre la scheda di gestione per il corso selezionato (UML)."""
        idx = self.list_view.currentIndex().row()
        if 0 <= idx < len(self.corsi):
            c = self.corsi[idx]
            self.vista_dettaglio = VistaCorso(c, elimina_callback=self.load_corsi)
            self.vista_dettaglio.show()

    def update_ui(self) -> None:
        """Aggiorna l'elenco corsi nella QListView (UML)."""
        model = QStringListModel()
        items = [f"{getattr(c, 'codice', '')} - {getattr(c, 'nome', '')} ({getattr(c, 'stato', '')})" for c in self.corsi]
        model.setStringList(items)
        self.list_view.setModel(model)


class GestioneCorsi(QWidget):
    """Contenitore per la gestione corsi referente."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.vista_gestisci = VistaGestisciCorsi()
        layout.addWidget(self.vista_gestisci)
