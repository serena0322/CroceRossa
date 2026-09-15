from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QSizePolicy, QDialog, QLabel, QDateEdit,
    QGraphicsDropShadowEffect, QFrame, QSpacerItem, QStackedWidget,
    QComboBox
)
from PyQt5.QtCore import (
    QDate, Qt, QPropertyAnimation, QEasingCurve,
    QPoint, QTimer, QThread, pyqtSignal
)
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter, QLinearGradient, QPen, QBrush

from Sistema import Sistema
from GestioneUtenteController import GestioneUtenteController
from Utente import Utente
from Volontario import Volontario

# ─────────────────────────────────────────────────────────────
#  Google OAuth worker — esegue il flusso nel background thread
# ─────────────────────────────────────────────────────────────
class GoogleOAuthWorker(QThread):
    """Apre il browser per il flusso OAuth2, poi segnala il risultato."""
    auth_success = pyqtSignal(str, str, str)   # email, nome, token
    auth_failed  = pyqtSignal(str)             # messaggio errore

    # Carica le credenziali OAuth dal file di configurazione
    @staticmethod
    def _load_credentials():
        import json, os
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "google_oauth_config.json"
        )
        try:
            with open(config_path, "r") as f:
                cfg = json.load(f)
            client_id     = cfg.get("client_id", "")
            client_secret = cfg.get("client_secret", "")
            if "INSERISCI" in client_id or not client_id:
                return None, None
            return client_id, client_secret
        except Exception:
            return None, None

    def run(self):
        try:
            import webbrowser
            import urllib.parse
            import http.server
            import threading
            import requests

            CLIENT_ID, CLIENT_SECRET = self._load_credentials()
            if not CLIENT_ID:
                self.auth_failed.emit(
                    "Credenziali Google OAuth non configurate.\n\n"
                    "Apri il file 'google_oauth_config.json' nella cartella del progetto\n"
                    "e segui le istruzioni per inserire il tuo Client ID e Client Secret."
                )
                return

            REDIRECT_URI = "http://localhost:9753/oauth/callback"
            SCOPE        = "openid email profile"

            auth_code_holder: dict = {"code": None}
            server_done = threading.Event()

            class CallbackHandler(http.server.BaseHTTPRequestHandler):
                def do_GET(self):
                    parsed = urllib.parse.urlparse(self.path)
                    params = urllib.parse.parse_qs(parsed.query)
                    code   = params.get("code", [None])[0]
                    auth_code_holder["code"] = code
                    # Risposta HTML di chiusura con stile CRI e chiusura automatica
                    html = b"""<!DOCTYPE html><html><head><meta charset='utf-8'>
                    <title>Croce Rossa Italiana - Accesso Google</title>
                    <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                        display: flex; align-items: center; justify-content: center;
                        height: 100vh; margin: 0; background: #121212; color: #ffffff;
                    }
                    .box {
                        text-align: center; background: #1e1e1e; padding: 40px 48px;
                        border-radius: 16px; border: 1px solid #333333;
                        box-shadow: 0 14px 35px rgba(0,0,0,0.5); max-width: 380px;
                    }
                    .check { font-size: 54px; color: #00e676; margin-bottom: 12px; }
                    h2 { margin: 0 0 8px 0; font-size: 21px; font-weight: 700; color: #ffffff; }
                    p { color: #aaaaaa; font-size: 14px; line-height: 1.4; margin: 0; }
                    .badge {
                        display: inline-block; margin-top: 16px; padding: 6px 14px;
                        background: #2b3548; color: #90caf9; border-radius: 16px;
                        font-size: 12px; font-weight: 600;
                    }
                    </style></head>
                    <body>
                    <div class='box'>
                        <div class='check'>&#10003;</div>
                        <h2>Accesso Google Riuscito!</h2>
                        <p>Autenticazione completata con successo. Torna all'applicazione Croce Rossa.</p>
                        <div class='badge'>Accesso in corso...</div>
                        <script>setTimeout(function(){ window.close(); }, 1200);</script>
                    </div>
                    </body></html>"""
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(html)
                    server_done.set()
                def log_message(self, format: str, *args):  # type: ignore[override]
                    pass  # Silenzia i log HTTP

            httpd = http.server.HTTPServer(("localhost", 9753), CallbackHandler)
            server_thread = threading.Thread(target=httpd.handle_request, daemon=True)
            server_thread.start()

            # Costruisci l'URL di autorizzazione Google
            auth_params = {
                "client_id":     CLIENT_ID,
                "redirect_uri":  REDIRECT_URI,
                "response_type": "code",
                "scope":         SCOPE,
                "access_type":   "offline",
                "prompt":        "select_account",
            }
            auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(auth_params)
            webbrowser.open(auth_url)

            # Attendi il codice dal browser (timeout 120s)
            server_done.wait(timeout=120)
            httpd.server_close()

            code = auth_code_holder["code"]
            if not code:
                self.auth_failed.emit("Autenticazione Google annullata o scaduta.")
                return

            # Scambia il codice con il token
            token_resp = requests.post("https://oauth2.googleapis.com/token", data={
                "code":          code,
                "client_id":     CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri":  REDIRECT_URI,
                "grant_type":    "authorization_code",
            }, timeout=15)

            if token_resp.status_code != 200:
                self.auth_failed.emit(f"Errore token Google: {token_resp.text[:200]}")
                return

            token_data  = token_resp.json()
            id_token    = token_data.get("id_token", "")
            access_token = token_data.get("access_token", "")

            # Recupera info profilo
            profile_resp = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            profile = profile_resp.json()
            email  = profile.get("email",  "")
            nome   = profile.get("given_name", profile.get("name", "Utente"))

            self.auth_success.emit(email, nome, id_token)

        except Exception as e:
            self.auth_failed.emit(f"Errore Google OAuth: {e}")


