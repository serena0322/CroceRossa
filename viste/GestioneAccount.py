from __future__ import annotations
from typing import List, Callable, Optional, TYPE_CHECKING
from PyQt5.QtWidgets import (
    QWidget, QListView, QComboBox, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QLineEdit
)
from PyQt5.QtCore import QStringListModel

if TYPE_CHECKING:
    from Utente import Utente
    from Volontario import Volontario
    from Referente import Referente


class VistaRecuperaCredenziali(QWidget):
    """
    Vista UML: VistaRecuperaCredenziali (in GestioneAccount)
    Attributi UML:
        email: QLineEdit
    Metodi UML:
        __init__()
        invia_click(): void
    """
    def __init__(self):
        super().__init__()
        self.email = QLineEdit(self)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Recupero Password:"))
        layout.addWidget(QLabel("Inserisci l'indirizzo email:"))
        layout.addWidget(self.email)
        btn_invia = QPushButton("Invia Nuova Password")
        btn_invia.clicked.connect(self.invia_click)
        layout.addWidget(btn_invia)

    def invia_click(self) -> None:
        """Invia la nuova password generata tramite email (UML act Login / RecuperaCredenziali)."""
        from GestioneUtenteController import GestioneUtenteController
        ctrl = GestioneUtenteController()
        em = self.email.text().strip()
        ctrl.recuperaCredenziali(em)


class VistaRegistrazioneVolontario(QWidget):
    """
    Vista UML: VistaRegistrazioneVolontario (in GestioneAccount)
    Attributi UML:
        qlines: QVBoxLayout (dict dei campi QLineEdit)
        v_layout: Integer (QVBoxLayout)
    Metodi UML:
        __init__()
        add_info_text(str, str): void
        registra_click(): void
    """
    def __init__(self):
        super().__init__()
        self.qlines: dict[str, QLineEdit] = {}
        self.v_layout = QVBoxLayout(self)
        self._init_ui()

    def _init_ui(self):
        self.v_layout.addWidget(QLabel("Registrazione Nuovo Volontario"))
        self.add_info_text("cod_fiscale", "Codice Fiscale")
        self.add_info_text("nome", "Nome")
        self.add_info_text("cognome", "Cognome")
        self.add_info_text("email", "Email")
        self.add_info_text("telefono", "Telefono")
        self.add_info_text("password", "Password")
        self.add_info_text("comitato", "Comitato CRI")

        btn_reg = QPushButton("Registra Volontario")
        btn_reg.clicked.connect(self.registra_click)
        self.v_layout.addWidget(btn_reg)

    def add_info_text(self, chiave: str, etichetta: str) -> None:
        lbl = QLabel(f"{etichetta}:")
        txt = QLineEdit(self)
        if "password" in chiave.lower():
            txt.setEchoMode(QLineEdit.Password)
        self.qlines[chiave] = txt
        self.v_layout.addWidget(lbl)
        self.v_layout.addWidget(txt)

    def registra_click(self) -> None:
        """Esegue la registrazione del volontario (UML CreaAccountVolontario)."""
        from Volontario import Volontario
        from GestioneUtenteController import GestioneUtenteController
        v = Volontario.create(
            codiceFiscale=self.qlines.get("cod_fiscale", QLineEdit()).text().strip(),
            nome=self.qlines.get("nome", QLineEdit()).text().strip(),
            cognome=self.qlines.get("cognome", QLineEdit()).text().strip(),
            email=self.qlines.get("email", QLineEdit()).text().strip(),
            telefono=self.qlines.get("telefono", QLineEdit()).text().strip(),
            comitato=self.qlines.get("comitato", QLineEdit()).text().strip()
        )
        pwd = self.qlines.get("password", QLineEdit()).text().strip()
        ctrl = GestioneUtenteController()
        ctrl.creaAccountVolontario(v, pwd)


