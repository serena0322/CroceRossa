"""VistaGestisciCorsi (GestioneCorsi) secondo le specifiche del PDF e mockup (pag. 107).
Layout:
- Intestazione 'Gestisci corsi'
- Tabella (Codice, Nome, Data Inizio, Stato, Posti liberi)
- Riga con due pulsanti affiancati: 'Visualizza iscritti' e 'Attesta partecipazione'
- Banner errore orizzontale ('Il corso non è concluso o non ha iscritti.')
- Sezione 'Gestisci un corso':
    - Riga 'Codice corso' con QLineEdit
    - Tre pulsanti affiancati: 'Inserisci', 'Modifica', 'Elimina'
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from attivita.corso import Corso
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore
from supporto.tabella import crea_tabella, popola_riga


class VistaGestisciCorsi(QWidget):
    def __init__(self, parent=None):
        super(VistaGestisciCorsi, self).__init__(parent)
        self.corsi: list[Corso] = []
        self.vista_iscritti = None
        self.vista_attesta = None
        self.vista_inserisci = None
        self.vista_modifica = None

        self.setWindowTitle("Gestisci corsi")
        self.resize(700, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.tabella = crea_tabella(["Codice", "Nome", "Data Inizio", "Stato", "Posti liberi"], self)
        layout.addWidget(self.tabella)

        # Due pulsanti: [Visualizza iscritti] [Attesta partecipazione]
        row_azioni = QHBoxLayout()
        row_azioni.setSpacing(12)
        btn_iscritti = QPushButton("Visualizza iscritti")
        btn_iscritti.clicked.connect(self.visualizza_iscritti_click)
        row_azioni.addWidget(btn_iscritti, 1)

        btn_attesta = QPushButton("Attesta partecipazione")
        btn_attesta.clicked.connect(self.attesta_partecipazione_click)
        row_azioni.addWidget(btn_attesta, 1)
        layout.addLayout(row_azioni)

        # errore 
        self.lbl_errore = crea_label_errore(self)
        layout.addWidget(self.lbl_errore)

        layout.addSpacing(6)

        # Sezione "Gestisci un corso"
        lbl_sezione = QLabel("<b>Gestisci un corso</b>")
        lbl_sezione.setStyleSheet("font-size: 13px; font-weight: bold; color: #2D3748;")
        layout.addWidget(lbl_sezione)

        codice_row = QHBoxLayout()
        codice_row.setSpacing(12)
        lbl_codice = QLabel("Codice corso")
        lbl_codice.setFixedWidth(120)
        lbl_codice.setStyleSheet("font-size: 13px; font-weight: 500;")
        codice_row.addWidget(lbl_codice)

        self.codice = QLineEdit(self)
        self.codice.textChanged.connect(self.update_pulsanti)
        codice_row.addWidget(self.codice, 1)
        layout.addLayout(codice_row)

        # Tre pulsanti affiancati: Inserisci | Modifica | Elimina
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

        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.load_corsi()

    def load_corsi(self) -> None:
        self.corsi = Corso().visualizzaCorsi()
        self.update_ui()

    def update_ui(self) -> None:
        self.tabella.setRowCount(len(self.corsi))
        for r, c in enumerate(self.corsi):
            d = c.getDati()
            popola_riga(self.tabella, r, [
                d.get("codice", ""),
                d.get("nome", ""),
                f"{d['dataInizio']:%d/%m/%Y}",
                c.getStato().value,
                str(d.get("postiLiberi", 0))
            ])

        if not self.corsi:
            mostra_errore(self.lbl_errore, "Nessun corso attivo presente.")
        else:
            nascondi_errore(self.lbl_errore)

        self.update_pulsanti()

    def update_pulsanti(self) -> None:
        ha_codice = bool(self.codice.text().strip())
        self.btn_ins.setEnabled(ha_codice)
        self.btn_mod.setEnabled(ha_codice)
        self.btn_elim.setEnabled(ha_codice)

    def _get_selected_corso(self) -> Corso | None:
        idx = self.tabella.currentRow()
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
        iscritti = Corso().attestaPartecipazione(corso)
        if not iscritti:
            mostra_errore(self.lbl_errore, "Il corso non è concluso o non ha iscritti.")
            return

        from viste.gestione_corsi.vista_attesta_partecipazione import VistaAttestaPartecipazione
        self.vista_attesta = VistaAttestaPartecipazione(corso) #levato self.load_corsi.
        self.vista_attesta.show()

    def inserisci_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        if not Corso().inserisciCorso(cod):
            mostra_errore(self.lbl_errore, f"Corso {cod} già presente.")
            return

        from viste.gestione_corsi.vista_inserisci_corso import VistaInserisciCorso
        self.vista_inserisci = VistaInserisciCorso(cod, self.load_corsi)
        self.vista_inserisci.show()

    def modifica_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        dati_c = Corso().modificaCorso(cod)
        if not dati_c:
            mostra_errore(self.lbl_errore, "Corso non trovato o non programmato.")
            return

        trovati = [c for c in self.corsi if c.getDati()["codice"] == cod]
        if not trovati:
            return
        from viste.gestione_corsi.vista_modifica_corso import VistaModificaCorso
        self.vista_modifica = VistaModificaCorso(trovati[0], self.load_corsi)
        self.vista_modifica.show()

    def elimina_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        cod = self.codice.text().strip()
        ok = Corso().eliminaCorso(cod)
        if ok:
            nascondi_errore(self.lbl_errore)
            self.load_corsi()
        else:
            mostra_errore(self.lbl_errore, "Corso non trovato o non programmato.")
