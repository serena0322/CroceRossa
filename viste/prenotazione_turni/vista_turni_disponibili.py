"""VistaTurniDisponibili (PrenotazioneTurni).
Layout:
- Intestazione 'Turni disponibili'
- Filtri su riga:
    'Data' [date picker]   'Tipo di servizio' [line edit]
- Pulsante 'Filtra' centrato
- Tabella: Codice | Data | Orario | Posti liberi
- Due pulsanti: 'Dettagli' e 'Prenota' affiancati
- Banner di errore (es. 'Sei già prenotato a un turno che si sovrappone.')
"""
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDateEdit, QPushButton
)
from PyQt5.QtCore import QDate
from attivita.turno import Turno
from attivita.prenotazione import Prenotazione
from utenti.volontario import Volontario
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore
from supporto.tabella import crea_tabella, popola_riga


class VistaTurniDisponibili(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaTurniDisponibili, self).__init__(parent)
        self.volontario = volontario
        self.turni: list[Turno] = []
        self.vista_dettagli = None

        self.setWindowTitle("Turni disponibili")
        self.resize(650, 480)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Riga filtri
        filtro_layout = QHBoxLayout()
        filtro_layout.setSpacing(14)

        lbl_data = QLabel("Data")
        lbl_data.setStyleSheet("font-size: 13px; font-weight: 500;")
        filtro_layout.addWidget(lbl_data)

        self.data_filtro = QDateEdit(self)
        self.data_filtro.setDate(QDate.currentDate())
        self.data_filtro.setCalendarPopup(True)
        filtro_layout.addWidget(self.data_filtro, 1)

        lbl_tipo = QLabel("Tipo di servizio")
        lbl_tipo.setStyleSheet("font-size: 13px; font-weight: 500;")
        filtro_layout.addWidget(lbl_tipo)

        self.tipo = QLineEdit(self)
        self.tipo.setPlaceholderText("Es. Trasporto sanitario")
        filtro_layout.addWidget(self.tipo, 1)

        main_layout.addLayout(filtro_layout)

        # Pulsante centrato "Filtra"
        btn_f_layout = QHBoxLayout()
        btn_f_layout.addStretch()
        btn_filtra = QPushButton("Filtra")
        btn_filtra.setFixedWidth(160)
        btn_filtra.clicked.connect(self.filtra_turni_click)
        btn_f_layout.addWidget(btn_filtra)
        btn_f_layout.addStretch()
        main_layout.addLayout(btn_f_layout)

        # Tabella colonne: Codice | Data | Orario | Posti liberi
        self.tabella = crea_tabella(["Codice", "Data", "Orario", "Posti liberi"], self)
        main_layout.addWidget(self.tabella)

        # Due pulsanti: [Dettagli] [Prenota]
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_dettagli = QPushButton("Dettagli")
        btn_dettagli.clicked.connect(self.show_selected_info)
        btn_row.addWidget(btn_dettagli, 1)

        btn_prenota = QPushButton("Prenota")
        btn_prenota.clicked.connect(self.prenota_turno_click)
        btn_row.addWidget(btn_prenota, 1)
        main_layout.addLayout(btn_row)

        # Banner di errore
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        self.setLayout(main_layout)
        self.load_turni()

    def load_turni(self) -> None:
        self.turni = Turno().visualizzaTurniDisponibili()
        self.update_ui()

    def filtra_turni_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        qd = self.data_filtro.date()
        d = date(qd.year(), qd.month(), qd.day())
        tipo = self.tipo.text().strip()

        # Filtra per data e tipo servizio
        self.turni = Turno().filtraTurni(d, tipo)
        self.update_ui()
        if not self.turni:
            mostra_errore(self.lbl_errore, "Nessun turno trovato con i criteri selezionati.")


    def update_ui(self) -> None:
        self.tabella.setRowCount(len(self.turni))
        for r, t in enumerate(self.turni):
            d = t.getDati()
            popola_riga(self.tabella, r, [
                d.get("codice", ""),
                f"{d['data']:%d/%m/%Y}",
                f"{d['oraInizio']:%H:%M}-{d['oraFine']:%H:%M}",
                str(d.get("postiLiberi", 0))
            ])

        if not self.turni:
            mostra_errore(self.lbl_errore, "Nessun turno disponibile presente.")
        else:
            nascondi_errore(self.lbl_errore)

    def show_selected_info(self) -> None:
        nascondi_errore(self.lbl_errore)
        idx = self.tabella.currentRow()
        if not (0 <= idx < len(self.turni)):
            mostra_errore(self.lbl_errore, "Selezionare un turno dall'elenco.")
            return
        from viste.prenotazione_turni.vista_dettagli_turno import VistaDettagliTurno
        self.vista_dettagli = VistaDettagliTurno(self.turni[idx])
        self.vista_dettagli.show()

    def prenota_turno_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        idx = self.tabella.currentRow()
        if not (0 <= idx < len(self.turni)):
            mostra_errore(self.lbl_errore, "Selezionare un turno dall'elenco.")
            return

        turno = self.turni[idx]
        msg = Prenotazione().prenotaTurno(turno, self.volontario)
        if msg:
            if "sovrappone" in msg.lower():
                msg = "Sei già prenotato a un turno che si sovrappone."
            mostra_errore(self.lbl_errore, msg)
            return

        self.load_turni()
