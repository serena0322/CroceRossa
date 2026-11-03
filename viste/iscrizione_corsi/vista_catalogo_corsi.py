"""VistaCatalogoCorsi (IscrizioneCorsi) secondo le specifiche del PDF e mockup (catalogo_corsi.png).
Layout:
- Intestazione 'Catalogo corsi'
- Riga filtro: 'Tipo di corso' [QLineEdit testo libero]  [Pulsante Filtra]
- Tabella colonne: Codice | Nome | Posti liberi
- Due pulsanti: 'Dettagli' e 'Iscriviti' affiancati
- Banner di errore: 'Sei già iscritto a questo corso.'
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton
)
from utenti.volontario import Volontario
from attivita.corso import Corso
from attivita.iscrizione import Iscrizione
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore
from supporto.tabella import crea_tabella, popola_riga


class VistaCatalogoCorsi(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaCatalogoCorsi, self).__init__(parent)
        self.volontario = volontario
        self.corsi: list[Corso] = []
        self.vista_dettagli = None

        self.setWindowTitle("Catalogo corsi")
        self.resize(600, 440)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Intestazione come mockup: "Catalogo corsi"

        # Riga filtro: Tipo di corso [QLineEdit]   [Filtra]
        filtro_row = QHBoxLayout()
        filtro_row.setSpacing(12)

        lbl_tipo = QLabel("Tipo di corso")
        lbl_tipo.setStyleSheet("font-size: 13px; font-weight: 500;")
        filtro_row.addWidget(lbl_tipo)

        self.tipo_filtro = QLineEdit(self)
        self.tipo_filtro.setPlaceholderText("Es. Sanitario, Base...")
        filtro_row.addWidget(self.tipo_filtro, 1)

        btn_filtra = QPushButton("Filtra")
        btn_filtra.setFixedWidth(160)
        btn_filtra.clicked.connect(self.filtra_corsi_click)
        filtro_row.addWidget(btn_filtra)

        main_layout.addLayout(filtro_row)

        # Tabella colonne da mockup: Codice | Nome | Posti liberi
        self.tabella = crea_tabella(["Codice", "Nome", "Posti liberi"], self)
        main_layout.addWidget(self.tabella)

        # Pulsanti [Dettagli] e [Iscriviti] affiancati
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        btn_dett = QPushButton("Dettagli")
        btn_dett.clicked.connect(self.show_selected_info)
        btn_row.addWidget(btn_dett, 1)

        btn_iscr = QPushButton("Iscriviti")
        btn_iscr.clicked.connect(self.iscrivi_click)
        btn_row.addWidget(btn_iscr, 1)

        main_layout.addLayout(btn_row)

        # Banner errore (es. 'Sei già iscritto a questo corso.')
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        self.setLayout(main_layout)
        self.load_corsi()

    def load_corsi(self) -> None:
        self.corsi = Corso().visualizzaCatalogoCorsi()
        self.update_ui()

    def filtra_corsi_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        tipo = self.tipo_filtro.text().strip()
        if not tipo or tipo.lower() == "tutti":
            self.corsi = Corso().visualizzaCatalogoCorsi()
        else:
            self.corsi = Corso().filtraCorsi(tipo)
        self.update_ui()
        if not self.corsi:
            mostra_errore(self.lbl_errore, "Nessun corso trovato con il filtro specificato.")
        

    def update_ui(self) -> None:
        self.tabella.setRowCount(len(self.corsi))
        for r, c in enumerate(self.corsi):
            d = c.getDati()
            popola_riga(self.tabella, r, [
                d.get("codice", ""),
                d.get("nome", ""),
                str(d.get("postiLiberi", 0))
            ])

        if not self.corsi:
            mostra_errore(self.lbl_errore, "Nessun corso disponibile a catalogo.")
        else:
            nascondi_errore(self.lbl_errore)

    def show_selected_info(self) -> None:
        nascondi_errore(self.lbl_errore)
        idx = self.tabella.currentRow()
        if not (0 <= idx < len(self.corsi)):
            mostra_errore(self.lbl_errore, "Selezionare un corso dall'elenco.")
            return
        from viste.iscrizione_corsi.vista_dettagli_corso import VistaDettagliCorso
        self.vista_dettagli = VistaDettagliCorso(self.corsi[idx])
        self.vista_dettagli.show()

    def iscrivi_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        idx = self.tabella.currentRow()
        if not (0 <= idx < len(self.corsi)):
            mostra_errore(self.lbl_errore, "Selezionare un corso dall'elenco.")
            return

        corso = self.corsi[idx]
        ok = Iscrizione().iscriviCorso(corso, self.volontario)
        if ok:
            nascondi_errore(self.lbl_errore)
            self.load_corsi()
        else:
            mostra_errore(self.lbl_errore, "Sei già iscritto a questo corso.")
