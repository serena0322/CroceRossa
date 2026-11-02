"""VistaHomeVolontario (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 104).
Layout:
- Intestazione: 'Croce Rossa Ancona - Home Volontario'
- Titolo grande: 'Ciao <Nome> <Cognome>'
- Sezione 'Area Utente':
    Riga 1: [Profilo]  [Carriera]
    Riga 2: [Le mie patenti] centrato/largo
- Sezione 'Area Attività':
    Riga 1: [Turni disponibili]   [Catalogo corsi]
    Riga 2: [Le mie prenotazioni] [Le mie iscrizioni]
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from utenti.volontario import Volontario


class VistaHomeVolontario(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaHomeVolontario, self).__init__(parent)
        self.volontario = volontario
        self.setWindowTitle("Croce Rossa Ancona - Home Volontario")
        self.resize(500, 380)

        self.vista_successiva = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(12)

        # Intestazione come mockup: "Croce Rossa Ancona - Home Volontario"

        d = self.volontario.getDati()
        lbl_welcome = QLabel(f"<b>Ciao {d.get('nome', '')} {d.get('cognome', '')}</b>")
        lbl_welcome.setStyleSheet("font-size: 18px; font-weight: bold; color: #1A202C;")
        main_layout.addWidget(lbl_welcome)

        # --- Sezione Area Utente ---
        lbl_account = QLabel("<b>Area Utente</b>")
        lbl_account.setStyleSheet("font-size: 13px; font-weight: bold; color: #2D3748; margin-top: 6px;")
        main_layout.addWidget(lbl_account)

        riga_ut1 = QHBoxLayout()
        riga_ut1.setSpacing(12)
        btn_prof = QPushButton("Profilo")
        btn_prof.clicked.connect(self.go_profilo)
        riga_ut1.addWidget(btn_prof, 1)

        btn_carr = QPushButton("Carriera")
        btn_carr.clicked.connect(self.go_carriera)
        riga_ut1.addWidget(btn_carr, 1)
        main_layout.addLayout(riga_ut1)

        riga_ut2 = QHBoxLayout()
        riga_ut2.setSpacing(12)
        btn_pat = QPushButton("Le mie patenti")
        btn_pat.clicked.connect(self.go_patenti)
        riga_ut2.addWidget(btn_pat, 1)
        main_layout.addLayout(riga_ut2)

        # --- Sezione Area Attività ---
        lbl_attivita = QLabel("<b>Area Attività</b>")
        lbl_attivita.setStyleSheet("font-size: 13px; font-weight: bold; color: #2D3748; margin-top: 8px;")
        main_layout.addWidget(lbl_attivita)

        riga_att1 = QHBoxLayout()
        riga_att1.setSpacing(12)
        btn_disp = QPushButton("Turni disponibili")
        btn_disp.clicked.connect(self.go_turni_disponibili)
        riga_att1.addWidget(btn_disp, 1)

        btn_cat = QPushButton("Catalogo corsi")
        btn_cat.clicked.connect(self.go_catalogo_corsi)
        riga_att1.addWidget(btn_cat, 1)
        main_layout.addLayout(riga_att1)

        riga_att2 = QHBoxLayout()
        riga_att2.setSpacing(12)
        btn_mie_pren = QPushButton("Le mie prenotazioni")
        btn_mie_pren.clicked.connect(self.go_prenotazioni)
        riga_att2.addWidget(btn_mie_pren, 1)

        btn_mie_iscr = QPushButton("Le mie iscrizioni")
        btn_mie_iscr.clicked.connect(self.go_iscrizioni)
        riga_att2.addWidget(btn_mie_iscr, 1)
        main_layout.addLayout(riga_att2)

        self.setLayout(main_layout)

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

    def go_profilo(self) -> None:
        from viste.gestione_account.vista_profilo import VistaProfilo
        self.vista_successiva = VistaProfilo(self.volontario)
        self.vista_successiva.show()

    def go_carriera(self) -> None:
        from viste.gestione_account.vista_carriera import VistaCarriera
        self.vista_successiva = VistaCarriera(self.volontario)
        self.vista_successiva.show()

    def go_patenti(self) -> None:
        from viste.gestione_patenti.vista_gestisci_patenti import VistaGestisciPatenti
        self.vista_successiva = VistaGestisciPatenti(self.volontario)
        self.vista_successiva.show()
