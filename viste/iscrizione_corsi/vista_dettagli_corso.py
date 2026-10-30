"""VistaDettagliCorso (IscrizioneCorsi) secondo le specifiche del PDF e mockup (pag. 14)."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from attivita.corso import Corso


class VistaDettagliCorso(QWidget):
    def __init__(self, corso: Corso, parent=None):
        super(VistaDettagliCorso, self).__init__(parent)
        self.corso = corso
        d = Corso().visualizzaDettagliCorso(corso)

        self.setWindowTitle(f"Dettagli corso {d['codice']}")
        self.resize(420, 340)

        layout = QVBoxLayout(self)
        righe = [
            ("Nome", d["nome"]),
            ("Descrizione", d["descrizione"]),
            ("Direttore del corso", d["direttoreCorso"]),
            ("Tipo di corso", d["tipoCorso"]),
            ("Date", f"{d['dataInizio']:%d/%m/%Y} – {d['dataFine']:%d/%m/%Y}"),
            ("Luogo / orario", f"{d['luogo']} · {d['orario']}"),
            ("Posti totali / liberi", f"{d['postiTotali']} / {d['postiLiberi']}")
        ]
        for etichetta, valore in righe:
            layout.addWidget(QLabel(f"<b>{etichetta}:</b> {valore}"))

        self.setLayout(layout)
