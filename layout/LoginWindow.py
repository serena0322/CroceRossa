from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QTabWidget, QMessageBox, QSpacerItem, QSizePolicy
)

# 🧹 Pulizia: Via tutti gli import di Firebase e Auth diretti!
# Importiamo invece il Modello e il Controller secondo il pattern MVC
from Sistema import Sistema
from GestioneUtenteController import GestioneUtenteController
from Utente import Utente

class LoginWindow(QWidget):
    def __init__(self, sistema: Sistema, callback_login_success):
        super().__init__()
        self.setWindowTitle("🔐 Accesso - Croce Rossa")
        self.resize(350, 450) # Leggermente ingrandita per ospitare i nuovi campi
        self.sistema = sistema
        self.callback_login_success = callback_login_success
        
        # Inizializziamo il nostro "Direttore d'orchestra"
        self.controller = GestioneUtenteController()

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

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email")
        layout.addWidget(self.login_email)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.login_password)

        btn_login = QPushButton("Accedi")
        # pyrefly: ignore [missing-attribute]
        btn_login.clicked.connect(self.login)
        layout.addWidget(btn_login)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        widget.setLayout(layout)
        return widget

    def register_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Email")
        layout.addWidget(self.reg_email)

        self.reg_nome = QLineEdit()
        self.reg_nome.setPlaceholderText("Nome")
        layout.addWidget(self.reg_nome)

        self.reg_cognome = QLineEdit()
        self.reg_cognome.setPlaceholderText("Cognome")
        layout.addWidget(self.reg_cognome)

        self.reg_cod_fiscale = QLineEdit()
        self.reg_cod_fiscale.setPlaceholderText("Codice Fiscale")
        layout.addWidget(self.reg_cod_fiscale)
        
        # --- Nuovi campi aggiunti per rispettare il Modello UML ---
        self.reg_data_nascita = QLineEdit()
        self.reg_data_nascita.setPlaceholderText("Data di nascita (GG/MM/AAAA)")
        layout.addWidget(self.reg_data_nascita)
        
        self.reg_telefono = QLineEdit()
        self.reg_telefono.setPlaceholderText("Telefono")
        layout.addWidget(self.reg_telefono)
        # ---------------------------------------------------------

        self.reg_ruolo = QLineEdit()
        self.reg_ruolo.setPlaceholderText("Ruolo (es: volontario)")
        layout.addWidget(self.reg_ruolo)

        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Password")
        self.reg_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.reg_password)

        btn_register = QPushButton("Registrati")
        # pyrefly: ignore [missing-attribute]
        btn_register.clicked.connect(self.registra)
        layout.addWidget(btn_register)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        widget.setLayout(layout)
        return widget

    def login(self):
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()

        # Il controller si occupa di validare e interrogare Firebase
        successo = self.controller.effettuaLogin(email, password)
        
        if successo:
            QMessageBox.information(self, "Login", f"✅ Login riuscito!")
            self.callback_login_success()
            self.close()
        else:
            QMessageBox.warning(self, "Errore", "❌ Credenziali errate o formato non valido.")


    def registra(self):
        # 1. Raccoglie i dati dai campi di testo
        email = self.reg_email.text().strip()
        nome = self.reg_nome.text().strip()
        cognome = self.reg_cognome.text().strip()
        cod_fiscale = self.reg_cod_fiscale.text().strip()
        data_nascita = self.reg_data_nascita.text().strip()
        telefono = self.reg_telefono.text().strip()
        ruolo = self.reg_ruolo.text().strip().lower()
        password = self.reg_password.text().strip()

        # 2. Crea un'Entità pura
        nuovo_utente = Utente(
            cod_fiscale=cod_fiscale,
            nome=nome,
            cognome=cognome,
            email=email,
            data_nascita=data_nascita,
            ruolo=ruolo,
            telefono=telefono
        )

        # 3. Passa l'Entità al Controller per il salvataggio
        successo = self.controller.registraAccount(nuovo_utente, password)

        if successo:
            QMessageBox.information(self, "Registrazione", "✅ Account creato con successo.")
            self.callback_login_success()
            self.close()
        else:
            QMessageBox.warning(self, "Errore", "❌ Registrazione fallita. Controlla i dati inseriti.")