# ─────────────────────────────────────────────────────────────
#  Widget campo di input moderno
# ─────────────────────────────────────────────────────────────
class ModernInput(QLineEdit):
    def __init__(self, placeholder="", is_password=False, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        if is_password:
            self.setEchoMode(QLineEdit.Password)
        self.setFixedHeight(48)
        self.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.08);
                border: 1.5px solid rgba(255,255,255,0.15);
                border-radius: 10px;
                padding: 0 16px;
                color: #ffffff;
                font-size: 14px;
                font-family: "Helvetica Neue", Arial;
            }
            QLineEdit:focus {
                border: 1.5px solid #e53935;
                background-color: rgba(229,57,53,0.08);
            }
            QLineEdit::placeholder {
                color: rgba(255,255,255,0.4);
            }
        """)


# ─────────────────────────────────────────────────────────────
#  Widget menu a tendina moderno per selezione ruolo
# ─────────────────────────────────────────────────────────────
class ModernComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setStyleSheet("""
            QComboBox {
                background-color: rgba(255,255,255,0.08);
                border: 1.5px solid rgba(255,255,255,0.15);
                border-radius: 10px;
                padding: 0 16px;
                color: #ffffff;
                font-size: 14px;
                font-family: "Helvetica Neue", Arial;
            }
            QComboBox:focus {
                border: 1.5px solid #e53935;
                background-color: rgba(229,57,53,0.08);
            }
            QComboBox::drop-down {
                border: none;
                width: 32px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid rgba(255,255,255,0.7);
                margin-right: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                color: #ffffff;
                selection-background-color: #e53935;
                selection-color: #ffffff;
                border: 1px solid #333333;
                border-radius: 8px;
                outline: none;
                padding: 4px;
            }
        """)


# ─────────────────────────────────────────────────────────────
#  Widget bottone primario moderno
# ─────────────────────────────────────────────────────────────
class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e53935, stop:1 #c62828);
                color: white;
                font-size: 15px;
                font-weight: 700;
                border-radius: 10px;
                border: none;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ef5350, stop:1 #e53935);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c62828, stop:1 #b71c1c);
            }
        """)


