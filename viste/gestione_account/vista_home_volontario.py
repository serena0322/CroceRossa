"""VistaHomeVolontario (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 5)."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from utenti.volontario import Volontario


class VistaHomeVolontario(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaHomeVolontario, self).__init__(parent)
        self.volontario = volontario
        self.setWindowTitle("Home – Volontario")
        self.resize(450, 320)

        # Riferimenti per evitare che Python distrugga le finestre aperte
        self.vista_successiva = None

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        d = self.volontario.getDati()
        lbl_welcome = QLabel(f"Benvenuto, {d.get('nome', '')} {d.get('cognome', '')}")
        lbl_welcome.setProperty("heading", "true")
        layout.addWidget(lbl_welcome)

        lbl_turni = QLabel("Turni")
        lbl_turni.setProperty("section", "true")
        layout.addWidget(lbl_turni)

        turni_layout = QHBoxLayout()
        btn_disp = QPushButton("Turni disponibili")
        btn_disp.clicked.connect(self.go_turni_disponibili)
        turni_layout.addWidget(btn_disp)

        btn_mie_pren = QPushButton("Le mie prenotazioni")
        btn_mie_pren.clicked.connect(self.go_prenotazioni)
        turni_layout.addWidget(btn_mie_pren)
        layout.addLayout(turni_layout)

        lbl_corsi = QLabel("Corsi")
        lbl_corsi.setProperty("section", "true")
        layout.addWidget(lbl_corsi)

        corsi_layout = QHBoxLayout()
        btn_cat = QPushButton("Catalogo corsi")
        btn_cat.clicked.connect(self.go_catalogo_corsi)
        corsi_layout.addWidget(btn_cat)

        btn_mie_iscr = QPushButton("Le mie iscrizioni")
        btn_mie_iscr.clicked.connect(self.go_iscrizioni)
        corsi_layout.addWidget(btn_mie_iscr)
        layout.addLayout(corsi_layout)

        lbl_account = QLabel("Il mio account")
        lbl_account.setProperty("section", "true")
        layout.addWidget(lbl_account)
        account_layout = QHBoxLayout()
        btn_pat = QPushButton("Le mie patenti")
        btn_pat.clicked.connect(self.go_patenti)
        account_layout.addWidget(btn_pat)

        btn_carr = QPushButton("Carriera")
        btn_carr.clicked.connect(self.go_carriera)
        account_layout.addWidget(btn_carr)

        btn_prof = QPushButton("Profilo")
        btn_prof.clicked.connect(self.go_profilo)
        account_layout.addWidget(btn_prof)
        layout.addLayout(account_layout)

        self.setLayout(layout)

    def go_turni_disponibili(self) -> None:
        from viste.prenotazione_turni.vista_turni_disponibili import VistaTurniDisponibili
        self.vista_successiva = VistaTurniDisponibili(self.volontario)
        self.vista_successiva.show()

    def go_prenotazioni(self) -> None:
        from viste.prenotazione_turni.vista_prenotazioni import VistaPrenotazioni
        self.vista_successiva = VistaPrenotazioni(self.volontario)
        self.vista_successiva.show()

    def go_catalogo_corsi(self) -> None:
        from viste.iscrizione_corsi.vista_catalogo_corsi import VistaCatalogoCorsi
        self.vista_successiva = VistaCatalogoCorsi(self.volontario)
        self.vista_successiva.show()

    def go_iscrizioni(self) -> None:
        from viste.iscrizione_corsi.vista_iscrizioni import VistaIscrizioni
        self.vista_successiva = VistaIscrizioni(self.volontario)
        self.vista_successiva.show()

    def go_patenti(self) -> None:
        from viste.gestione_patenti.vista_gestisci_patenti import VistaGestisciPatenti
        self.vista_successiva = VistaGestisciPatenti(self.volontario)
        self.vista_successiva.show()

    def go_carriera(self) -> None:
        from viste.gestione_account.vista_carriera import VistaCarriera
        self.vista_successiva = VistaCarriera(self.volontario)
        self.vista_successiva.show()

    def go_profilo(self) -> None:
        from viste.gestione_account.vista_profilo import VistaProfilo
        self.vista_successiva = VistaProfilo(self.volontario)
        self.vista_successiva.show()
