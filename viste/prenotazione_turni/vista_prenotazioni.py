"""VistaPrenotazioni (PrenotazioneTurni).
Layout:
- Intestazione 'Le mie prenotazioni'
- Tabella (Data, Orario, Codice turno)
- Pulsante 'Annulla prenotazione' centrato in basso
- Banner di errore (es. 'Mancano meno di 24 ore all'inizio del turno.')
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from utenti.volontario import Volontario
from attivita.prenotazione import Prenotazione
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore
from supporto.tabella import crea_tabella, popola_riga


class VistaPrenotazioni(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaPrenotazioni, self).__init__(parent)
        self.volontario = volontario
        self.prenotazioni: list[Prenotazione] = []

        self.setWindowTitle("Le mie prenotazioni")
        self.resize(550, 400)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Tabella colonne: Data | Orario | Codice turno
        self.tabella = crea_tabella(["Data", "Orario", "Codice turno"], self)
        main_layout.addWidget(self.tabella)

        # Pulsante centrato "Annulla prenotazione"
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_annulla = QPushButton("Annulla prenotazione")
        btn_annulla.setFixedWidth(220)
        btn_annulla.clicked.connect(self.annulla_prenotazione_click)
        btn_layout.addWidget(btn_annulla)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # Banner d'errore
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        self.setLayout(main_layout)
        self.load_prenotazioni()

    def load_prenotazioni(self) -> None:
        self.prenotazioni = self.volontario.visualizzaPrenotazioni()
        self.update_ui()

    def update_ui(self) -> None:
        self.tabella.setRowCount(len(self.prenotazioni))
        for r, p in enumerate(self.prenotazioni):
            d = p.getDatiTurno()
            popola_riga(self.tabella, r, [
                f"{d['data']:%d/%m/%Y}",
                f"{d['oraInizio']:%H:%M}-{d['oraFine']:%H:%M}",
                d.get("codice", "")
            ])

        if not self.prenotazioni:
            mostra_errore(self.lbl_errore, "Nessuna prenotazione attiva presente.")
        else:
            nascondi_errore(self.lbl_errore)

    def annulla_prenotazione_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        idx = self.tabella.currentRow()
        if not (0 <= idx < len(self.prenotazioni)):
            mostra_errore(self.lbl_errore, "Selezionare una prenotazione dall'elenco.")
            return

        prenotazione = self.prenotazioni[idx]
        ok = self.volontario.annullaPrenotazione(prenotazione)
        if ok:
            nascondi_errore(self.lbl_errore)
            self.load_prenotazioni()
        else:
            mostra_errore(self.lbl_errore, "Mancano meno di 24 ore all'inizio del turno.")
