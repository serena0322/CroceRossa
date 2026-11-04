"""VistaIscrittiCorso (GestioneCorsi).
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

        layout.addWidget(QLabel(f"Iscritti al corso {codice}"))

        self.tabella = crea_tabella(["Nome", "Cognome", "E-mail", "Telefono", "Iscritto il"], self)
        layout.addWidget(self.tabella)

        self.setLayout(layout)
        self.load_iscritti()

    def load_iscritti(self) -> None:
        iscritti = Corso().visualizzaIscrittiCorso(self.corso)
        self.tabella.setRowCount(len(iscritti))
        for r, d in enumerate(iscritti):
            popola_riga(self.tabella, r, [
                d.get("nome", ""),
                d.get("cognome", ""),
                d.get("email", ""),
                d.get("telefono", ""),
                f"{d['dataIscrizione']:%d/%m/%Y}"
            ])
