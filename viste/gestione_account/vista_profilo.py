"""VistaProfilo (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 6)."""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from utenti.utente import Utente
from utenti.volontario import Volontario


class VistaProfilo(QWidget):
    def __init__(self, utente: Utente, parent=None):
        super(VistaProfilo, self).__init__(parent)
        self.utente = utente
        self.setWindowTitle("Il mio profilo")
        self.resize(420, 320)

        self.qlines: dict[str, QLineEdit] = {}
        self.v_layout = QVBoxLayout(self)

        d = self.utente.getDati()
        self.v_layout.addWidget(QLabel(f"<b>Dati attuali:</b> {d.get('email', '')} · {d.get('telefono', '')}"))

        self.add_info_text("email", "Nuova e-mail")
        self.add_info_text("telefono", "Nuovo telefono")
        self.add_info_text("password", "Nuova password")

        self.qlines["email"].setText(d.get("email", ""))
        self.qlines["telefono"].setText(d.get("telefono", ""))

        btn_box = QHBoxLayout()
        btn_salva = QPushButton("Salva modifiche")
        btn_salva.clicked.connect(self.salva_modifiche_click)
        btn_box.addWidget(btn_salva)

        btn_elimina = QPushButton("Elimina account")
        btn_elimina.clicked.connect(self.elimina_account_click)
        btn_box.addWidget(btn_elimina)
        self.v_layout.addLayout(btn_box)

        self.setLayout(self.v_layout)

    def add_info_text(self, chiave: str, etichetta: str) -> None:
        self.v_layout.addWidget(QLabel(f"{etichetta}:"))
        txt = QLineEdit(self)
        if chiave == "password":
            txt.setEchoMode(QLineEdit.Password)
        self.qlines[chiave] = txt
        self.v_layout.addWidget(txt)

    def salva_modifiche_click(self) -> None:
        em = self.qlines["email"].text().strip()
        tel = self.qlines["telefono"].text().strip()
        pwd = self.qlines["password"].text().strip()
        if not pwd:
            pwd = self.utente.getPassword()

        ok = self.utente.modificaDati(em, tel, pwd)
        if ok:
            QMessageBox.information(self, "Profilo", "Dati modificati con successo.")
            self.close()
        else:
            QMessageBox.critical(self, "Errore", "E-mail già usata o password non valida.")

    def elimina_account_click(self) -> None:
        rep = QMessageBox.question(
            self, "Conferma eliminazione",
            "Sei sicuro di voler eliminare definitivamente il tuo account?",
            QMessageBox.Yes | QMessageBox.No
        )
        if rep == QMessageBox.Yes:
            self.utente.eliminaAccount()
            QMessageBox.information(self, "Account eliminato", "Account eliminato con successo.")
            self.close()
