from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

class ModificaDatiDialog(QDialog):
    def __init__(self, volontario, parent=None):
        super().__init__(parent)
        self.volontario = volontario
        self.setWindowTitle("Modifica dati personali")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        self.nome_edit = QLineEdit(volontario.nome)
        self.cognome_edit = QLineEdit(volontario.cognome)
        self.email_edit = QLineEdit(volontario.email)
        self.nascita_edit = QLineEdit(volontario.nascita)
        self.telefono_edit = QLineEdit(volontario.telefono)
        self.curriculum_edit = QTextEdit(volontario.curriculum)
        self.patenti_edit = QLineEdit(", ".join(volontario.patenti))
        self.compagnia_edit = QLineEdit(volontario.compagnia_appartenenza)
        self.disponibilita_edit = QLineEdit(", ".join(volontario.disponibilita))

        layout.addWidget(QLabel("Nome:"))
        layout.addWidget(self.nome_edit)
        layout.addWidget(QLabel("Cognome:"))
        layout.addWidget(self.cognome_edit)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_edit)
        layout.addWidget(QLabel("Data di nascita:"))
        layout.addWidget(self.nascita_edit)
        layout.addWidget(QLabel("Telefono:"))
        layout.addWidget(self.telefono_edit)
        layout.addWidget(QLabel("Curriculum:"))
        layout.addWidget(self.curriculum_edit)
        layout.addWidget(QLabel("Patenti (separate da virgola):"))
        layout.addWidget(self.patenti_edit)
        layout.addWidget(QLabel("Compagnia di appartenenza:"))
        layout.addWidget(self.compagnia_edit)
        layout.addWidget(QLabel("Disponibilità (es. lunedì, martedì):"))
        layout.addWidget(self.disponibilita_edit)

        salva_btn = QPushButton("Salva")
        salva_btn.clicked.connect(self.salva_dati)
        layout.addWidget(salva_btn)

        self.setLayout(layout)

    def salva_dati(self):
        self.volontario.nome = self.nome_edit.text().strip()
        self.volontario.cognome = self.cognome_edit.text().strip()
        nuova_email = self.email_edit.text().strip()
        if nuova_email != self.volontario.email:
            self.volontario.aggiorna_email(nuova_email)
        self.volontario.nascita = self.nascita_edit.text().strip()
        self.volontario.telefono = self.telefono_edit.text().strip()
        self.volontario.curriculum = self.curriculum_edit.toPlainText().strip()
        self.volontario.patenti = [p.strip() for p in self.patenti_edit.text().split(",") if p.strip()]
        self.volontario.compagnia_appartenenza = self.compagnia_edit.text().strip()
        self.volontario.disponibilita = [d.strip() for d in self.disponibilita_edit.text().split(",") if d.strip()]

        try:
            self.volontario.aggiorna_firestore()
            QMessageBox.information(self, "Successo", "✅ Dati aggiornati con successo.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"❌ Errore nel salvataggio: {e}")
