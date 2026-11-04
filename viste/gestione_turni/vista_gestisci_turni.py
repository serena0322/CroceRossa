"""VistaGestisciTurni (GestioneTurni).
Layout:
- Intestazione 'Gestisci turni'
- Tabella: Codice | Data | Luogo | Mezzo | Paziente | Patente
- Pulsante 'Visualizza prenotati' centrato
- Sezione 'Gestisci un turno':
  - Codice turno [line edit]
  - Tre pulsanti affiancati: Inserisci | Modifica | Elimina
- Banner di errore (es. 'Turno non trovato o non più programmato.')
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from attivita.turno import Turno
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore
from supporto.tabella import crea_tabella, popola_riga


class VistaGestisciTurni(QWidget):
    def __init__(self, parent=None):
        super(VistaGestisciTurni, self).__init__(parent)
        self.turni: list[Turno] = []
        self.vista_prenotati = None
        self.vista_inserisci = None
        self.vista_modifica = None

        self.setWindowTitle("Gestisci turni")
        self.resize(720, 520)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Tabella colonne: Codice | Data | Luogo | Mezzo | Paziente | Patente
        self.tabella = crea_tabella(["Codice", "Data", "Luogo", "Mezzo", "Paziente", "Patente"], self)
        main_layout.addWidget(self.tabella)

        # Pulsante centrato "Visualizza prenotati"
        btn_v_layout = QHBoxLayout()
        btn_v_layout.addStretch()
        btn_prenotati = QPushButton("Visualizza prenotati")
        btn_prenotati.setFixedWidth(240)
        btn_prenotati.clicked.connect(self.visualizza_prenotati_click)
        btn_v_layout.addWidget(btn_prenotati)
        btn_v_layout.addStretch()
        main_layout.addLayout(btn_v_layout)

        main_layout.addSpacing(6)

        # Sezione "Gestisci un turno"
        lbl_sezione = QLabel("<b>Gestisci un turno</b>")
        lbl_sezione.setStyleSheet("font-size: 13px; font-weight: bold; color: #2D3748;")
        main_layout.addWidget(lbl_sezione)

        codice_row = QHBoxLayout()
        codice_row.setSpacing(12)
        lbl_codice = QLabel("Codice turno")
        lbl_codice.setFixedWidth(120)
        lbl_codice.setStyleSheet("font-size: 13px; font-weight: 500;")
        codice_row.addWidget(lbl_codice)

        self.codice = QLineEdit(self)
        self.codice.textChanged.connect(self.update_pulsanti)
        codice_row.addWidget(self.codice, 1)
        main_layout.addLayout(codice_row)

        # Tre pulsanti: Inserisci | Modifica | Elimina
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_ins = QPushButton("Inserisci")
        self.btn_ins.clicked.connect(self.inserisci_click)
        btn_row.addWidget(self.btn_ins, 1)

        self.btn_mod = QPushButton("Modifica")
        self.btn_mod.clicked.connect(self.modifica_click)
        btn_row.addWidget(self.btn_mod, 1)

        self.btn_elim = QPushButton("Elimina")
        self.btn_elim.clicked.connect(self.elimina_click)
        btn_row.addWidget(self.btn_elim, 1)

        main_layout.addLayout(btn_row)

        # Banner di errore
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        self.setLayout(main_layout)
        self.load_turni()

    def load_turni(self) -> None:
        self.turni = Turno().visualizzaTurni()
        self.update_ui()

    def update_ui(self) -> None:
        self.tabella.setRowCount(len(self.turni))
        for r, t in enumerate(self.turni):
            d = t.getDati()
            pat_ok = "Sì" if t.verificaPatentePrenotati() else "No"
            paziente = d.get('datiPaziente', '').strip() or "-"
            popola_riga(self.tabella, r, [
                d.get("codice", ""),
                f"{d['data']:%d/%m/%Y}",
                d.get("luogo", ""),
                d.get("mezzo", "") or "-",
                paziente,
                pat_ok
            ])

        if not self.turni:
            mostra_errore(self.lbl_errore, "Nessun turno attivo presente.")
        else:
            nascondi_errore(self.lbl_errore)

        self.update_pulsanti()

    def update_pulsanti(self) -> None:
        ha_codice = bool(self.codice.text().strip())
        self.btn_ins.setEnabled(ha_codice)
        self.btn_mod.setEnabled(ha_codice)
        self.btn_elim.setEnabled(ha_codice)

    def visualizza_prenotati_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        idx = self.tabella.currentRow()
        if not (0 <= idx < len(self.turni)):
            mostra_errore(self.lbl_errore, "Selezionare un turno dall'elenco.")
            return
        turno = self.turni[idx]
        from viste.gestione_turni.vista_prenotati_turno import VistaPrenotatiTurno
        self.vista_prenotati = VistaPrenotatiTurno(turno)
        self.vista_prenotati.show()

    def inserisci_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        if not Turno().inserisciTurno(cod):
            mostra_errore(self.lbl_errore, f"Turno {cod} già presente.")
            return

        from viste.gestione_turni.vista_inserisci_turno import VistaInserisciTurno
        self.vista_inserisci = VistaInserisciTurno(cod, self.load_turni)
        self.vista_inserisci.show()

    def modifica_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        dati_t = Turno().modificaTurno(cod)
        if not dati_t:
            mostra_errore(self.lbl_errore, "Turno non trovato o non più programmato.")
            return

        trovati = [t for t in self.turni if t.getDati()["codice"] == cod]
        if not trovati:
            return
        from viste.gestione_turni.vista_modifica_turno import VistaModificaTurno
        self.vista_modifica = VistaModificaTurno(trovati[0], self.load_turni)
        self.vista_modifica.show()

    def elimina_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        ok = Turno().eliminaTurno(cod)
        if ok:
            nascondi_errore(self.lbl_errore)
            self.load_turni()
        else:
            mostra_errore(self.lbl_errore, "Turno non trovato o non più programmato.")
