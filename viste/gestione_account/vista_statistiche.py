"""VistaStatistiche (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 7)."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QListView
from PyQt5.QtCore import QStringListModel
from statistiche.gestore_statistiche import GestoreStatistiche


class VistaStatistiche(QWidget):
    def __init__(self, parent=None):
        super(VistaStatistiche, self).__init__(parent)
        self.setWindowTitle("Statistiche")
        self.resize(500, 380)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Categoria:</b>"))

        self.combo = QComboBox(self)
        self.combo.addItems(["volontari", "turni", "corsi"])
        self.combo.currentTextChanged.connect(self.onChanged)
        layout.addWidget(self.combo)

        self.label_risultati = QLabel(self)
        layout.addWidget(self.label_risultati)

        self.list_view = QListView(self)
        layout.addWidget(self.list_view)

        self.setLayout(layout)
        self.onChanged("volontari")

    def onChanged(self, categoria: str) -> None:
        stats = GestoreStatistiche().gestisciStatistiche(categoria)
        self.mostra_statistiche(categoria, stats)

    def mostra_statistiche(self, categoria: str, d: dict) -> None:
        if not d:
            self.label_risultati.setText("Nessun dato per la categoria scelta.")
            self.list_view.setModel(QStringListModel([]))
            return

        if categoria == "volontari":
            ore_tot = d.get('oreServizioTotali', d.get('oreTotali', 0.0))
            media_ore = d.get('mediaOreServizio', d.get('mediaOre', 0.0))
            txt = (
                f"Volontari registrati: {d.get('numeroVolontari', 0)}\n"
                f"Ore di servizio totali: {ore_tot:.1f}\n"
                f"Media ore per volontario: {media_ore:.1f}"
            )
            self.label_risultati.setText(txt)
            model = QStringListModel()
            righe = [f"{nome} {cognome} — {ore:.1f} ore" for nome, cognome, ore in d.get("classifica", [])]
            model.setStringList(righe)
            self.list_view.setModel(model)
        elif categoria == "turni":
            occ_media = d.get('percentualeMediaPostiOccupati', d.get('occupazioneMediaConclusi', 0.0))
            turni_stato = d.get('turniPerStato', d.get('perStato', {}))
            turni_tipo = d.get('turniPerTipoServizio', d.get('perTipo', {}))
            txt = (
                f"Prenotazioni totali: {d.get('prenotazioniTotali', 0)}\n"
                f"Percentuale media posti occupati (conclusi): {occ_media:.1f}%\n"
                f"Per stato: {turni_stato}\n"
                f"Per tipo servizio: {turni_tipo}"
            )
            self.label_risultati.setText(txt)
            self.list_view.setModel(QStringListModel([]))
        elif categoria == "corsi":
            occ_media = d.get('percentualeMediaPostiOccupati', d.get('occupazioneMediaConclusi', 0.0))
            corsi_stato = d.get('corsiPerStato', d.get('perStato', {}))
            corsi_tipo = d.get('corsiPerTipo', d.get('perTipo', {}))
            superati = d.get('percentualeSuperatiPerCorso', d.get('percentualeSuperati', {}))
            txt = (
                f"Iscrizioni totali: {d.get('iscrizioniTotali', 0)}\n"
                f"Percentuale media posti occupati (conclusi): {occ_media:.1f}%\n"
                f"Per stato: {corsi_stato}\n"
                f"Per tipo corso: {corsi_tipo}\n"
                f"Percentuale superati per corso: {superati}"
            )
            self.label_risultati.setText(txt)
            self.list_view.setModel(QStringListModel([]))
