"""VistaGestisciCorsi (GestioneCorsi): VisualizzaCorsi, CUDCorso, VisualizzaIscrittiCorso, AttestaPartecipazione."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QListView, QPushButton
)
from PyQt5.QtCore import QStringListModel
from attivita.corso import Corso
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaGestisciCorsi(QWidget):
    def __init__(self, parent=None):                      # create(): void
        super(VistaGestisciCorsi, self).__init__(parent)
        self.corsi: list[Corso] = []
        self.vista_iscritti = None      #associazione 0..1 VistaIscrittiCorso
        self.vista_attesta = None       #associazione 0..1 VistaAttestaPartecipazione
        self.vista_inserisci = None     #associazione 0..1 VistaInserisciCorso
        self.vista_modifica = None      # associazione 0..1 VistaModificaCorso

        self.setWindowTitle("Gestione corsi")
        self.resize(580, 420)

        layout = QVBoxLayout(self)

        self.list_view = QListView(self)
        layout.addWidget(self.list_view)

        row_azioni = QHBoxLayout()
        btn_iscritti = QPushButton("Visualizza iscritti")
        btn_iscritti.clicked.connect(self.visualizza_iscritti_click)
        row_azioni.addWidget(btn_iscritti)

        btn_attesta = QPushButton("Attesta partecipazione")
        btn_attesta.clicked.connect(self.attesta_partecipazione_click)
        row_azioni.addWidget(btn_attesta)
        layout.addLayout(row_azioni)

        layout.addWidget(QLabel("<b>Gestisci un corso</b>"))
        codice_row = QHBoxLayout()
        codice_row.addWidget(QLabel("Codice corso"))
        self.codice = QLineEdit(self)
        codice_row.addWidget(self.codice)
        layout.addLayout(codice_row)

        btn_row = QHBoxLayout()
        btn_ins = QPushButton("Inserisci")
        btn_ins.clicked.connect(self.inserisci_click)
        btn_mod = QPushButton("Modifica")
        btn_mod.clicked.connect(self.modifica_click)
        btn_rim = QPushButton("Rimuovi")
        btn_rim.clicked.connect(self.rimuovi_click)
        pulsanti_cud = (btn_ins, btn_mod, btn_rim)
        for b in pulsanti_cud:
            b.setEnabled(False)                           # codice vuoto: disattivati
            btn_row.addWidget(b)
        layout.addLayout(btn_row)

        self.lbl_errore = crea_label_errore(self)
        layout.addWidget(self.lbl_errore)

        # Attiva Inserisci/Modifica/Rimuovi solo se il codice non e' vuoto.
        # Non ricostruisce la lista, quindi la selezione dell'elenco non si perde.
        self.codice.textChanged.connect(
            lambda testo: [b.setEnabled(bool(testo.strip())) for b in pulsanti_cud])

        self.setLayout(layout)
        self.load_corsi()

    def load_corsi(self) -> None:
        self.corsi = Corso().visualizzaCorsi()            # dal piu' recente al meno recente
        self.update_ui()

    def update_ui(self) -> None:
        if self.corsi:
            righe = []
            for c in self.corsi:
                d = c.getDati()
                righe.append(
                    f"{d['codice']} | {d['nome']} | Inizio: {d['dataInizio']:%d/%m/%Y} | "
                    f"Stato: {c.getStato().value} | Posti liberi: {d['postiLiberi']}"
                )
        else:
            righe = ["Nessun corso presente."]            # VisualizzaCorsi 3.1
        self.list_view.setModel(QStringListModel(righe))
        if not self.corsi:
            mostra_errore(self.lbl_errore, "Nessun corso attivo presente.")
        else:
            nascondi_errore(self.lbl_errore)


    def _get_selected_corso(self) -> Corso | None:       # - get_selected_corso(): Corso
        idx = self.list_view.currentIndex().row()
        if 0 <= idx < len(self.corsi):
            return self.corsi[idx]
        return None

    def visualizza_iscritti_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        corso = self._get_selected_corso()
        if not corso:
            mostra_errore(self.lbl_errore, "Selezionare un corso dall'elenco.")
            return
        from viste.gestione_corsi.vista_iscritti_corso import VistaIscrittiCorso
        self.vista_iscritti = VistaIscrittiCorso(corso)
        self.vista_iscritti.show()

    def attesta_partecipazione_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        corso = self._get_selected_corso()
        if not corso:
            mostra_errore(self.lbl_errore, "Selezionare un corso dall'elenco.")
            return
        if not Corso().attestaPartecipazione(corso):
            mostra_errore(self.lbl_errore, "Il corso non è concluso o non ha iscritti.")
            return
        from viste.gestione_corsi.vista_attesta_partecipazione import VistaAttestaPartecipazione
        self.vista_attesta = VistaAttestaPartecipazione(corso)   # create(Corso)
        self.vista_attesta.show()

    def inserisci_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        if not Corso().inserisciCorso(cod):
            mostra_errore(self.lbl_errore, "Corso già presente.")         # CUDCorso 2.4.1
            return
        from viste.gestione_corsi.vista_inserisci_corso import VistaInserisciCorso
        self.vista_inserisci = VistaInserisciCorso(cod, self.load_corsi)
        self.vista_inserisci.show()

    def modifica_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        if not Corso().modificaCorso(cod):
            mostra_errore(self.lbl_errore, "Corso non trovato o non programmato.")   # CUDCorso 3.4.1
            return
        trovati = [c for c in self.corsi if c.getDati()["codice"] == cod]
        if not trovati:
            return
        from viste.gestione_corsi.vista_modifica_corso import VistaModificaCorso
        self.vista_modifica = VistaModificaCorso(trovati[0], self.load_corsi)
        self.vista_modifica.show()

    def rimuovi_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        if Corso().rimuoviCorso(cod):
            nascondi_errore(self.lbl_errore)
            self.load_corsi()
        else:
            mostra_errore(self.lbl_errore, "Corso non trovato o non programmato.")   # CUDCorso 4.4.1