class VistaRegistrazioneReferente(QWidget):
    """
    Vista UML: VistaRegistrazioneReferente (in GestioneAccount)
    Attributi UML:
        qlines: QVBoxLayout (dict dei campi QLineEdit)
        utente: Utente
        v_layout: Integer (QVBoxLayout)
    Metodi UML:
        __init__()
        add_info_text(str, str): void
        registra_click(): void
    """
    def __init__(self):
        super().__init__()
        self.utente = None
        self.qlines: dict[str, QLineEdit] = {}
        self.v_layout = QVBoxLayout(self)
        self._init_ui()

    def _init_ui(self):
        self.v_layout.addWidget(QLabel("Registrazione Nuovo Referente"))
        self.add_info_text("cod_fiscale", "Codice Fiscale")
        self.add_info_text("nome", "Nome")
        self.add_info_text("cognome", "Cognome")
        self.add_info_text("email", "Email")
        self.add_info_text("telefono", "Telefono")
        self.add_info_text("password", "Password")
        self.add_info_text("settoreGestito", "Settore Gestito")
        self.add_info_text("codiceAutorizzazione", "Codice Autorizzazione Referente")

        btn_reg = QPushButton("Registra Referente")
        btn_reg.clicked.connect(self.registra_click)
        self.v_layout.addWidget(btn_reg)

    def add_info_text(self, chiave: str, etichetta: str) -> None:
        lbl = QLabel(f"{etichetta}:")
        txt = QLineEdit(self)
        if "password" in chiave.lower():
            txt.setEchoMode(QLineEdit.Password)
        self.qlines[chiave] = txt
        self.v_layout.addWidget(lbl)
        self.v_layout.addWidget(txt)

    def registra_click(self) -> None:
        """Esegue la registrazione del referente verificando il codice (UML act CreaAccountReferente)."""
        from Referente import Referente
        from GestioneUtenteController import GestioneUtenteController
        ref = Referente.create(
            cod_fiscale=self.qlines.get("cod_fiscale", QLineEdit()).text().strip(),
            nome=self.qlines.get("nome", QLineEdit()).text().strip(),
            cognome=self.qlines.get("cognome", QLineEdit()).text().strip(),
            email=self.qlines.get("email", QLineEdit()).text().strip(),
            telefono=self.qlines.get("telefono", QLineEdit()).text().strip(),
            settoreGestito=self.qlines.get("settoreGestito", QLineEdit()).text().strip(),
            codiceAutorizzazione=self.qlines.get("codiceAutorizzazione", QLineEdit()).text().strip()
        )
        pwd = self.qlines.get("password", QLineEdit()).text().strip()
        ctrl = GestioneUtenteController()
        ctrl.creaAccountReferente(ref, pwd, codice_autorizzazione=ref.codiceAutorizzazione)


class VistaProfilo(QWidget):
    """
    Vista UML: VistaProfilo (in GestioneAccount)
    Attributi UML:
        qlines: dict
        utente: Utente
        v_layout: QVBoxLayout
    Metodi UML:
        __init__(Utente)
        add_info_text(str, str): void
        elimia_account_click(): void
        salva_modifiche_click(): void
    """
    def __init__(self, utente: Utente):
        super().__init__()
        self.utente = utente
        self.qlines: dict[str, QLineEdit] = {}
        self.v_layout = QVBoxLayout(self)
        self._init_ui()

    def _init_ui(self):
        self.v_layout.addWidget(QLabel(f"Profilo Utente: {getattr(self.utente, 'nome', '')} {getattr(self.utente, 'cognome', '')}"))
        self.add_info_text("email", "Email")
        self.add_info_text("telefono", "Telefono")
        self.add_info_text("comitato", "Comitato")

        if self.utente:
            if "email" in self.qlines:
                self.qlines["email"].setText(getattr(self.utente, "email", ""))
            if "telefono" in self.qlines:
                self.qlines["telefono"].setText(getattr(self.utente, "telefono", ""))
            if "comitato" in self.qlines:
                self.qlines["comitato"].setText(getattr(self.utente, "comitato", ""))

        btns = QHBoxLayout()
        btn_salva = QPushButton("Salva Modifiche")
        btn_salva.clicked.connect(self.salva_modifiche_click)
        btns.addWidget(btn_salva)

        btn_del = QPushButton("Elimina Account")
        btn_del.clicked.connect(self.elimia_account_click)
        btns.addWidget(btn_del)
        self.v_layout.addLayout(btns)

    def add_info_text(self, chiave: str, etichetta: str) -> None:
        lbl = QLabel(f"{etichetta}:")
        txt = QLineEdit(self)
        self.qlines[chiave] = txt
        self.v_layout.addWidget(lbl)
        self.v_layout.addWidget(txt)

    def salva_modifiche_click(self) -> None:
        """Salva le modifiche anagrafiche apportate al profilo (UML ModificaDati)."""
        from GestioneUtenteController import GestioneUtenteController
        ctrl = GestioneUtenteController()
        if self.utente:
            self.utente.email = self.qlines.get("email", QLineEdit()).text().strip()
            self.utente.telefono = self.qlines.get("telefono", QLineEdit()).text().strip()
            self.utente.comitato = self.qlines.get("comitato", QLineEdit()).text().strip()
            ctrl.modificaDati(self.utente)

    def elimia_account_click(self) -> None:
        """Elimina definitivamente l'account utente (UML EliminaAccount)."""
        from GestioneUtenteController import GestioneUtenteController
        ctrl = GestioneUtenteController()
        if self.utente:
            cf = getattr(self.utente, "cod_fiscale", "") or getattr(self.utente, "email", "")
            ctrl.eliminaAccount(cf)


