"""Viste/PrenotazioneTurni: VistaDettagliTurno (VisualizzaDettagliTurno).
Secondo il mockup (pag. 13 del PDF di controllo), la vista dei dettagli e' in sola lettura.
La prenotazione si effettua dall'elenco (VistaTurniDisponibili).
"""
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from attivita.turno import Turno


class VistaDettagliTurno(QWidget):
    def __init__(self, turno: Turno, parent=None):
        super(VistaDettagliTurno, self).__init__(parent)
        self.turno = turno
        d = Turno().visualizzaDettagliTurno(turno)
        layout = QVBoxLayout()
        righe = [
            ("Codice", d["codice"]),
            ("Data", f"{d['data']:%d/%m/%Y}"),
            ("Orario", f"{d['oraInizio']:%H:%M} - {d['oraFine']:%H:%M}"),
            ("Luogo", d["luogo"]),
            ("Tipo di servizio", d["tipoServizio"]),
            ("Posti", f"{d['postiLiberi']} liberi su {d['postiTotali']}"),
            ("Patente richiesta", d["patenteRichiesta"] or "nessuna"),
            ("Corsi richiesti", d["corsiRichiesti"] or "nessuno"),
            ("Mezzo", d["mezzo"]),
            ("Materiale", d["materialeNecessario"]),
            ("Dati paziente", d["datiPaziente"] or "-")
        ]
        for etichetta, valore in righe:
            layout.addWidget(QLabel(f"{etichetta}: {valore}"))

        self.setLayout(layout)
        self.setWindowTitle(f"Dettagli turno {d['codice']}")
