"""VistaGestisciPatenti (GestionePatenti) secondo le specifiche del PDF e mockup (pag. 104).
Layout:
- Intestazione 'Le mie patenti'
- Tabella: Codice | Tipo | Data di scadenza
- Sezione 'Gestisci una patente':
  - Codice patente [line edit]
  - Tre pulsanti affiancati: Inserisci | Modifica | Rimuovi
- Banner di errore (es. 'Codice già presente.')
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from utenti.volontario import Volontario
from utenti.patente import Patente
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore
from supporto.tabella import crea_tabella, popola_riga


class VistaGestisciPatenti(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaGestisciPatenti, self).__init__(parent)
        self.volontario = volontario
        self.patenti: list[Patente] = []
        self.vista_inserisci = None
        self.vista_modifica = None

        self.setWindowTitle("Le mie patenti")
        self.resize(600, 460)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)


        self.tabella = crea_tabella(["Codice", "Tipo", "Data di scadenza"], self)
        main_layout.addWidget(self.tabella)

        main_layout.addSpacing(6)

        # Sezione "Gestisci una patente"
        lbl_sezione = QLabel("<b>Gestisci una patente</b>")
        lbl_sezione.setStyleSheet("font-size: 13px; font-weight: bold; color: #2D3748;")
        main_layout.addWidget(lbl_sezione)

        codice_row = QHBoxLayout()
        codice_row.setSpacing(12)
        lbl_codice = QLabel("Codice patente")
        lbl_codice.setFixedWidth(120)
        lbl_codice.setStyleSheet("font-size: 13px; font-weight: 500;")
        codice_row.addWidget(lbl_codice)

        self.codice = QLineEdit(self)
        self.codice.textChanged.connect(self.update_pulsanti)
        codice_row.addWidget(self.codice, 1)
        main_layout.addLayout(codice_row)

        # Tre pulsanti: Inserisci | Modifica | Rimuovi
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_ins = QPushButton("Inserisci")
        self.btn_ins.clicked.connect(self.inserisci_click)
        btn_row.addWidget(self.btn_ins, 1)

        self.btn_mod = QPushButton("Modifica")
        self.btn_mod.clicked.connect(self.modifica_click)
        btn_row.addWidget(self.btn_mod, 1)

        self.btn_rim = QPushButton("Rimuovi")
        self.btn_rim.clicked.connect(self.rimuovi_click)
        btn_row.addWidget(self.btn_rim, 1)

        main_layout.addLayout(btn_row)

        #errore
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        self.setLayout(main_layout)
        self.load_patenti()

    def load_patenti(self) -> None:
        self.patenti = self.volontario.visualizzaPatenti()
        self.update_ui()

    def update_ui(self) -> None:
        self.tabella.setRowCount(len(self.patenti))
        for r, p in enumerate(self.patenti):
            d = p.getDati()
            popola_riga(self.tabella, r, [
                d.get("codice", ""),
                d.get("tipo", ""),
                f"{d['dataScadenza']:%d/%m/%Y}"
            ])

        if not self.patenti:
            mostra_errore(self.lbl_errore, "Nessuna patente presente.")
        else:
            nascondi_errore(self.lbl_errore)

        self.update_pulsanti()

    def update_pulsanti(self) -> None:
        ha_codice = bool(self.codice.text().strip())
        self.btn_ins.setEnabled(ha_codice)
        self.btn_mod.setEnabled(ha_codice)
        self.btn_rim.setEnabled(ha_codice)

    def inserisci_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        if not Patente().inserisciPatente(cod):
            mostra_errore(self.lbl_errore, "Codice già presente.")
            return

        from viste.gestione_patenti.vista_inserisci_patente import VistaInserisciPatente
        self.vista_inserisci = VistaInserisciPatente(cod, self.volontario, self.load_patenti)
        self.vista_inserisci.show()

    def modifica_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        dati_p = Patente().modificaPatente(cod, self.volontario)
        if not dati_p:
            mostra_errore(self.lbl_errore, "Patente non trovata o non appartenente al tuo account.")
            return

        trovate = [p for p in self.patenti if p.getDati()["codice"] == cod]
        if not trovate:
            return
        from viste.gestione_patenti.vista_modifica_patente import VistaModificaPatente
        self.vista_modifica = VistaModificaPatente(trovate[0], self.load_patenti)
        self.vista_modifica.show()

    def rimuovi_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        ok = Patente().rimuoviPatente(cod, self.volontario)
        if ok:
            nascondi_errore(self.lbl_errore)
            self.load_patenti()
        else:
            mostra_errore(self.lbl_errore, "Patente non trovata.")
