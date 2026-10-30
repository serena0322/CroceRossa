"""VistaHomeReferente (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 6)."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from utenti.referente import Referente


class VistaHomeReferente(QWidget):
    def __init__(self, referente: Referente, parent=None):
        super(VistaHomeReferente, self).__init__(parent)
        self.referente = referente
        self.setWindowTitle("Home – Referente")
        self.resize(450, 240)

        self.vista_successiva = None

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        d = self.referente.getDati()
        settore = d.get("settoreGestito", "Emergenza")
        lbl_head = QLabel(f"Benvenuto – Settore {settore}")
        lbl_head.setProperty("heading", "true")
        layout.addWidget(lbl_head)

        riga1 = QHBoxLayout()
        btn_turni = QPushButton("Gestisci turni")
        btn_turni.clicked.connect(self.go_gestisci_turni)
        riga1.addWidget(btn_turni)

        btn_corsi = QPushButton("Gestisci corsi")
        btn_corsi.clicked.connect(self.go_gestisci_corsi)
        riga1.addWidget(btn_corsi)
        layout.addLayout(riga1)

        riga2 = QHBoxLayout()
        btn_stats = QPushButton("Statistiche")
        btn_stats.clicked.connect(self.go_statistiche)
        riga2.addWidget(btn_stats)

        btn_prof = QPushButton("Profilo")
        btn_prof.clicked.connect(self.go_profilo)
        riga2.addWidget(btn_prof)
        layout.addLayout(riga2)

        self.setLayout(layout)

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