class VistaCarriera(QWidget):
    """
    Vista UML: VistaCarriera (in GestioneAccount)
    Attributi UML:
        list_view: QListView
        volontario: Volontario
    Metodi UML:
        __init__(Volontario)
        load_carriera(): void
    """
    def __init__(self, volontario: Volontario):
        super().__init__()
        self.volontario = volontario
        self.list_view = QListView(self)
        self._init_ui()
        self.load_carriera()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Riepilogo Carriera e Storico Formativo:"))
        layout.addWidget(self.list_view)

    def load_carriera(self) -> None:
        """Carica il riepilogo carriera del volontario (UML VisualizzaCarriera)."""
        from GestioneUtenteController import GestioneUtenteController
        ctrl = GestioneUtenteController()
        data = ctrl.visualizzaCarriera(self.volontario) if self.volontario else {}
        model = QStringListModel()
        items = [
            f"Codice Fiscale: {data.get('cod_fiscale', '')}",
            f"Monte Ore Servizio: {data.get('oreServizio', 0)} h",
            f"Patenti: {', '.join(data.get('patenti', []))}",
            f"Qualifiche: {', '.join(data.get('qualifiche', []))}",
            f"Turni Svolti: {data.get('turni_svolti', 0)}",
            f"Corsi Frequentati: {data.get('corsi_frequentati', 0)}"
        ]
        model.setStringList(items)
        self.list_view.setModel(model)


class VistaStatistiche(QWidget):
    """
    Vista UML: VistaStatistiche (in GestioneAccount)
    Attributi UML:
        combo: QComboBox
        label_risultati: QLabel
    Metodi UML:
        __init__()
        mostra_statistiche(dict): void
        onChanged(str): void
    """
    def __init__(self):
        super().__init__()
        self.combo = QComboBox(self)
        self.label_risultati = QLabel(self)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Statistiche Generali Croce Rossa:"))
        self.combo.addItems(["Tutte", "Volontari", "Turni", "Corsi"])
        self.combo.currentTextChanged.connect(self.onChanged)
        layout.addWidget(self.combo)
        layout.addWidget(self.label_risultati)
        self.onChanged("Tutte")

    def onChanged(self, val: str) -> None:
        """Aggiorna le statistiche in base al settore selezionato (UML GestisciStatistiche)."""
        from GestoreStatistiche import GestoreStatistiche
        gs = GestoreStatistiche()
        stats = gs.gestisciStatistiche(val)
        self.mostra_statistiche(stats)

    def mostra_statistiche(self, d: dict) -> None:
        """Mostra a video i parametri statistici aggregati (UML)."""
        txt = (
            f"Volontari Totali: {d.get('totale_volontari', 0)}\n"
            f"Referenti: {d.get('totale_referenti', 0)}\n"
            f"Monte Ore Complessivo: {d.get('monte_ore_complessivo', 0)} h\n"
            f"Turni Totali: {d.get('totale_turni', 0)} (Coperti: {d.get('turni_coperti', 0)})\n"
            f"Tasso Copertura Turni: {d.get('tasso_copertura_turni', 0)}%\n"
            f"Corsi Totali: {d.get('totale_corsi', 0)}"
        )
        self.label_risultati.setText(txt)


