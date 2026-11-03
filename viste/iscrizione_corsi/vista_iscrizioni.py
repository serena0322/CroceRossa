"""VistaIscrizioni (IscrizioneCorsi) secondo le specifiche del PDF e mockup.
Layout:
- Intestazione 'Le mie iscrizioni'
- Tabella colonne: Nome | Codice | Data inizio | Luogo
- Pulsante 'Annulla iscrizione' centrato
- Banner di errore (es. 'Mancano meno di 2 giorni all'inizio del corso.')
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from utenti.volontario import Volontario
from attivita.iscrizione import Iscrizione
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore
from supporto.tabella import crea_tabella, popola_riga


class VistaIscrizioni(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaIscrizioni, self).__init__(parent)
        self.volontario = volontario
        self.iscrizioni: list[Iscrizione] = []

        self.setWindowTitle("Le mie iscrizioni")
        self.resize(580, 400)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        self.tabella = crea_tabella(["Nome", "Codice", "Data inizio", "Luogo"], self)
        main_layout.addWidget(self.tabella)

        # Pulsante centrato "Annulla iscrizione"
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_annulla = QPushButton("Annulla iscrizione")
        btn_annulla.setFixedWidth(220)
        btn_annulla.clicked.connect(self.annulla_iscrizione_click)
        btn_layout.addWidget(btn_annulla)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        #errore
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        self.setLayout(main_layout)
        self.load_iscrizioni()

    def load_iscrizioni(self) -> None:
        self.iscrizioni = self.volontario.visualizzaIscrizioni()
        self.update_ui()

    def update_ui(self) -> None:
        self.tabella.setRowCount(len(self.iscrizioni))
        for r, i in enumerate(self.iscrizioni):
            d = i.getDatiCorso()
            popola_riga(self.tabella, r, [
                d.get("nome", ""),
                d.get("codice", ""),
                f"{d['dataInizio']:%d/%m/%Y}",
                d.get("luogo", "")
            ])

        if not self.iscrizioni:
            mostra_errore(self.lbl_errore, "Nessuna iscrizione attiva presente.")
        else:
            nascondi_errore(self.lbl_errore)

    def annulla_iscrizione_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        idx = self.tabella.currentRow()
        if not (0 <= idx < len(self.iscrizioni)):
            mostra_errore(self.lbl_errore, "Selezionare un'iscrizione dall'elenco.")
            return

        iscr = self.iscrizioni[idx]
        ok = self.volontario.annullaIscrizione(iscr)
        if ok:
            nascondi_errore(self.lbl_errore)
            self.load_iscrizioni()
        else:
            mostra_errore(self.lbl_errore, "Mancano meno di 2 giorni all'inizio del corso.")
