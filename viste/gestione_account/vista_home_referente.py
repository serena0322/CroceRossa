"""VistaHomeReferente (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 104).
Layout:
- Intestazione: 'Croce Rossa Ancona - Home Referente'
- Saluto: 'Ciao'
- Due righe con 2 pulsanti affiancati:
    Riga 1: [Profilo]        [Statistiche]
    Riga 2: [Gestisci turni] [Gestisci corsi]
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from utenti.referente import Referente


class VistaHomeReferente(QWidget):
    def __init__(self, referente: Referente, parent=None):
        super(VistaHomeReferente, self).__init__(parent)
        self.referente = referente
        self.setWindowTitle("Croce Rossa Ancona - Home Referente")
        self.resize(500, 260)

        self.vista_successiva = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(14)

        # Intestazione come mockup: "Croce Rossa Ancona - Home Referente"

        lbl_ciao = QLabel("<b>Ciao</b>")
        lbl_ciao.setStyleSheet("font-size: 18px; font-weight: bold; color: #1A202C;")
        main_layout.addWidget(lbl_ciao)

        # Griglia 2x2 dei pulsanti esattamente come da mockup:
        # Riga 1: [Profilo] [Statistiche]
        riga1 = QHBoxLayout()
        riga1.setSpacing(12)
        btn_prof = QPushButton("Profilo")
        btn_prof.clicked.connect(self.go_profilo)
        riga1.addWidget(btn_prof, 1)

        btn_stats = QPushButton("Statistiche")
        btn_stats.clicked.connect(self.go_statistiche)
        riga1.addWidget(btn_stats, 1)
        main_layout.addLayout(riga1)

        # Riga 2: [Gestisci turni] [Gestisci corsi]
        riga2 = QHBoxLayout()
        riga2.setSpacing(12)
        btn_turni = QPushButton("Gestisci turni")
        btn_turni.clicked.connect(self.go_gestisci_turni)
        riga2.addWidget(btn_turni, 1)

        btn_corsi = QPushButton("Gestisci corsi")
        btn_corsi.clicked.connect(self.go_gestisci_corsi)
        riga2.addWidget(btn_corsi, 1)
        main_layout.addLayout(riga2)

        self.setLayout(main_layout)

    def go_gestisci_turni(self) -> None:
        from viste.gestione_turni.vista_gestisci_turni import VistaGestisciTurni
        self.vista_successiva = VistaGestisciTurni()
        self.vista_successiva.show()

    def go_gestisci_corsi(self) -> None:
        from viste.gestione_corsi.vista_gestisci_corsi import VistaGestisciCorsi
        self.vista_successiva = VistaGestisciCorsi()
        self.vista_successiva.show()

    def go_statistiche(self) -> None:
        from viste.gestione_account.vista_statistiche import VistaStatistiche
        self.vista_successiva = VistaStatistiche()
        self.vista_successiva.show()

    def go_profilo(self) -> None:
        from viste.gestione_account.vista_profilo import VistaProfilo
        self.vista_successiva = VistaProfilo(self.referente)
        self.vista_successiva.show()
