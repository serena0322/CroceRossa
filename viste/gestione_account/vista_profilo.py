"""VistaProfilo (GestioneAccount) secondo le specifiche del PDF e mockup (pag. 104).
Layout a due colonne:
- Titolo 'Profilo'
- Istruzione 'Modifica i tuoi recapiti e la password.'
- E-mail (QLineEdit)
- Telefono (QLineEdit)
- Nuova password (QLineEdit in modalità password)
- Banner di errore (es. 'La password non rispetta il formato richiesto.')
- Pulsante 'Salva modifiche' centrato
- Pulsante 'Elimina account' centrato sotto
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton
)
from utenti.utente import Utente
from supporto.stile import crea_label_errore, mostra_errore, nascondi_errore


class VistaProfilo(QWidget):
    def __init__(self, utente: Utente, parent=None):
        super(VistaProfilo, self).__init__(parent)
        self.utente = utente
        self.setWindowTitle("Profilo")
        self.resize(500, 360)

        self.qlines: dict[str, QLineEdit] = {}
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Intestazione come mockup pag. 104: "Profilo"

        lbl_sotto = QLabel("Modifica i tuoi recapiti e la password.")
        lbl_sotto.setStyleSheet("font-size: 13px; color: #4A5568;")
        main_layout.addWidget(lbl_sotto)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        d = self.utente.getDati()

        def add_row(key: str, label_text: str, default_val: str = "", is_pwd: bool = False, row_idx: int = 0):
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 13px; font-weight: 500;")
            txt = QLineEdit(self)
            txt.setText(str(default_val))
            if is_pwd:
                txt.setEchoMode(QLineEdit.Password)
            self.qlines[key] = txt
            grid.addWidget(lbl, row_idx, 0)
            grid.addWidget(txt, row_idx, 1)

        add_row("email", "E-mail", d.get("email", ""), row_idx=0)
        add_row("telefono", "Telefono", d.get("telefono", ""), row_idx=1)
        add_row("password", "Nuova password", "", is_pwd=True, row_idx=2)

        main_layout.addLayout(grid)

        # Banner errore
        self.lbl_errore = crea_label_errore(self)
        main_layout.addWidget(self.lbl_errore)

        # Pulsante centrato "Salva modifiche"
        btn_s_layout = QHBoxLayout()
        btn_s_layout.addStretch()
        btn_salva = QPushButton("Salva modifiche")
        btn_salva.setFixedWidth(200)
        btn_salva.clicked.connect(self.salva_modifiche_click)
        btn_s_layout.addWidget(btn_salva)
        btn_s_layout.addStretch()
        main_layout.addLayout(btn_s_layout)

        # Pulsante centrato "Elimina account"
        btn_e_layout = QHBoxLayout()
        btn_e_layout.addStretch()
        btn_elimina = QPushButton("Elimina account")
        btn_elimina.setFixedWidth(200)
        btn_elimina.clicked.connect(self.elimina_account_click)
        btn_e_layout.addWidget(btn_elimina)
        btn_e_layout.addStretch()
        main_layout.addLayout(btn_e_layout)

        self.setLayout(main_layout)

    def salva_modifiche_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        em = self.qlines["email"].text().strip()
        tel = self.qlines["telefono"].text().strip()
        pwd = self.qlines["password"].text().strip()
        if not pwd:
            pwd = self.utente.getPassword()

        ok = self.utente.modificaDati(em, tel, pwd)
        if ok:
            self.close()
        else:
            mostra_errore(self.lbl_errore, "La password non rispetta il formato richiesto o e-mail già usata.")

    def elimina_account_click(self) -> None:
        nascondi_errore(self.lbl_errore)
        self.utente.eliminaAccount()

        from PyQt5.QtWidgets import QApplication
        from viste.gestione_account.vista_login import VistaLogin

        app = QApplication.instance()
        self.vista_login = VistaLogin()
        self.vista_login.show()

        if app:
            for widget in app.topLevelWidgets():
                if widget is not self.vista_login:
                    widget.close()
