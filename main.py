# main.py
import sys
from PyQt5.QtWidgets import QApplication
from Sistema import Sistema
from layout.MainWindow import MainWindow
from layout.LoginWindow import LoginWindow

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.sistema = Sistema()
        self.main_window = None
        self.login_window = LoginWindow(self.sistema, self.apri_main)
        self.login_window.show()

    def apri_main(self):
        self.main_window = MainWindow(self.sistema, self.esegui_logout)
        self.main_window.show()

    def esegui_logout(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        self.sistema.logged_user = None
        self.login_window = LoginWindow(self.sistema, self.apri_main)
        self.login_window.show()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    controller = AppController()
    controller.run()
