"""VistaCarriera (GestioneAccount).
Layout:
- Intestazione 'Carriera'
- Sezione 'Corsi superati': tabella con colonna 'Corso'
- Sezione 'Turni svolti': tabella con colonne 'Data' e 'Codice'
- Totale ore di servizio: 'Ore di servizio totali: <ore>'
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from utenti.volontario import Volontario
from supporto.tabella import crea_tabella, popola_riga


class VistaCarriera(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaCarriera, self).__init__(parent)
        self.volontario = volontario
        self.setWindowTitle("Carriera")
        self.resize(520, 480)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)


        d = self.volontario.visualizzaCarriera()
        corsi = d.get("corsiSuperati", [])
        turni = d.get("turniSvolti", [])
        ore = d.get("oreServizio", 0.0)

        lbl_corsi = QLabel("<b>Corsi superati</b>")
        lbl_corsi.setStyleSheet("font-size: 13px; font-weight: bold; color: #2D3748;")
        main_layout.addWidget(lbl_corsi)

        self.tabella_corsi = crea_tabella(["Corso"], self)
        main_layout.addWidget(self.tabella_corsi)

        lbl_turni = QLabel("<b>Turni svolti</b>")
        lbl_turni.setStyleSheet("font-size: 13px; font-weight: bold; color: #2D3748;")
        main_layout.addWidget(lbl_turni)

        self.tabella_turni = crea_tabella(["Data", "Codice"], self)
        main_layout.addWidget(self.tabella_turni)

        self.lbl_ore = QLabel(f"<b>Ore di servizio totali:</b> {ore:g}")
        self.lbl_ore.setStyleSheet("font-size: 13px; font-weight: bold; color: #1A202C;")
        main_layout.addWidget(self.lbl_ore)

        self.setLayout(main_layout)
        self.load_carriera(corsi, turni)

    def load_carriera(self, corsi: list, turni: list) -> None:
        self.tabella_corsi.setRowCount(len(corsi))
        for r, c in enumerate(corsi):
            popola_riga(self.tabella_corsi, r, [c])

        self.tabella_turni.setRowCount(len(turni))
        for r, (data, cod) in enumerate(turni):
            popola_riga(self.tabella_turni, r, [f"{data:%d/%m/%Y}", cod])
