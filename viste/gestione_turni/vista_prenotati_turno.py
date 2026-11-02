"""VistaPrenotatiTurno (GestioneTurni) secondo le specifiche del PDF e mockup (pag. 104).
Layout:
- Intestazione: 'Prenotati al turno <codice>'
- Tabella: Nome | Cognome | E-mail | Telefono | Prenotato il
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from attivita.turno import Turno
from supporto.tabella import crea_tabella, popola_riga


class VistaPrenotatiTurno(QWidget):
    def __init__(self, turno: Turno, parent=None):
        super(VistaPrenotatiTurno, self).__init__(parent)
        self.turno = turno

        d = self.turno.getDati()
        codice = d.get("codice", "")
        self.setWindowTitle(f"Prenotati al turno {codice}")
        self.resize(650, 360)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Intestazione come mockup pag. 104: "Prenotati al turno T-170"

        # Tabella colonne: Nome | Cognome | E-mail | Telefono | Prenotato il
        self.tabella = crea_tabella(["Nome", "Cognome", "E-mail", "Telefono", "Prenotato il"], self)
        main_layout.addWidget(self.tabella)

        self.setLayout(main_layout)
        self.load_prenotati()

    def load_prenotati(self) -> None:
        prenotazioni = sorted(self.turno.getPrenotazioni(), key=lambda p: p.getDataPrenotazione())
        self.tabella.setRowCount(len(prenotazioni))
        for r, p in enumerate(prenotazioni):
            vol = p.getVolontario()
            d = vol.getDati() if vol else {}
            data_p = p.getDataPrenotazione()
            str_data = f"{data_p:%d/%m/%Y}" if data_p else "-"
            popola_riga(self.tabella, r, [
                d.get("nome", ""),
                d.get("cognome", ""),
                d.get("email", ""),
                d.get("telefono", ""),
                str_data
            ])
