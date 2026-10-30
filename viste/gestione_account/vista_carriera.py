"""VistaCarriera (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 6)."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView, QMessageBox
from PyQt5.QtCore import QStringListModel
from utenti.volontario import Volontario


class VistaCarriera(QWidget):
    def __init__(self, volontario: Volontario, parent=None):
        super(VistaCarriera, self).__init__(parent)
        self.volontario = volontario
        self.setWindowTitle("La mia carriera")
        self.resize(460, 360)

        self.list_view = QListView(self)
        layout = QVBoxLayout(self)

        d = self.volontario.visualizzaCarriera()
        corsi = d.get("corsiSuperati", [])
        turni = d.get("turniSvolti", [])
        ore = d.get("oreServizio", 0.0)

        layout.addWidget(QLabel("<b>Corsi superati</b>"))
        lbl_corsi = QLabel("\n".join(corsi) if corsi else "Nessun corso superato.")
        layout.addWidget(lbl_corsi)

        layout.addWidget(QLabel("<b>Turni svolti</b>"))
        layout.addWidget(self.list_view)

        layout.addWidget(QLabel(f"<b>Totale ore di servizio:</b> {ore:.1f}"))

        self.setLayout(layout)
        self.load_carriera(turni)

    def load_carriera(self, turni: list) -> None:
        model = QStringListModel()
        righe = [f"Data: {data:%d/%m/%Y} | Turno: {cod}" for data, cod in turni]
        if not righe:
            righe = ["Nessun turno svolto."]
        model.setStringList(righe)
        self.list_view.setModel(model)