class VistaHomeVolontario(QWidget):
    """
    Vista UML: VistaHomeVolontario (in GestioneAccount)
    Attributi UML:
        volontario: Volontario
    Metodi UML:
        __init__(Volontario)
        go_carriera(): void
        go_catalogo_corsi(): void
        go_iscrizioni(): void
        go_patenti(): void
        go_prenotazioni(): void
        go_profilo(): void
        go_turni_disponibili(): void
    """
    def __init__(self, volontario: Volontario):
        super().__init__()
        self.volontario = volontario
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Benvenuto Volontario: {getattr(self.volontario, 'nome', '')} {getattr(self.volontario, 'cognome', '')}"))

        btn_turni = QPushButton("Visualizza Turni Disponibili")
        btn_turni.clicked.connect(self.go_turni_disponibili)
        layout.addWidget(btn_turni)

        btn_pren = QPushButton("Mie Prenotazioni Turni")
        btn_pren.clicked.connect(self.go_prenotazioni)
        layout.addWidget(btn_pren)

        btn_corsi = QPushButton("Catalogo Corsi Formativi")
        btn_corsi.clicked.connect(self.go_catalogo_corsi)
        layout.addWidget(btn_corsi)

        btn_iscr = QPushButton("Mie Iscrizioni Corsi")
        btn_iscr.clicked.connect(self.go_iscrizioni)
        layout.addWidget(btn_iscr)

        btn_pat = QPushButton("Le Mie Patenti")
        btn_pat.clicked.connect(self.go_patenti)
        layout.addWidget(btn_pat)

        btn_carr = QPushButton("La Mia Carriera")
        btn_carr.clicked.connect(self.go_carriera)
        layout.addWidget(btn_carr)

        btn_prof = QPushButton("Modifica Profilo")
        btn_prof.clicked.connect(self.go_profilo)
        layout.addWidget(btn_prof)

    def go_turni_disponibili(self) -> None:
        from Viste.PrenotazioneTurni import VistaTurniDisponibili
        self._w = VistaTurniDisponibili(self.volontario)
        self._w.show()

    def go_prenotazioni(self) -> None:
        from Viste.PrenotazioneTurni import VistaPrenotazioni
        self._w = VistaPrenotazioni(self.volontario)
        self._w.show()

    def go_catalogo_corsi(self) -> None:
        from Viste.IscrizioneCorsi import VistaCatalogoCorsi
        self._w = VistaCatalogoCorsi(self.volontario)
        self._w.show()

    def go_iscrizioni(self) -> None:
        from Viste.IscrizioneCorsi import VistaIscrizioni
        self._w = VistaIscrizioni(self.volontario)
        self._w.show()

    def go_patenti(self) -> None:
        from Viste.GestionePatenti import VistaGestisciPatenti
        self._w = VistaGestisciPatenti(self.volontario)
        self._w.show()

    def go_carriera(self) -> None:
        self._w = VistaCarriera(self.volontario)
        self._w.show()

    def go_profilo(self) -> None:
        self._w = VistaProfilo(self.volontario)
        self._w.show()


