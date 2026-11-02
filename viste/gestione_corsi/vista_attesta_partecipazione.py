"""VistaAttestaPartecipazione (GestioneCorsi) secondo le specifiche del PDF e mockup (pag. 107).
Layout:
- Intestazione: 'Attesta partecipazione - <codice> <nome>'
- Istruzione: 'Seleziona i Volontari che hanno superato il corso.'
- Checkbox con checkbox quadrata, nome e cognome
- Pulsante 'Conferma' centrato in basso
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QScrollArea, QPushButton
)
from attivita.corso import Corso
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaAttestaPartecipazione(QWidget):
    def __init__(self, corso: Corso, callback=None, parent=None):
        super(VistaAttestaPartecipazione, self).__init__(parent)
        self.corso = corso
        self.callback = callback
        self.iscritti = []
        self.checkboxes: list[tuple[QCheckBox, object]] = []

        d = self.corso.getDati()
        codice = d.get("codice", "")
        nome = d.get("nome", "")
        self.setWindowTitle(f"Attesta partecipazione - {codice} {nome}")
        self.resize(520, 400)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Intestazione come mockup: "Attesta partecipazione - C-028 BLSD"

        lbl_sottotitolo = QLabel("Seleziona i Volontari che hanno superato il corso.")
        lbl_sottotitolo.setStyleSheet("font-size: 13px; color: #4A5568;")
        main_layout.addWidget(lbl_sottotitolo)

        # Area scrollabile o contenitore per i checkbox
        self.box_widget = QWidget()
        self.box_layout = QVBoxLayout(self.box_widget)
        self.box_layout.setContentsMargins(10, 6, 10, 6)
        self.box_layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.box_widget)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #CBD5E0; border-radius: 4px; background: #FFFFFF; }")
        main_layout.addWidget(scroll, 1)

        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        # Pulsante centrato "Conferma"
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_conferma = QPushButton("Conferma")
        btn_conferma.setFixedWidth(200)
        btn_conferma.clicked.connect(self.conferma_superati_click)
        btn_layout.addWidget(btn_conferma)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.load_iscritti()

    def load_iscritti(self) -> None:
        self.iscritti = Corso().attestaPartecipazione(self.corso)
        for i in reversed(range(self.box_layout.count())):
            w = self.box_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.checkboxes.clear()

        # Verifica chi è già attestato superato
        superati_set = {
            isc.getVolontario() for isc in self.corso.getIscrizioni() if isc.getSuperato()
        }

        for v in self.iscritti:
            d = v.getDati()
            cb = QCheckBox(f"{d.get('nome', '')} {d.get('cognome', '')}")
            cb.setStyleSheet("font-size: 13px; font-weight: 500;")
            if v in superati_set:
                cb.setChecked(True)
            self.box_layout.addWidget(cb)
            self.checkboxes.append((cb, v))

        self.box_layout.addStretch()

    def conferma_superati_click(self) -> None:
        superati = [v for cb, v in self.checkboxes if cb.isChecked()]
        Corso().selezionaSuperati(self.corso, superati)
        if self.callback:
            self.callback()
        self.close()
