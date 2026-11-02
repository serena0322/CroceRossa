"""VistaIscrittiCorso (GestioneCorsi) secondo le specifiche del PDF e mockup (pag. 107).
Layout:
- Intestazione: 'Iscritti al corso <codice>'
- Tabella: Nome | Cognome | E-mail | Telefono | Iscritto il
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from attivita.corso import Corso
from supporto.tabella import crea_tabella, popola_riga


class VistaIscrittiCorso(QWidget):
    def __init__(self, corso: Corso, parent=None):
        super(VistaIscrittiCorso, self).__init__(parent)
        self.corso = corso

        d = self.corso.getDati()
        codice = d.get("codice", "")
        self.setWindowTitle(f"Iscritti al corso {codice}")
        self.resize(650, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Intestazione come nel mockup di pagina 107: "Iscritti al corso C-028"

        self.tabella = crea_tabella(["Nome", "Cognome", "E-mail", "Telefono", "Iscritto il"], self)
        layout.addWidget(self.tabella)

        self.setLayout(layout)
        self.load_iscritti()

    def load_iscritti(self) -> None:
        iscrizioni = sorted(self.corso.getIscrizioni(), key=lambda i: i.getDataIscrizione())
        self.tabella.setRowCount(len(iscrizioni))
        for r, isc in enumerate(iscrizioni):
            vol = isc.getVolontario()
            d = vol.getDati() if vol else {}
            data_isc = isc.getDataIscrizione()
            str_data = f"{data_isc:%d/%m/%Y}" if data_isc else "-"
            popola_riga(self.tabella, r, [
                d.get("nome", ""),
                d.get("cognome", ""),
                d.get("email", ""),
                d.get("telefono", ""),
                str_data
            ])
