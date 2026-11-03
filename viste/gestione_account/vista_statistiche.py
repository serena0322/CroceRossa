"""VistaStatistiche (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 104).
Layout:
- Intestazione 'Statistiche'
- Menu a tendina 'Categoria' [Volontari | Turni e prenotazioni | Corsi e iscrizioni]
- In base alla categoria selezionata mostra le sezioni statistiche e le tabelle allineate secondo i mockup.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QComboBox, QTableWidget
)
from statistiche.gestore_statistiche import GestoreStatistiche
from supporto.tabella import crea_tabella, popola_riga


class VistaStatistiche(QWidget):
    def __init__(self, parent=None):
        super(VistaStatistiche, self).__init__(parent)
        self.setWindowTitle("Statistiche")
        self.resize(550, 480)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Intestazione come mockup pag. 104: "Statistiche"

        cat_layout = QHBoxLayout()
        cat_layout.setSpacing(16)
        lbl_cat = QLabel("Categoria")
        lbl_cat.setFixedWidth(120)
        lbl_cat.setStyleSheet("font-size: 13px; font-weight: 500;")
        cat_layout.addWidget(lbl_cat)

        self.combo = QComboBox(self)
        self.combo.addItems(["Volontari", "Turni e prenotazioni", "Corsi e iscrizioni"])
        self.combo.currentTextChanged.connect(self.on_Changed)
        cat_layout.addWidget(self.combo, 1)
        main_layout.addLayout(cat_layout)

        # Contenitore dinamico delle statistiche
        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        main_layout.addWidget(self.content_widget, 1)

        self.setLayout(main_layout)
        self.on_Changed("Volontari")

    def on_Changed(self, cat_label: str) -> None:
        # Pulisce i widget correnti
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            w = item.widget()
            l = item.layout()
            if w:
                w.setParent(None)
            elif l:
                while l.count():
                    sub = l.takeAt(0).widget()
                    if sub:
                        sub.setParent(None)

        if cat_label == "Volontari":
            self._render_volontari()
        elif cat_label == "Turni e prenotazioni":
            self._render_turni()
        elif cat_label == "Corsi e iscrizioni":
            self._render_corsi()

    def _render_volontari(self) -> None:
        stats = GestoreStatistiche().gestisciStatistiche("volontari")
        if not stats:
            self.content_layout.addWidget(QLabel("Nessun dato disponibile."))
            return

        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(6)

        ore_tot = stats.get('oreServizioTotali', stats.get('oreTotali', 0.0))
        media_ore = stats.get('mediaOreServizio', stats.get('mediaOre', 0.0))
        n_vol = stats.get('numeroVolontari', 0)

        righe = [
            ("Volontari registrati", str(n_vol)),
            ("Ore di servizio totali", f"{ore_tot:g}"),
            ("Media ore per volontario", f"{media_ore:.1f}")
        ]
        for r, (k, v) in enumerate(righe):
            lbl_k = QLabel(k)
            lbl_k.setStyleSheet("font-size: 13px; font-weight: 500;")
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet("font-size: 13px;")
            grid.addWidget(lbl_k, r, 0)
            grid.addWidget(lbl_v, r, 1)

        self.content_layout.addLayout(grid)
        self.content_layout.addSpacing(6)

        # Tabella classifica ore: Volontario | Ore di servizio
        tabella = crea_tabella(["Volontario", "Ore di servizio"], self)
        classifica = stats.get("classifica", [])
        tabella.setRowCount(len(classifica))
        for r, (nome, cognome, ore) in enumerate(classifica):
            popola_riga(tabella, r, [
                f"{nome} {cognome}",
                f"{ore:g}"
            ])
        self.content_layout.addWidget(tabella, 1)

    def _render_turni(self) -> None:
        stats = GestoreStatistiche().gestisciStatistiche("turni")
        if not stats:
            self.content_layout.addWidget(QLabel("Nessun dato disponibile."))
            return

        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(6)

        turni_stato = stats.get('turniPerStato', stats.get('perStato', {}))
        prog = turni_stato.get("PROGRAMMATO", 0)
        inc = turni_stato.get("IN_CORSO", 0)
        conc = turni_stato.get("CONCLUSO", 0)
        pren_tot = stats.get("prenotazioniTotali", 0)
        occ = stats.get("percentualeMediaPostiOccupati", stats.get("occupazioneMediaConclusi", 0.0))

        lbl_s = QLabel("<b>Turni per stato</b>")
        lbl_s.setStyleSheet("font-size: 13px; font-weight: bold; color: #2D3748;")
        self.content_layout.addWidget(lbl_s)

        righe_stato = [
            ("Programmati", str(prog)),
            ("In corso", str(inc)),
            ("Conclusi", str(conc))
        ]
        for r, (k, v) in enumerate(righe_stato):
            lbl_k = QLabel(k)
            lbl_k.setStyleSheet("font-size: 13px; font-weight: 500;")
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet("font-size: 13px;")
            grid.addWidget(lbl_k, r, 0)
            grid.addWidget(lbl_v, r, 1)

        self.content_layout.addLayout(grid)
        self.content_layout.addSpacing(6)

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(30)
        grid2.setVerticalSpacing(6)
        righe_tot = [
            ("Prenotazioni totali", str(pren_tot)),
            ("Posti occupati (turni conclusi)", f"{round(occ)}%")
        ]
        for r, (k, v) in enumerate(righe_tot):
            lbl_k = QLabel(k)
            lbl_k.setStyleSheet("font-size: 13px; font-weight: 500;")
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet("font-size: 13px;")
            grid2.addWidget(lbl_k, r, 0)
            grid2.addWidget(lbl_v, r, 1)

        self.content_layout.addLayout(grid2)
        self.content_layout.addStretch()

    def _render_corsi(self) -> None:
        stats = GestoreStatistiche().gestisciStatistiche("corsi")
        if not stats:
            self.content_layout.addWidget(QLabel("Nessun dato disponibile."))
            return

        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(6)

        corsi_stato = stats.get('corsiPerStato', stats.get('perStato', {}))
        prog = corsi_stato.get("PROGRAMMATO", 0)
        inc = corsi_stato.get("IN_CORSO", 0)
        conc = corsi_stato.get("CONCLUSO", 0)
        isc_tot = stats.get("iscrizioniTotali", 0)
        occ = stats.get("percentualeMediaPostiOccupati", stats.get("occupazioneMediaConclusi", 0.0))

        lbl_s = QLabel("<b>Corsi per stato</b>")
        lbl_s.setStyleSheet("font-size: 13px; font-weight: bold; color: #2D3748;")
        self.content_layout.addWidget(lbl_s)

        righe_stato = [
            ("Programmati", str(prog)),
            ("In corso", str(inc)),
            ("Conclusi", str(conc))
        ]
        for r, (k, v) in enumerate(righe_stato):
            lbl_k = QLabel(k)
            lbl_k.setStyleSheet("font-size: 13px; font-weight: 500;")
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet("font-size: 13px;")
            grid.addWidget(lbl_k, r, 0)
            grid.addWidget(lbl_v, r, 1)

        self.content_layout.addLayout(grid)
        self.content_layout.addSpacing(6)

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(30)
        grid2.setVerticalSpacing(6)
        righe_tot = [
            ("Iscrizioni totali", str(isc_tot)),
            ("Posti occupati (corsi conclusi)", f"{round(occ)}%")
        ]
        for r, (k, v) in enumerate(righe_tot):
            lbl_k = QLabel(k)
            lbl_k.setStyleSheet("font-size: 13px; font-weight: 500;")
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet("font-size: 13px;")
            grid2.addWidget(lbl_k, r, 0)
            grid2.addWidget(lbl_v, r, 1)

        self.content_layout.addLayout(grid2)
        self.content_layout.addSpacing(6)

        # Tabella superati: Corso concluso | % iscritti che lo hanno superato
        tabella = crea_tabella(["Corso concluso", "% iscritti che lo hanno superato"], self)
        superati_dict = stats.get("percentualeSuperati", stats.get("percentualeSuperatiPerCorso", {}))
        tabella.setRowCount(len(superati_dict))
        for r, (corso_nome, perc) in enumerate(superati_dict.items()):
            popola_riga(tabella, r, [
                str(corso_nome),
                f"{round(perc)}%"
            ])
        self.content_layout.addWidget(tabella, 1)
