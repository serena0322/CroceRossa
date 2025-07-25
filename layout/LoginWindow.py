from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTabWidget, QMessageBox, QSpacerItem, QSizePolicy
)
from FirebaseConfig import api_key
from FirebaseConfig import db
from Sistema import Sistema
from auth import login_utente, registra_utente

class LoginWindow(QWidget):
    def __init__(self, sistema: Sistema, callback_login_success):
        super().__init__()
        self.setWindowTitle("🔐 Accesso - Croce Rossa")
        self.resize(350, 300)
        self.sistema = sistema
        self.callback_login_success = callback_login_success

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: "Helvetica Neue", Arial;
                font-size: 14px;
            }
            QLineEdit, QPushButton {
                background-color: #2e2e2e;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 6px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)

        tab_widget = QTabWidget()
        tab_widget.addTab(self.login_tab(), "🔑 Login")
        tab_widget.addTab(self.register_tab(), "📝 Registrati")

        layout = QVBoxLayout()
        layout.addWidget(tab_widget)
        self.setLayout(layout)

    def login_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.login_codice = QLineEdit()
        self.login_codice.setPlaceholderText("Email")
        layout.addWidget(self.login_codice)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.login_password)

        btn_login = QPushButton("Accedi")
        btn_login.clicked.connect(self.login)
        layout.addWidget(btn_login)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        widget.setLayout(layout)
        return widget

    def register_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.reg_codice = QLineEdit()
        self.reg_codice.setPlaceholderText("Email")
        layout.addWidget(self.reg_codice)

        self.reg_nome = QLineEdit()
        self.reg_nome.setPlaceholderText("Nome")
        layout.addWidget(self.reg_nome)

        self.reg_cognome = QLineEdit()
        self.reg_cognome.setPlaceholderText("Cognome")
        layout.addWidget(self.reg_cognome)

        self.reg_cod_fiscale = QLineEdit()
        self.reg_cod_fiscale.setPlaceholderText("Codice Fiscale")
        layout.addWidget(self.reg_cod_fiscale)

        self.reg_ruolo = QLineEdit()
        self.reg_ruolo.setPlaceholderText("Ruolo")
        layout.addWidget(self.reg_ruolo)

        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Password")
        self.reg_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.reg_password)

        btn_register = QPushButton("Registrati")
        btn_register.clicked.connect(self.registra)  # qui chiami solo la logica
        layout.addWidget(btn_register)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        widget.setLayout(layout)
        return widget

    def login(self):
        email = self.login_codice.text().strip()
        password = self.login_password.text().strip()

        try:
            data = login_utente(email, password, api_key)
            if data:
                QMessageBox.information(self, "Login", f"✅ Login riuscito per {email}")
                self.callback_login_success()
                self.close()
            else:
                QMessageBox.warning(self, "Errore", "❌ Credenziali errate.")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il login:\n{e}")

    def registra(self):
        try:
            email = self.reg_codice.text().strip()
            nome = self.reg_nome.text().strip()
            cognome = self.reg_cognome.text().strip()
            password = self.reg_password.text().strip()
            cod_fiscale = self.reg_cod_fiscale.text().strip()
            ruolo = self.reg_ruolo.text().strip().lower()  # standardizza in minuscolo

            # Chiamata a Firebase Auth
            firebase_user = registra_utente(cod_fiscale, email, password, nome, ruolo)
            if not firebase_user:
                QMessageBox.warning(self, "Errore", "❌ Email già registrata.")
                return

            id_documento = cod_fiscale

            # Collezioni standardizzate in minuscolo
            if ruolo == "volontario":
                collezione = "Volontario"
            elif ruolo == "referente":
                collezione = "Referente"
            elif ruolo == "operatore_sanitario":
                collezione = "Operatore_Sanitario"
            else:
                QMessageBox.critical(self, "Errore", f"❌ Ruolo non valido: {ruolo}")
                return

            # Salvataggio nella collezione corretta
            db.collection(collezione).document(id_documento).set({
                "cod_fiscale": cod_fiscale,
                "nome": nome,
                "cognome": cognome,
                "email": email,
                "ruolo": ruolo
            })

            QMessageBox.information(self, "Registrazione", "✅ Account creato con successo.")

            # 🔁 PASSAGGIO A MAIN WINDOW
            self.callback_login_success()  # Chiama la MainWindow
            self.close()  # Chiudi la finestra di login

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Registrazione fallita:\n{e}")