# ─────────────────────────────────────────────────────────────
#  Widget bottone secondario (outline)
# ─────────────────────────────────────────────────────────────
class SecondaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255,255,255,0.75);
                font-size: 13px;
                font-weight: 500;
                border: 1.5px solid rgba(255,255,255,0.2);
                border-radius: 10px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.06);
                color: #ffffff;
                border-color: rgba(255,255,255,0.4);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.10);
            }
        """)


class RecuperoCredenzialiDialog(QDialog):
    """Finestra modale per la richiesta di recupero credenziali / reset password."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Recupero Credenziali — Croce Rossa Italiana")
        self.setFixedWidth(460)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
                font-family: "Helvetica Neue", Arial;
            }
            QLineEdit {
                background-color: #262626;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #c62828;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        lbl_titolo = QLabel("<h3 style='margin:0; color: white;'>🔐 Recupera Password / Account</h3>")
        layout.addWidget(lbl_titolo)

        lbl_desc = QLabel(
            "Inserisci l'indirizzo <b>Email</b> o il <b>Codice Fiscale</b> associato al tuo profilo CRI.<br>"
            "Riceverai un'email con le istruzioni e il collegamento per reimpostare la tua password."
        )
        lbl_desc.setStyleSheet("color: #b0bec5; font-size: 13px;")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        self.txt_identificativo = QLineEdit()
        self.txt_identificativo.setPlaceholderText("Es. mario.rossi@cri.it oppure RSSMRA85M01H501Z")
        layout.addWidget(self.txt_identificativo)

        self.lbl_feedback = QLabel()
        self.lbl_feedback.setWordWrap(True)
        self.lbl_feedback.hide()
        layout.addWidget(self.lbl_feedback)

        btn_box = QHBoxLayout()
        btn_invia = QPushButton("Invia Link di Ripristino")
        btn_invia.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                color: white;
                font-weight: bold;
                padding: 10px 18px;
                border-radius: 6px;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        btn_invia.clicked.connect(self._invia_recupero)  # pyrefly: ignore [missing-attribute]
        btn_box.addWidget(btn_invia)

        btn_annulla = QPushButton("Annulla")
        btn_annulla.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #ccc;
                padding: 10px 16px;
                border-radius: 6px;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background-color: #444;
                color: white;
            }
        """)
        btn_annulla.clicked.connect(self.reject)  # pyrefly: ignore [missing-attribute]
        btn_box.addWidget(btn_annulla)

        layout.addLayout(btn_box)

    def _invia_recupero(self):
        val = self.txt_identificativo.text().strip()
        if not val:
            self.lbl_feedback.setText("<span style='color: #ff5252;'>⚠️ Inserisci la tua email o codice fiscale.</span>")
            self.lbl_feedback.show()
            return

        from GestioneUtenteController import GestioneUtenteController
        ctrl = GestioneUtenteController()
        successo, messaggio = ctrl.recuperaCredenziali(val)

        if successo:
            QMessageBox.information(self, "Email di Recupero Inviata", f"✅ {messaggio}")
            self.accept()
        else:
            self.lbl_feedback.setText(f"<span style='color: #ff5252;'>❌ {messaggio}</span>")
            self.lbl_feedback.show()


# ─────────────────────────────────────────────────────────────
#  Dialog di selezione ruolo al primo accesso Google
# ─────────────────────────────────────────────────────────────
class SelezioneRuoloGoogleDialog(QDialog):
    def __init__(self, nome_utente: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Primo Accesso Google — Croce Rossa Italiana")
        self.setFixedSize(500, 390)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # type: ignore[attr-defined]
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: "Helvetica Neue", Arial;
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox, QLineEdit {
                background-color: #2a2a2a;
                border: 1.5px solid #444444;
                border-radius: 8px;
                padding: 10px 14px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
            }
            QComboBox:focus, QLineEdit:focus {
                border-color: #e53935;
            }
            QComboBox QAbstractItemView {
                background-color: #222222;
                color: #ffffff;
                selection-background-color: #e53935;
                selection-color: #ffffff;
                border: 1px solid #444;
                outline: none;
                padding: 4px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e53935, stop:1 #c62828);
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef5350, stop:1 #d32f2f);
            }
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 26, 32, 26)
        lay.setSpacing(12)

        t_lbl = QLabel(f"👋 Ciao {nome_utente}!")
        t_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        lay.addWidget(t_lbl)

        sub_lbl = QLabel(
            "Questo account Google non è ancora registrato nel sistema CRI.\n"
            "Dichiara con quale ruolo operativo desideri registrarti:"
        )
        sub_lbl.setStyleSheet("font-size: 13px; color: #b0bec5; line-height: 1.4;")
        sub_lbl.setWordWrap(True)
        lay.addWidget(sub_lbl)

        self.combo_ruolo = QComboBox()
        self.combo_ruolo.addItem("🚑 Volontario Operativo (Iscrizione ai Turni, Checklist)", "volontario")
        self.combo_ruolo.addItem("📋 Referente / Coordinatore (Gestione Turni, Mezzi, Corsi e Rubrica)", "referente")
        self.combo_ruolo.addItem("🩺 Operatore Sanitario (Personale Medico / Infermieristico)", "operatore_sanitario")
        self.combo_ruolo.setFixedHeight(46)
        lay.addWidget(self.combo_ruolo)

        self.lbl_pin = QLabel("🔒 <b>PIN di Autorizzazione Comitato (Richiesto per Referente):</b>")
        self.lbl_pin.setStyleSheet("font-size: 12px; color: #ffb74d;")
        self.lbl_pin.hide()
        lay.addWidget(self.lbl_pin)

        self.txt_pin = QLineEdit()
        self.txt_pin.setPlaceholderText("Inserisci PIN di sicurezza CRI...")
        self.txt_pin.setEchoMode(QLineEdit.Password)
        self.txt_pin.setFixedHeight(44)
        self.txt_pin.hide()
        lay.addWidget(self.txt_pin)

        def _on_role_change():
            is_ref = self.combo_ruolo.currentData() == "referente"
            self.lbl_pin.setVisible(is_ref)
            self.txt_pin.setVisible(is_ref)

        self.combo_ruolo.currentIndexChanged.connect(lambda _: _on_role_change())  # pyrefly: ignore [missing-attribute]

        lay.addSpacing(6)

        btn_conferma = QPushButton("Conferma e Accedi")
        btn_conferma.setFixedHeight(46)
        btn_conferma.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]
        btn_conferma.clicked.connect(self._on_conferma_clicked)  # pyrefly: ignore [missing-attribute]
        lay.addWidget(btn_conferma)

    def _on_conferma_clicked(self):
        ruolo = self.get_ruolo_selezionato()
        if ruolo == "referente":
            from security_config import verifica_pin_referente
            pin = self.txt_pin.text().strip()
            if not verifica_pin_referente(pin):
                QMessageBox.critical(
                    self,
                    "PIN Non Valido",
                    "❌ Codice di Autorizzazione Referente errato o non inserito.\n\n"
                    "Per registrarsi come Referente è necessario il PIN fornito dal Comitato CRI.\n"
                    "Se non possiedi il codice, seleziona 'Volontario Operativo'."
                )
                return
        self.accept()

    def get_ruolo_selezionato(self) -> str:
        return self.combo_ruolo.currentData() or "volontario"


# ─────────────────────────────────────────────────────────────
#  Finestra principale di Login
# ─────────────────────────────────────────────────────────────
class LoginWindow(QWidget):
    def __init__(self, sistema: Sistema, callback_login_success):
        super().__init__()
        self.setWindowTitle("Croce Rossa Italiana — Accesso")
        self.setFixedSize(860, 580)
        self.sistema = sistema
        self.callback_login_success = callback_login_success
        self.controller = GestioneUtenteController()
        self._google_worker = None

        self.setStyleSheet("""
            QWidget { background: transparent; color: #ffffff; font-family: "Helvetica Neue", Arial; }
            QLabel  { background: transparent; }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Pannello sinistro ─────────────────────────────
        left = self._build_left_panel()
        root.addWidget(left, stretch=5)

        # ── Pannello destro (form) ────────────────────────
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_login_panel())     # 0 = login
        self._stack.addWidget(self._build_register_panel())  # 1 = registrazione

        right_wrapper = QWidget()
        right_wrapper.setObjectName("rightPanel")
        right_wrapper.setStyleSheet("""
            QWidget#rightPanel { background: #0f0f0f; }
        """)
        rw_layout = QVBoxLayout(right_wrapper)
        rw_layout.setContentsMargins(0, 0, 0, 0)
        rw_layout.addWidget(self._stack)
        root.addWidget(right_wrapper, stretch=4)

        # Animazione fade-in all'apertura
        self.setWindowOpacity(0.0)
        self._fade_in()

    # ── PANNELLO SINISTRO ─────────────────────────────────────
    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("leftPanel")
        panel.setStyleSheet("""
            QWidget#leftPanel {
                background: qlineargradient(x1:0, y1:0, x2:0.6, y2:1,
                    stop:0 #8b0000, stop:0.45 #c62828, stop:1 #1a0000);
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(48, 56, 40, 48)
        layout.setSpacing(0)

        # Logo / Simbolo Croce Rossa
        cross_label = QLabel()
        cross_label.setFixedSize(80, 80)
        cross_label.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
        cross_label.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.12);
                border: 2px solid rgba(255,255,255,0.25);
                border-radius: 20px;
                font-size: 44px;
            }
        """)
        cross_label.setText("🏥")
        layout.addWidget(cross_label, alignment=Qt.AlignLeft)  # type: ignore[attr-defined]

        layout.addSpacing(36)

        # Titolo principale
        title = QLabel("Croce Rossa\nItaliana")
        title.setStyleSheet("""
            font-size: 34px;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.2;
            letter-spacing: -0.5px;
        """)
        title.setWordWrap(True)
        layout.addWidget(title)

        layout.addSpacing(12)

        # Sottotitolo
        sub = QLabel("Portale Volontari\ne Referenti")
        sub.setStyleSheet("font-size: 16px; color: rgba(255,255,255,0.7); font-weight: 400;")
        sub.setWordWrap(True)
        layout.addWidget(sub)

        layout.addStretch()

        # Features list
        for icon, text in [
            ("📅", "Gestione turni di servizio"),
            ("🚐", "Monitoraggio flotta"),
            ("🎓", "Formazione e certificazioni"),
            ("📊", "Reportistica attività"),
        ]:
            row = QHBoxLayout()
            row.setSpacing(10)
            ico = QLabel(icon)
            ico.setStyleSheet("font-size: 18px;")
            ico.setFixedWidth(28)
            txt = QLabel(text)
            txt.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.75); font-weight: 400;")
            row.addWidget(ico)
            row.addWidget(txt)
            row.addStretch()
            layout.addLayout(row)
            layout.addSpacing(8)

        layout.addStretch()

        # Footer versione
        ver = QLabel("v2.0 — 2026")
        ver.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.3);")
        layout.addWidget(ver, alignment=Qt.AlignLeft)  # type: ignore[attr-defined]

        return panel

    # ── PANNELLO LOGIN ────────────────────────────────────────
    def _build_login_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(48, 52, 48, 40)
        layout.setSpacing(0)

        # Intestazione
        h_label = QLabel("Bentornato 👋")
        h_label.setStyleSheet("font-size: 26px; font-weight: 700; color: #fff;")
        layout.addWidget(h_label)
        layout.addSpacing(4)

        sub = QLabel("Accedi al tuo account per continuare")
        sub.setStyleSheet("font-size: 13px; color: rgba(255,255,255,0.45);")
        layout.addWidget(sub)
        layout.addSpacing(32)

        # Campi
        self._login_email = ModernInput("Email", parent=self)
        self._login_pwd   = ModernInput("Password", is_password=True, parent=self)
        layout.addWidget(self._login_email)
        layout.addSpacing(12)
        layout.addWidget(self._login_pwd)
        layout.addSpacing(6)

        # Link Password Dimenticata / Recupero Credenziali
        box_forgot = QHBoxLayout()
        box_forgot.addStretch()
        btn_forgot = QPushButton("Hai dimenticato la password?")
        btn_forgot.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]
        btn_forgot.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #90caf9;
                font-size: 12px;
                font-weight: 500;
                padding: 0;
            }
            QPushButton:hover {
                color: #ffffff;
                text-decoration: underline;
            }
        """)
        btn_forgot.clicked.connect(self._apri_recupero_credenziali)  # pyrefly: ignore [missing-attribute]
        box_forgot.addWidget(btn_forgot)
        layout.addLayout(box_forgot)
        layout.addSpacing(14)

        # Bottone accedi
        btn_login = PrimaryButton("Accedi")
        btn_login.clicked.connect(self._do_login)  # pyrefly: ignore [missing-attribute]
        layout.addWidget(btn_login)
        layout.addSpacing(14)

        # Divisore ─── oppure ───
        div_layout = QHBoxLayout()
        for _ in range(2):
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet("color: rgba(255,255,255,0.12);")
            div_layout.addWidget(line)
            if _ == 0:
                lbl = QLabel("  oppure  ")
                lbl.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.3);")
                lbl.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
                div_layout.addWidget(lbl)
        layout.addLayout(div_layout)
        layout.addSpacing(14)

        # Bottone Google
        btn_google = QPushButton()
        btn_google.setFixedHeight(48)
        btn_google.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]
        btn_google.setText("  Continua con Google")
        btn_google.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.06);
                border: 1.5px solid rgba(255,255,255,0.18);
                border-radius: 10px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                text-align: center;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.11);
                border-color: rgba(255,255,255,0.35);
            }
            QPushButton:pressed { background: rgba(255,255,255,0.15); }
        """)
        # SVG Google colorato come testo emoji (testo Unicode)
        btn_google.setText("  🌐  Continua con Google")
        btn_google.clicked.connect(self._do_google_login)  # pyrefly: ignore [missing-attribute]
        layout.addWidget(btn_google)

        layout.addStretch()

        # Link switch a registrazione
        switch = QPushButton("Non hai un account? Registrati →")
        switch.setFlat(True)
        switch.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]
        switch.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                color: #e57373; font-size: 13px; font-weight: 500;
                text-align: center;
            }
            QPushButton:hover { color: #ef9a9a; }
        """)
        switch.clicked.connect(lambda: self._stack.setCurrentIndex(1))  # pyrefly: ignore [missing-attribute]
        layout.addWidget(switch, alignment=Qt.AlignCenter)  # type: ignore[attr-defined]

        return panel

    # ── PANNELLO REGISTRAZIONE ────────────────────────────────
    def _build_register_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(48, 36, 48, 28)
        layout.setSpacing(0)

        h_label = QLabel("Crea account")
        h_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #fff;")
        layout.addWidget(h_label)
        layout.addSpacing(4)
        sub = QLabel("Compila i campi per registrarti (Volontario, Referente o Operatore)")
        sub.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.4);")
        layout.addWidget(sub)
        layout.addSpacing(20)

        self._reg_email  = ModernInput("Email", parent=self)
        self._reg_nome   = ModernInput("Nome", parent=self)
        self._reg_cognome= ModernInput("Cognome", parent=self)
        self._reg_cf     = ModernInput("Codice Fiscale (16 caratteri)", parent=self)
        self._reg_dob    = ModernInput("Data di nascita (GG/MM/AAAA)", parent=self)
        self._reg_tel    = ModernInput("Telefono", parent=self)
        
        self._reg_ruolo  = ModernComboBox(parent=self)
        self._reg_ruolo.addItem("🚑 Ruolo: Volontario Operativo", "volontario")
        self._reg_ruolo.addItem("📋 Ruolo: Referente / Coordinatore", "referente")
        self._reg_ruolo.addItem("🩺 Ruolo: Operatore Sanitario", "operatore_sanitario")

        self._reg_pin = ModernInput("PIN Autorizzazione Referente (CRI)", is_password=True, parent=self)
        self._reg_pin.hide()

        def _on_reg_ruolo_changed():
            is_ref = (self._reg_ruolo.currentData() == "referente")
            self._reg_pin.setVisible(is_ref)

        self._reg_ruolo.currentIndexChanged.connect(lambda _: _on_reg_ruolo_changed())  # pyrefly: ignore [missing-attribute]

        self._reg_pwd    = ModernInput("Password (min. 6 caratteri)", is_password=True, parent=self)

        fields = [self._reg_email, self._reg_nome, self._reg_cognome,
                  self._reg_cf, self._reg_dob, self._reg_tel, self._reg_ruolo, self._reg_pin, self._reg_pwd]

        for i, f in enumerate(fields):
            layout.addWidget(f)
            if i < len(fields) - 1:
                layout.addSpacing(8)

        layout.addSpacing(16)

        btn_reg = PrimaryButton("Crea Account")
        btn_reg.clicked.connect(self._do_register)  # pyrefly: ignore [missing-attribute]
        layout.addWidget(btn_reg)
        layout.addSpacing(10)

        switch = QPushButton("← Hai già un account? Accedi")
        switch.setFlat(True)
        switch.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]
        switch.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                color: #e57373; font-size: 13px; font-weight: 500;
                text-align: center;
            }
            QPushButton:hover { color: #ef9a9a; }
        """)
        switch.clicked.connect(lambda: self._stack.setCurrentIndex(0))  # pyrefly: ignore [missing-attribute]
        layout.addWidget(switch, alignment=Qt.AlignCenter)  # type: ignore[attr-defined]

        return panel

    # ── ANIMAZIONE FADE-IN ────────────────────────────────────
    def _fade_in(self):
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(400)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

    def _apri_recupero_credenziali(self):
        dlg = RecuperoCredenzialiDialog(self)
        dlg.exec_()

    # ── LOGIN EMAIL/PASSWORD ──────────────────────────────────
    def _do_login(self):
        email = self._login_email.text().strip()
        pwd   = self._login_pwd.text().strip()
        if not email or not pwd:
            self._shake(self._login_email)
            return
        if self.controller.effettuaLogin(email, pwd, self.sistema):
            from session_manager import save_session
            save_session(self.sistema.logged_user)
            self.callback_login_success()
            self.close()
        else:
            QMessageBox.warning(self, "Accesso Negato",
                "❌ Credenziali non corrette o account non trovato.\n"
                "Verifica email e password e riprova.")
            self._shake(self._login_email)

    # ── REGISTRAZIONE ─────────────────────────────────────────
    def _do_register(self):
        email   = self._reg_email.text().strip()
        nome    = self._reg_nome.text().strip()
        cognome = self._reg_cognome.text().strip()
        cf      = self._reg_cf.text().strip()
        dob     = self._reg_dob.text().strip()
        tel     = self._reg_tel.text().strip()
        if hasattr(self._reg_ruolo, "currentData"):
            ruolo = str(self._reg_ruolo.currentData() or "volontario").lower()
        else:
            ruolo = self._reg_ruolo.text().strip().lower() or "volontario"
        pwd     = self._reg_pwd.text().strip()

        if not all([email, nome, cognome, cf, dob, tel, pwd]):
            QMessageBox.warning(self, "Campi Mancanti", "⚠️ Compila tutti i campi obbligatori.")
            return

        if ruolo == "referente":
            from security_config import verifica_pin_referente
            pin_val = self._reg_pin.text().strip() if hasattr(self, "_reg_pin") else ""
            if not verifica_pin_referente(pin_val):
                QMessageBox.critical(
                    self,
                    "Accesso Negato — PIN Referente Richiesto",
                    "❌ Codice di Autorizzazione Referente non valido o mancante.\n\n"
                    "Per registrarsi come Referente è obbligatorio inserire il PIN di sicurezza CRI.\n"
                    "Se non possiedi il codice, seleziona 'Volontario Operativo'."
                )
                if hasattr(self, "_reg_pin"):
                    self._shake(self._reg_pin)
                return

        from UtenteFactory import costruisci_utente
        nuovo = costruisci_utente({
            "cod_fiscale": cf,
            "nome": nome,
            "cognome": cognome,
            "email": email,
            "nascita": dob,
            "telefono": tel,
            "ruolo": ruolo
        })
        if self.controller.registraAccount(nuovo, pwd):
            if nuovo not in self.sistema.volontari:
                self.sistema.aggiungi_volontario(nuovo)
            self.sistema.logged_user = nuovo
            from session_manager import save_session
            save_session(nuovo)
            titolo_ruolo = "Referente / Coordinatore" if ruolo == "referente" else ("Operatore Sanitario" if ruolo == "operatore_sanitario" else "Volontario")
            QMessageBox.information(self, "Benvenuto!", f"✅ Account ({titolo_ruolo}) creato con successo. Benvenuto!")
            self.callback_login_success()
            self.close()
        else:
            QMessageBox.warning(self, "Registrazione Fallita",
                "❌ Impossibile creare l'account.\n"
                "Verifica che il Codice Fiscale (16 caratteri) e il telefono siano corretti.")

    # ── GOOGLE OAUTH REALE ────────────────────────────────────
    def _do_google_login(self):
        """Avvia il flusso OAuth2 Google nel browser di sistema."""
        if self._google_worker and self._google_worker.isRunning():
            return

        # Stato di caricamento sul bottone
        from PyQt5.QtWidgets import QPushButton as _QPB
        sender = self.sender()
        btn = sender if isinstance(sender, _QPB) else None
        if btn:
            btn.setText("⏳  In attesa del browser...")  # type: ignore[attr-defined]
            btn.setEnabled(False)  # type: ignore[attr-defined]
            self._google_btn_ref = btn

        self.mostra_toast("🌐 Apertura browser per accesso Google...", tipo="info", durata_ms=3000)

        self._google_worker = GoogleOAuthWorker()
        self._google_worker.auth_success.connect(self._on_google_auth_success)  # pyrefly: ignore [missing-attribute]
        self._google_worker.auth_failed.connect(self._on_google_auth_failed)  # pyrefly: ignore [missing-attribute]
        self._google_worker.finished.connect(self._on_google_worker_done)  # pyrefly: ignore [missing-attribute]
        self._google_worker.start()

    def _on_google_auth_success(self, email: str, nome: str, id_token: str):
        """Chiamato dal worker thread dopo autenticazione Google riuscita."""
        self.sistema.sincronizza_con_firebase()
        email_clean = email.strip().lower()
        esistente = next(
            (v for v in self.sistema.volontari if str(getattr(v, "email", "")).strip().lower() == email_clean),
            None
        )

        # Se non trovato per email, controlla se c'è un utente associato alla sessione su questo dispositivo
        if not esistente:
            from session_manager import load_session
            s = load_session()
            if s and s.get("cod_fiscale"):
                cf_sess = str(s.get("cod_fiscale")).strip().upper()
                candidato = self.sistema.get_volontario(cf_sess)
                if candidato:
                    esistente = candidato
                    esistente.email = email
                    try:
                        esistente.aggiorna_firestore()
                    except Exception:
                        pass

        if esistente:
            self.sistema.logged_user = esistente
            from session_manager import save_session
            save_session(esistente)
            nome_disp = esistente.nome or nome or "Volontario"
            self.close()
            self.callback_login_success(f"🌐 Accesso eseguito con Google! Bentornato/a, {nome_disp}.")
        else:
            # Primo accesso con questo account Google: chiedi esplicitamente con quale ruolo registrarsi!
            nome_parts = (nome or "").strip().split(maxsplit=1)
            nome_val = nome_parts[0] if nome_parts else "Volontario"
            cognome_val = nome_parts[1] if len(nome_parts) > 1 else ""

            dlg_ruolo = SelezioneRuoloGoogleDialog(nome_val, self)
            dlg_ruolo.exec_()
            ruolo_scelto = dlg_ruolo.get_ruolo_selezionato()

            import hashlib
            email_hash = hashlib.sha256(email_clean.encode("utf-8")).hexdigest().upper()
            auto_cf = f"GGL{email_hash[:13]}"  # Esattamente 16 caratteri alfanumerici

            from UtenteFactory import costruisci_utente
            nuovo = costruisci_utente({
                "cod_fiscale": auto_cf,
                "nome": nome_val,
                "cognome": cognome_val,
                "email": email,
                "nascita": "01/01/1995",
                "telefono": "",
                "ruolo": ruolo_scelto
            })
            
            # Registra su database e memoria di sistema
            try:
                self.controller.registraAccount(nuovo, f"Google_{auto_cf}")
            except Exception as e:
                print(f"⚠️ Errore registraAccount Google: {e}")
                
            if nuovo not in self.sistema.volontari:
                self.sistema.aggiungi_volontario(nuovo)
                
            self.sistema.logged_user = nuovo
            from session_manager import save_session
            save_session(nuovo)
            self.close()
            titolo_ruolo = "Referente / Coordinatore" if ruolo_scelto == "referente" else ("Operatore Sanitario" if ruolo_scelto == "operatore_sanitario" else "Volontario")
            self.callback_login_success(f"🎉 Accesso eseguito con Google ({titolo_ruolo})! Benvenuto/a, {nome_val}.")

    def _on_google_auth_failed(self, error_msg: str):
        if "annullata" in error_msg.lower() or "scaduta" in error_msg.lower():
            self.mostra_toast("⚠️ Accesso Google annullato.", tipo="warning")
        else:
            self.mostra_toast(f"❌ {error_msg}", tipo="error", durata_ms=4500)

    def _on_google_worker_done(self):
        btn = getattr(self, "_google_btn_ref", None)
        if btn:
            btn.setText("  🌐  Continua con Google")  # type: ignore[attr-defined]
            btn.setEnabled(True)  # type: ignore[attr-defined]

    # ── TOAST NOTIFICATION ────────────────────────────────────
    def mostra_toast(self, messaggio: str, tipo: str = "success", durata_ms: int = 3000):
        if not hasattr(self, "_toast_frame"):
            self._toast_timer = QTimer(self)
            self._toast_timer.setSingleShot(True)
            self._toast_timer.timeout.connect(self._nascondi_toast)

            self._toast_frame = QFrame(self)
            self._toast_layout = QHBoxLayout(self._toast_frame)
            self._toast_layout.setContentsMargins(14, 8, 14, 8)
            self._toast_label = QLabel(self._toast_frame)
            self._toast_layout.addWidget(self._toast_label)
            self._toast_frame.hide()

        color_bg = "#2e7d32" if tipo == "success" else ("#c62828" if tipo == "error" else ("#ef6c00" if tipo == "warning" else "#1565c0"))
        self._toast_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color_bg};
                color: white;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.25);
            }}
            QLabel {{
                color: white;
                font-weight: bold;
                font-size: 13px;
                background: transparent;
            }}
        """)
        self._toast_label.setText(messaggio)
        self._toast_frame.adjustSize()
        w = self._toast_frame.width()
        h = self._toast_frame.height()
        self._toast_frame.move((self.width() - w) // 2, self.height() - h - 25)
        self._toast_frame.show()
        self._toast_frame.raise_()
        self._toast_timer.start(durata_ms)

    def _nascondi_toast(self):
        if hasattr(self, "_toast_frame"):
            self._toast_frame.hide()

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if hasattr(self, "_toast_frame") and self._toast_frame.isVisible():
            w = self._toast_frame.width()
            h = self._toast_frame.height()
            self._toast_frame.move((self.width() - w) // 2, self.height() - h - 25)

    # ── SHAKE ANIMATION (errore) ──────────────────────────────
    def _shake(self, widget: QWidget):
        orig = widget.pos()
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(300)
        anim.setKeyValueAt(0.0,  orig)
        anim.setKeyValueAt(0.15, orig + QPoint(-8, 0))
        anim.setKeyValueAt(0.30, orig + QPoint( 8, 0))
        anim.setKeyValueAt(0.45, orig + QPoint(-6, 0))
        anim.setKeyValueAt(0.60, orig + QPoint( 6, 0))
        anim.setKeyValueAt(0.75, orig + QPoint(-3, 0))
        anim.setKeyValueAt(1.0,  orig)
        anim.start()
        self._shake_anim = anim  # keep reference