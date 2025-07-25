# ruolo_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel

class RuoloDialog(QDialog):
    def __init__(self, ruoli_disponibili, callback_ruolo_scelto):
        super().__init__()
        self.setWindowTitle("Scegli il ruolo")
        self.callback_ruolo_scelto = callback_ruolo_scelto

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Scegli il ruolo per questo turno:"))

        for ruolo in ruoli_disponibili:
            btn = QPushButton(ruolo.capitalize())
            btn.clicked.connect(lambda _, r=ruolo: self.seleziona_ruolo(r))
            layout.addWidget(btn)

        self.setLayout(layout)

    def seleziona_ruolo(self, ruolo):
        self.callback_ruolo_scelto(ruolo)
        self.accept()
