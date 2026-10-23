# main.py
import sys
from dotenv import load_dotenv

# Carica le variabili d'ambiente da .env (se presente) prima di qualsiasi import applicativo.
# In produzione o CI/CD le variabili possono essere iniettate direttamente dall'ambiente host
# senza dipendere dal file .env.
load_dotenv()

from PyQt5.QtWidgets import QApplication
from Sistema import Sistema
from layout.MainWindow import MainWindow
from layout.LoginWindow import LoginWindow

from session_manager import load_session, clear_session

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.sistema = Sistema()
        self.main_window = None
        self.login_window = None

        # Verifica se esiste una sessione precedentemente salvata su questo dispositivo
        session = load_session()
        if session:
            try:
                cf = session.get("cod_fiscale", "").strip()
                email = session.get("email", "").strip().lower()
                print(f"[Main] Ripristino sessione automatica per {cf or email}...")

                # Carica i dati dal database locale JSON
                self.sistema.carica_dati()

                # Cerca l'utente autenticato per codice fiscale o email
                user = None
                if cf:
                    user = self.sistema.get_volontario(cf)
                if not user and email:
                    user = next((v for v in self.sistema.volontari if getattr(v, "email", "").strip().lower() == email), None)

                if user:
                    self.sistema.logged_user = user
                    print(f"[Main] Accesso automatico riuscito: {user.getNomeCompleto()} ({user.ruolo})")
                    self.apri_main()
                    return
                else:
                    print("[Main/Avviso] Profilo utente non trovato nel database locale. Richiedo nuovo login.")
                    clear_session()
            except Exception as e:
                print(f"[Main/Errore] Ripristino sessione: {e}")
                clear_session()

        # Nessuna sessione valida: mostra la finestra di login
        self.mostra_login()

    def mostra_login(self):
        self.login_window = LoginWindow(self.sistema, self.apri_main)
        self.login_window.show()

    def apri_main(self, login_toast: str = ""):
        if self.login_window:
            self.login_window.close()
            self.login_window = None
        self.main_window = MainWindow(self.sistema, self.esegui_logout, sync_on_start=False)
        self.main_window.show()
        if login_toast and hasattr(self.main_window, "mostra_toast"):
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(250, lambda: self.main_window.mostra_toast(login_toast, tipo="success", durata_ms=3500))

    def esegui_logout(self):
        # Rimuove la sessione memorizzata su questo dispositivo
        clear_session()
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        self.sistema.logged_user = None
        self.mostra_login()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    controller = AppController()
    controller.run()
