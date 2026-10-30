from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QSizePolicy, QDialog, QLabel, QDateEdit,
    QGraphicsDropShadowEffect, QFrame, QSpacerItem, QStackedWidget,
    QComboBox, QScrollArea
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
        self.setWindowTitle("Recupero Credenziali — Croce Rossa Italiana")
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

        lbl_titolo = QLabel("<h3 style='margin:0; color: white;'>Recupero Credenziali (Illustrativo)</h3>")
        layout.addWidget(lbl_titolo)

        lbl_desc = QLabel(
            "<b>Funzionalità a scopo puramente illustrativo:</b><br>"
            "In ambiente reale la procedura coinvolge il server di posta aziendale.<br>"
            "Inserisci la tua email o codice fiscale per visualizzare la simulazione del flusso UML."
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
        btn_invia = QPushButton("Simula Invio")
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
            self.lbl_feedback.setText("<span style='color: #ff5252;'>Inserisci la tua email o codice fiscale.</span>")
            self.lbl_feedback.show()
            return

        from GestioneUtenteController import GestioneUtenteController
        ctrl = GestioneUtenteController()
        successo, messaggio = ctrl.recuperaCredenziali(val)

        if successo:
            QMessageBox.information(self, "Simulazione Recupero Credenziali", f"{messaggio}")
            self.accept()
        else:
            self.lbl_feedback.setText(f"<span style='color: #ff5252;'>{messaggio}</span>")
            self.lbl_feedback.show()


# ─────────────────────────────────────────────────────────────
#  Finestra principale di Login
# ─────────────────────────────────────────────────────────────
class LoginWindow(QWidget):
    def __init__(self, sistema: Sistema, callback_login_success):
        super().__init__()
        self.setWindowTitle("Croce Rossa Italiana — Accesso")
        self.setMinimumSize(720, 560)  # dimensione minima garantita
        self.resize(860, 660)          # dimensione iniziale preferita
        self.sistema = sistema
        self.callback_login_success = callback_login_success
        self.controller = GestioneUtenteController()

        self.setStyleSheet("""
            QWidget { background: transparent; color: #ffffff; font-family: "Helvetica Neue", Arial; }
            QLabel  { background: transparent; }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Pannello sinistro ─────────────────────────────
        left = self._build_left_panel()
        left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore[attr-defined]
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
        right_wrapper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore[attr-defined]
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
        cross_label.setText("✚")
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
            ("•", "Gestione turni di servizio"),
            ("•", "Monitoraggio flotta"),
            ("•", "Formazione e certificazioni"),
            ("•", "Reportistica attività"),
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
        h_label = QLabel("Bentornato")
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
        layout.addStretch()

        # Link switch a registrazione
        switch = QPushButton("Non hai un account? Crea nuovo account →")
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
        # Pannello esterno che ospita lo scroll
        outer = QWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Area di scorrimento per evitare sovrapposizioni con molti campi
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore[attr-defined]
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: #1a1a1a; width: 6px; border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #444; border-radius: 3px; min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(48, 36, 48, 28)
        layout.setSpacing(0)

        h_label = QLabel("Crea nuovo account")
        h_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #fff;")
        layout.addWidget(h_label)
        layout.addSpacing(4)
        sub = QLabel("Compila i campi per registrarti (Volontario o Referente)")
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
        self._reg_ruolo.addItem("Ruolo: Volontario Operativo", "volontario")
        self._reg_ruolo.addItem("Ruolo: Referente / Coordinatore", "referente")

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

        btn_reg = PrimaryButton("Crea nuovo account")
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
        layout.addSpacing(8)

        scroll.setWidget(panel)
        outer_layout.addWidget(scroll)
        return outer

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
                "Credenziali non corrette o account non trovato.\n"
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
            QMessageBox.warning(self, "Campi Mancanti", "Compila tutti i campi obbligatori.")
            return

        if ruolo == "referente":
            from security_config import verifica_pin_referente
            pin_val = self._reg_pin.text().strip() if hasattr(self, "_reg_pin") else ""
            if not verifica_pin_referente(pin_val):
                QMessageBox.critical(
                    self,
                    "Accesso Negato — PIN Referente Richiesto",
                    "Codice di Autorizzazione Referente non valido o mancante.\n\n"
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
            # Per il referente non viene mostrato il messaggio modale "Account Creato"
            if ruolo != "referente":
                QMessageBox.information(self, "Benvenuto!", "Account Volontario creato con successo. Benvenuto!")
            self.callback_login_success()
            self.close()
        else:
            QMessageBox.warning(self, "Registrazione Fallita",
                "Impossibile creare l'account.\n"
                "Verifica che il Codice Fiscale (16 caratteri) e il telefono siano corretti.")


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