class VistaHomeReferente(QWidget):
    """
    Vista UML: VistaHomeReferente (in GestioneAccount)
    Attributi UML:
        referente: Referente
    Metodi UML:
        __init__()
        go_corsi(): void
        go_gestisci_corsi(): void
        go_gestisci_turni(): void
        go_profilo(): void
        go_statistiche(): void
    """
    def __init__(self, referente: Referente = None):
        super().__init__()
        self.referente = referente
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        nom = getattr(self.referente, 'nome', 'Referente')
        layout.addWidget(QLabel(f"Pannello Coordinatore / Referente: {nom}"))

        btn_turni = QPushButton("Gestione Turni Operativi")
        btn_turni.clicked.connect(self.go_gestisci_turni)
        layout.addWidget(btn_turni)

        btn_corsi = QPushButton("Gestione Corsi di Formazione")
        btn_corsi.clicked.connect(self.go_gestisci_corsi)
        layout.addWidget(btn_corsi)

        btn_stats = QPushButton("Statistiche e Indicatori CRI")
        btn_stats.clicked.connect(self.go_statistiche)
        layout.addWidget(btn_stats)

        btn_prof = QPushButton("Profilo Referente")
        btn_prof.clicked.connect(self.go_profilo)
        layout.addWidget(btn_prof)

    def go_corsi(self) -> None:
        self.go_gestisci_corsi()

    def go_gestisci_corsi(self) -> None:
        from Viste.GestioneCorsi import VistaGestisciCorsi
        self._w = VistaGestisciCorsi()
        self._w.show()

    def go_gestisci_turni(self) -> None:
        pass

    def go_statistiche(self) -> None:
        self._w = VistaStatistiche()
        self._w.show()

    def go_profilo(self) -> None:
        if self.referente:
            self._w = VistaProfilo(self.referente)
            self._w.show()


class VistaLogin(QWidget):
    """
    Vista UML: VistaLogin (in GestioneAccount)
    Attributi UML:
        email: QLineEdit
        password: QLineEdit
    Metodi UML:
        __init__()
        login_click(): void
        recupera_credenziali_click(): void
        registrazione_referente_click(): void
        registrazione_volontario_click(): void
    """
    def __init__(self):
        super().__init__()
        self.email = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.vista_home_volontario: Optional[VistaHomeVolontario] = None
        self.vista_home_referente: Optional[VistaHomeReferente] = None
        self.vista_recupero: Optional[VistaRecuperaCredenziali] = None
        self.vista_reg_vol: Optional[VistaRegistrazioneVolontario] = None
        self.vista_reg_ref: Optional[VistaRegistrazioneReferente] = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Accesso al Sistema CRI"))
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password)

        btn_login = QPushButton("Accedi (Login)")
        btn_login.clicked.connect(self.login_click)
        layout.addWidget(btn_login)

        btns_extra = QHBoxLayout()
        btn_rec = QPushButton("Recupera Password")
        btn_rec.clicked.connect(self.recupera_credenziali_click)
        btns_extra.addWidget(btn_rec)

        btn_reg_v = QPushButton("Registrati come Volontario")
        btn_reg_v.clicked.connect(self.registrazione_volontario_click)
        btns_extra.addWidget(btn_reg_v)

        btn_reg_r = QPushButton("Registrati come Referente")
        btn_reg_r.clicked.connect(self.registrazione_referente_click)
        btns_extra.addWidget(btn_reg_r)
        layout.addLayout(btns_extra)

    def login_click(self) -> None:
        """Esegue il login utente (UML act Login)."""
        from GestioneUtenteController import GestioneUtenteController
        from Sistema import Sistema
        ctrl = GestioneUtenteController()
        em = self.email.text().strip()
        pwd = self.password.text().strip()
        success = ctrl.login(em, pwd)
        if success:
            s = Sistema.get_instance()
            user = s.logged_user if s else None
            ruolo = getattr(user, "ruolo", "volontario")
            if str(ruolo).lower() == "referente":
                self.vista_home_referente = VistaHomeReferente(user)
                self.vista_home_referente.show()
            else:
                self.vista_home_volontario = VistaHomeVolontario(user)
                self.vista_home_volontario.show()

    def recupera_credenziali_click(self) -> None:
        """Apre la schermata di recupero credenziali (UML)."""
        self.vista_recupero = VistaRecuperaCredenziali()
        self.vista_recupero.show()

    def registrazione_volontario_click(self) -> None:
        """Apre la schermata di registrazione per un volontario (UML)."""
        self.vista_reg_vol = VistaRegistrazioneVolontario()
        self.vista_reg_vol.show()

    def registrazione_referente_click(self) -> None:
        """Apre la schermata di registrazione per un referente (UML)."""
        self.vista_reg_ref = VistaRegistrazioneReferente()
        self.vista_reg_ref.show()


class GestioneAccount(QWidget):
    """Contenitore per la gestione account."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.vista_login = VistaLogin()
        layout.addWidget(self.vista_login)
