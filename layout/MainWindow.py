# type: ignore
# layout/MainWindow.py
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QFormLayout, QLineEdit, QComboBox, QDialog, QCheckBox, QInputDialog,
    QAbstractItemView, QFrame
)
from PyQt5.QtCore import Qt
from Sistema import Sistema
from Referente import Referente
from Volontario import Volontario
from Mezzo import Mezzo
from Turno import Turno
from Corso import Corso
from Checklist import Checklist
from Report import Report
from layout.modifica_dati_dialog import ModificaDatiDialog

# Importing controllers for business logic delegation
from GestioneUtenteController import GestioneUtenteController
from GestioneFlottaController import GestioneFlottaController
from GestioneTurniController import GestioneTurniController
from GestioneFormazioneController import GestioneFormazioneController

class CreaTurnoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🆕 Crea Nuovo Turno")
        layout = QFormLayout()
        
        from PyQt5.QtWidgets import QSpinBox
        
        import uuid
        self.generated_id = str(uuid.uuid4())[:8].upper()
        self.id_edit = QLineEdit(self.generated_id)
        self.id_edit.setReadOnly(True)
        self.data_edit = QLineEdit("2026-07-15")
        self.luogo_edit = QLineEdit("Sede Centrale")
        self.ora_inizio_edit = QLineEdit("08:00")
        self.ora_fine_edit = QLineEdit("14:00")
        self.patente_combo = QComboBox()
        self.patente_combo.addItems(["Nessuna", "B", "C", "D", "E"])
        self.patente_combo.setCurrentText("B")
        self.paziente_edit = QLineEdit("Nessuno")
        
        # Role specific requirements
        self.req_autista_a = QSpinBox()
        self.req_autista_a.setRange(0, 10)
        self.req_autista_a.setValue(0)
        
        self.req_autista_b = QSpinBox()
        self.req_autista_b.setRange(0, 10)
        self.req_autista_b.setValue(0)
        
        self.req_soccorritore_a = QSpinBox()
        self.req_soccorritore_a.setRange(0, 10)
        self.req_soccorritore_a.setValue(1)
        
        self.req_soccorritore_b = QSpinBox()
        self.req_soccorritore_b.setRange(0, 10)
        self.req_soccorritore_b.setValue(1)
        
        self.servizio_edit = QLineEdit("Emergenza")
        
        layout.addRow("ID Turno (Generato):", self.id_edit)
        layout.addRow("Data (YYYY-MM-DD):", self.data_edit)
        layout.addRow("Luogo:", self.luogo_edit)
        layout.addRow("Ora Inizio:", self.ora_inizio_edit)
        layout.addRow("Ora Fine:", self.ora_fine_edit)
        layout.addRow("Patente Richiesta:", self.patente_combo)
        layout.addRow("Paziente (opzionale):", self.paziente_edit)
        
        # Row layout for roles
        layout.addRow("Fabbisogno Ruoli:", QLabel("<i>Imposta il numero di persone richieste per ruolo:</i>"))
        layout.addRow(" - Autista Tipo A:", self.req_autista_a)
        layout.addRow(" - Autista Tipo B:", self.req_autista_b)
        layout.addRow(" - Soccorritore Tipo A:", self.req_soccorritore_a)
        layout.addRow(" - Soccorritore Tipo B:", self.req_soccorritore_b)
        
        layout.addRow("Tipo Servizio:", self.servizio_edit)
        
        self.btn = QPushButton("Crea")
        self.btn.clicked.connect(self.accept)
        layout.addRow(self.btn)
        self.setLayout(layout)
        
    def get_turno(self) -> Turno:
        pat_val = self.patente_combo.currentText()
        if pat_val == "Nessuna":
            pat_val = ""
            
        tot_persone = (self.req_autista_a.value() + 
                       self.req_autista_b.value() + 
                       self.req_soccorritore_a.value() + 
                       self.req_soccorritore_b.value())
        if tot_persone == 0:
            tot_persone = 1  # Fallback to at least 1 person
            
        t = Turno(
            id=self.generated_id,
            data=self.data_edit.text().strip(),
            luogo=self.luogo_edit.text().strip(),
            oraInizio=self.ora_inizio_edit.text().strip(),
            oraFine=self.ora_fine_edit.text().strip(),
            patenteRichiesta=pat_val,
            paziente=self.paziente_edit.text().strip(),
            personeRichieste=tot_persone,
            tipoServizio=self.servizio_edit.text().strip()
        )
        t.persone_richieste = {
            "Autista Tipo A": self.req_autista_a.value(),
            "Autista Tipo B": self.req_autista_b.value(),
            "Soccorritore Tipo A": self.req_soccorritore_a.value(),
            "Soccorritore Tipo B": self.req_soccorritore_b.value()
        }
        return t

class CreaMezzoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🚐 Aggiungi Nuovo Mezzo")
        layout = QFormLayout()
        
        self.targa_edit = QLineEdit()
        self.tipo_edit = QLineEdit("Ambulanza")
        self.km_edit = QLineEdit("10000")
        self.scadenza_edit = QLineEdit("2027-12-31")
        
        layout.addRow("Targa:", self.targa_edit)
        layout.addRow("Tipo:", self.tipo_edit)
        layout.addRow("Chilometraggio Iniziale:", self.km_edit)
        layout.addRow("Scadenza Assicurazione:", self.scadenza_edit)
        
        self.btn = QPushButton("Aggiungi")
        self.btn.clicked.connect(self.accept)
        layout.addRow(self.btn)
        self.setLayout(layout)
        
    def get_mezzo(self) -> Mezzo:
        return Mezzo(
            targa=self.targa_edit.text().strip(),
            tipo=self.tipo_edit.text().strip(),
            chilometraggioTotale=int(self.km_edit.text().strip() or 0),
            dataScadenzaAssicurazione=self.scadenza_edit.text().strip()
        )

class CreaCorsoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎓 Crea Nuovo Corso Formativo")
        layout = QFormLayout()
        
        import uuid
        self.generated_id = str(uuid.uuid4())[:8].upper()
        self.id_edit = QLineEdit(self.generated_id)
        self.id_edit.setReadOnly(True)
        self.titolo_edit = QLineEdit("Corso BLSD")
        self.inizio_edit = QLineEdit("2026-10-01")
        self.fine_edit = QLineEdit("2026-10-15")
        self.mesi_edit = QLineEdit("24")
        self.qualifica_edit = QLineEdit("Certificazione BLSD")
        
        layout.addRow("ID Corso (Generato):", self.id_edit)
        layout.addRow("Titolo Corso:", self.titolo_edit)
        layout.addRow("Data Inizio:", self.inizio_edit)
        layout.addRow("Data Fine:", self.fine_edit)
        layout.addRow("Mesi Validità:", self.mesi_edit)
        layout.addRow("Qualifica Rilasciata:", self.qualifica_edit)
        
        self.btn = QPushButton("Crea")
        self.btn.clicked.connect(self.accept)
        layout.addRow(self.btn)
        self.setLayout(layout)
        
    def get_corso(self) -> Corso:
        return Corso(
            id=self.generated_id,
            titolo=self.titolo_edit.text().strip(),
            dataInizio=self.inizio_edit.text().strip(),
            dataFine=self.fine_edit.text().strip(),
            mesiValidita=int(self.mesi_edit.text().strip() or 12),
            qualificaRilasciata=self.qualifica_edit.text().strip()
        )

class ModificaTurnoDialog(QDialog):
    def __init__(self, turno, parent=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import QSpinBox
        self.setWindowTitle(f"✏️ Modifica Turno — {turno.id}")
        self.setMinimumWidth(420)
        layout = QFormLayout()

        self.data_edit = QLineEdit(turno.data)
        self.luogo_edit = QLineEdit(turno.luogo)
        self.ora_inizio_edit = QLineEdit(turno.oraInizio)
        self.ora_fine_edit = QLineEdit(turno.oraFine)
        self.servizio_edit = QLineEdit(turno.tipoServizio)
        self.paziente_edit = QLineEdit(turno.paziente)

        self.patente_combo = QComboBox()
        self.patente_combo.addItems(["Nessuna", "B", "C", "D", "E"])
        cur_pat = turno.patenteRichiesta or "Nessuna"
        self.patente_combo.setCurrentText(cur_pat if cur_pat else "Nessuna")

        req = getattr(turno, "persone_richieste", {})
        self.req_autista_a = QSpinBox(); self.req_autista_a.setRange(0, 10); self.req_autista_a.setValue(req.get("Autista Tipo A", 0))
        self.req_autista_b = QSpinBox(); self.req_autista_b.setRange(0, 10); self.req_autista_b.setValue(req.get("Autista Tipo B", 0))
        self.req_soccorritore_a = QSpinBox(); self.req_soccorritore_a.setRange(0, 10); self.req_soccorritore_a.setValue(req.get("Soccorritore Tipo A", 0))
        self.req_soccorritore_b = QSpinBox(); self.req_soccorritore_b.setRange(0, 10); self.req_soccorritore_b.setValue(req.get("Soccorritore Tipo B", 0))

        self.stato_combo = QComboBox()
        self.stato_combo.addItems(["Proposto", "Aperto", "Chiuso", "Concluso", "Annullato"])
        self.stato_combo.setCurrentText(turno.stato or "Proposto")

        layout.addRow("Data (YYYY-MM-DD):", self.data_edit)
        layout.addRow("Luogo:", self.luogo_edit)
        layout.addRow("Ora Inizio:", self.ora_inizio_edit)
        layout.addRow("Ora Fine:", self.ora_fine_edit)
        layout.addRow("Tipo Servizio:", self.servizio_edit)
        layout.addRow("Paziente:", self.paziente_edit)
        layout.addRow("Patente Richiesta:", self.patente_combo)
        layout.addRow("Stato:", self.stato_combo)
        layout.addRow(QLabel("<i>Fabbisogno per ruolo:</i>"))
        layout.addRow(" - Autista Tipo A:", self.req_autista_a)
        layout.addRow(" - Autista Tipo B:", self.req_autista_b)
        layout.addRow(" - Soccorritore Tipo A:", self.req_soccorritore_a)
        layout.addRow(" - Soccorritore Tipo B:", self.req_soccorritore_b)

        btn = QPushButton("💾 Salva Modifiche")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)
        self.setLayout(layout)

    def apply_to(self, turno):
        turno.data = self.data_edit.text().strip()
        turno.luogoDestinazione = self.luogo_edit.text().strip()
        turno.luogoPrelevamento = self.luogo_edit.text().strip()
        pat = self.patente_combo.currentText()
        turno.patenteRichiesta = "" if pat == "Nessuna" else pat
        turno.paziente = self.paziente_edit.text().strip()
        turno.oraInizio = self.ora_inizio_edit.text().strip()
        turno.oraFine = self.ora_fine_edit.text().strip()
        turno.tipoServizio = self.servizio_edit.text().strip()
        turno.stato = self.stato_combo.currentText()
        turno.persone_richieste = {
            "Autista Tipo A": self.req_autista_a.value(),
            "Autista Tipo B": self.req_autista_b.value(),
            "Soccorritore Tipo A": self.req_soccorritore_a.value(),
            "Soccorritore Tipo B": self.req_soccorritore_b.value()
        }
        turno.personeRichieste = sum(turno.persone_richieste.values()) or 1


class ModificaMezzoDialog(QDialog):
    def __init__(self, mezzo, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"✏️ Modifica Mezzo — {mezzo.targa}")
        self.setMinimumWidth(380)
        layout = QFormLayout()

        self.targa_edit = QLineEdit(mezzo.targa)
        self.targa_edit.setReadOnly(True)  # la targa è la chiave, non modificabile
        self.tipo_edit = QLineEdit(mezzo.tipo)
        self.km_edit = QLineEdit(str(mezzo.chilometraggioTotale))
        self.scadenza_edit = QLineEdit(str(mezzo.dataScadenzaAssicurazione or ""))

        self.stato_combo = QComboBox()
        self.stato_combo.addItems(["Disponibile", "In Manutenzione", "Fuori Servizio"])
        self.stato_combo.setCurrentText(mezzo.stato or "Disponibile")

        layout.addRow("Targa:", self.targa_edit)
        layout.addRow("Tipo:", self.tipo_edit)
        layout.addRow("Chilometraggio:", self.km_edit)
        layout.addRow("Scadenza Assicurazione:", self.scadenza_edit)
        layout.addRow("Stato:", self.stato_combo)

        btn = QPushButton("💾 Salva Modifiche")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)
        self.setLayout(layout)

    def apply_to(self, mezzo):
        mezzo.tipo = self.tipo_edit.text().strip()
        try:
            mezzo.chilometraggioTotale = int(self.km_edit.text().strip())
        except ValueError:
            pass
        mezzo.dataScadenzaAssicurazione = self.scadenza_edit.text().strip()
        mezzo.stato = self.stato_combo.currentText()
        mezzo.disponibile = (mezzo.stato == "Disponibile")


class ModificaCorsoDialog(QDialog):
    def __init__(self, corso, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"✏️ Modifica Corso — {corso.titolo}")
        self.setMinimumWidth(400)
        layout = QFormLayout()

        self.titolo_edit = QLineEdit(corso.titolo)
        self.inizio_edit = QLineEdit(corso.dataInizio)
        self.fine_edit = QLineEdit(corso.dataFine)
        self.mesi_edit = QLineEdit(str(getattr(corso, "mesiValidita", 24)))
        self.qualifica_edit = QLineEdit(getattr(corso, "qualificaRilasciata", ""))

        self.stato_combo = QComboBox()
        self.stato_combo.addItems(["Pianificato", "Aperto", "In Corso", "Concluso", "Annullato"])
        self.stato_combo.setCurrentText(corso.stato or "Pianificato")

        layout.addRow("Titolo Corso:", self.titolo_edit)
        layout.addRow("Data Inizio:", self.inizio_edit)
        layout.addRow("Data Fine:", self.fine_edit)
        layout.addRow("Mesi Validità:", self.mesi_edit)
        layout.addRow("Qualifica Rilasciata:", self.qualifica_edit)
        layout.addRow("Stato:", self.stato_combo)

        btn = QPushButton("💾 Salva Modifiche")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)
        self.setLayout(layout)

    def apply_to(self, corso):
        corso.titolo = self.titolo_edit.text().strip()
        corso.dataInizio = self.inizio_edit.text().strip()
        corso.dataFine = self.fine_edit.text().strip()
        try:
            corso.mesiValidita = int(self.mesi_edit.text().strip())
        except ValueError:
            pass
        corso.qualificaRilasciata = self.qualifica_edit.text().strip()
        corso.stato = self.stato_combo.currentText()


class CompilaChecklistDialog(QDialog):
    def __init__(self, checklist: Checklist, ruolo: str, targa: str = "CRI 302 AJ", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"📋 Compila Checklist ({ruolo})")
        self.resize(500, 600)
        self.checklist = checklist
        self.ruolo = ruolo
        self.targa = targa
        self.current_index = 0
        
        # Elenco completo dei controlli
        self.tutti_i_controlli = [
            {"categoria": "800-Materiale Vario", "nome": "Biancheria e Pulizia", "tipo": "ok_ko"},
            {"categoria": "400-Attrezzature", "nome": "Adattatore Pediatrico per Barella Autocaricante (Pedi-Mate)", "tipo": "ok_ko"},
            {"categoria": "400-Attrezzature", "nome": "Adattatore Pediatrico per Spinale (Pedi-Sleeve)", "tipo": "ok_ko"},
            {"categoria": "400-Attrezzature", "nome": "(2) T-POD (Cintura di immobilizzazione pelvica)", "tipo": "ok_ko"},
            {"categoria": "400-Attrezzature", "nome": "KED", "tipo": "ok_ko"},
            {"categoria": "400-Attrezzature", "nome": "(2 set) Set Collari cervicali Adulto e Pediatrico", "tipo": "ok_ko"},
            {"categoria": "400-Attrezzature", "nome": "(1 Set) Steccobende", "tipo": "ok_ko"},
            {"categoria": "400-Attrezzature", "nome": "Materassino a depressione (+pompa)", "tipo": "ok_ko"},
            {"categoria": "200-Monossido", "nome": "Rilevatore CO (Monossido)", "tipo": "ok_ko"},
            {"categoria": "100-Mezzo", "nome": "Kit da scasso + Kit cambio Ruota (Ruota di scorta)", "tipo": "ok_ko"},
            {"categoria": "100-Mezzo", "nome": "Radio Veicolare CRI / 118 + Telefono (dispositivi) di servizio", "tipo": "ok_ko"},
            {"categoria": "100-Mezzo", "nome": "Impianto di climatizzazione (intero sistema)", "tipo": "ok_ko"},
            {"categoria": "100-Mezzo", "nome": "Livello Olio motore", "tipo": "scelta", "opzioni": ["Pieno", "1/2", "Vuoto"]},
            {"categoria": "100-Mezzo", "nome": "Livello Carburante", "tipo": "scelta", "opzioni": ["Pieno", "3/4", "1/2", "Riserva"]},
            {"categoria": "100-Mezzo", "nome": "Torcia Elettrica (+cono giallo)", "tipo": "ok_ko"},
            {"categoria": "100-Mezzo", "nome": "(2) Estintori (V. guida e V. sanitario)", "tipo": "ok_ko"},
            {"categoria": "100-Mezzo", "nome": "Dispositivi di Sicurezza (Cicalino retromarcia, sensore prossimità, telecamera)", "tipo": "ok_ko"},
            {"categoria": "100-Mezzo", "nome": "(3) Caschi di Protezione", "tipo": "ok_ko"},
            {"categoria": "100-Mezzo", "nome": "Documentazione Veicolo (Assicurazione, Libretto di circolazione, Revisione e Tessera carburante)", "tipo": "ok_ko"},
            {"categoria": "100-Mezzo", "nome": "Controllo livelli (Liquido Radiatore, tergicristalli, servosterzo)", "tipo": "ok_ko"},
            {"categoria": "000-Quick look", "nome": "Bombolino O2 - DUE (2/3 lt)", "tipo": "atmosfere"},
            {"categoria": "000-Quick look", "nome": "Bombolino O2 - UNO (2/3 lt)", "tipo": "atmosfere"},
            {"categoria": "000-Quick look", "nome": "Barella Spinale + Ragno e fermacapi", "tipo": "ok_ko"},
            {"categoria": "000-Quick look", "nome": "Barella Cucchiaio + cinture a moschettone (n°4)", "tipo": "ok_ko"},
            {"categoria": "000-Quick look", "nome": "Telo con maniglie", "tipo": "ok_ko"},
            {"categoria": "000-Quick look", "nome": "Barella autocaricante + cinture (set completo)", "tipo": "ok_ko"},
            {"categoria": "000-Quick look", "nome": "Sedia cingolata", "tipo": "ok_ko"},
            {"categoria": "000-Quick look", "nome": "Monitor Defibrillatore", "tipo": "ok_ko"},
            {"categoria": "000-Quick look", "nome": "Bombola Fissa O2 - DUE (7lt)", "tipo": "atmosfere"},
            {"categoria": "000-Quick look", "nome": "Bombola Fissa O2 - UNO (7lt)", "tipo": "atmosfere"},
            {"categoria": "000-Quick look", "nome": "Impianto distribuzione O2", "tipo": "ok_ko"},
            {"categoria": "000-Quick look", "nome": "Pneumatici (Controllo visivo ed efficienza) + presenza catene da neve", "tipo": "ok_ko"},
            {"categoria": "000-Quick look", "nome": "Controllo generale - Mezzo e Allestimento", "tipo": "ok_ko"},
            {"categoria": "000-Quick look", "nome": "Dispositivi di Emergenza (Sirena primaria, secondaria, lampeggianti, strobo e faro brandeggiabile)", "tipo": "ok_ko"},
            {"categoria": "000-Quick look", "nome": "Avviamento Motore", "tipo": "ok_ko"},
            # Controlli addizionali Soccorritore
            {"categoria": "900-Zaino", "nome": "Zaino di Soccorso", "tipo": "ok_ko"},
            {"categoria": "800-Materiale Vario", "nome": "Materiale Vario", "tipo": "ok_ko"},
            {"categoria": "750-KIT", "nome": "Kit Intubazione", "tipo": "ok_ko"},
            {"categoria": "750-KIT", "nome": "Kit Vari (Cateterismo, Sondino Nasogastrico, ecc. - vedi lista)", "tipo": "ok_ko"},
            {"categoria": "750-KIT", "nome": "Kit C-PAP", "tipo": "ok_ko"},
            {"categoria": "700-DPI", "nome": "DPI", "tipo": "ok_ko"},
            {"categoria": "600-Medicazione", "nome": "Medicazione (2 di 2)", "tipo": "ok_ko"},
            {"categoria": "600-Medicazione", "nome": "Medicazione (1 di 2)", "tipo": "ok_ko"},
            {"categoria": "500-Infusione", "nome": "Vano: Infusione", "tipo": "ok_ko"},
            {"categoria": "500-Infusione", "nome": "Set Infusione (2 di 2)", "tipo": "ok_ko"},
            {"categoria": "400-DPI", "nome": "Guanti Monouso", "tipo": "ok_ko"},
            {"categoria": "300-Materiale Vario", "nome": "Biancheria (Lenzuola, Coperte)", "tipo": "ok_ko"}
        ]
        
        # Filtra i controlli in base al ruolo
        dpi_controlli = [
            {"categoria": "700-DPI", "nome": "DPI Personali (personale checklist)", "tipo": "ok_ko"},
            {"categoria": "400-DPI", "nome": "Guanti Monouso", "tipo": "ok_ko"},
            {"categoria": "100-Mezzo", "nome": "(3) Caschi di Protezione", "tipo": "ok_ko"}
        ]
        
        if "Autista" in ruolo:
            self.controlli = [
                c for c in self.tutti_i_controlli 
                if c["categoria"] in ["100-Mezzo", "100-Veicolo"] or 
                c["nome"] in [
                    "Biancheria e Pulizia",
                    "Pneumatici (Controllo visivo ed efficienza) + presenza catene da neve",
                    "Controllo generale - Mezzo e Allestimento",
                    "Dispositivi di Emergenza (Sirena primaria, secondaria, lampeggianti, strobo e faro brandeggiabile)",
                    "Avviamento Motore"
                ]
            ]
        else: # Soccorritore (Tipo A / Tipo B)
            # Soccorritore controlla zaino e attrezzature mediche
            self.controlli = [
                c for c in self.tutti_i_controlli 
                if not (c["categoria"] in ["100-Mezzo", "100-Veicolo"] or 
                c["nome"] in [
                    "Pneumatici (Controllo visivo ed efficienza) + presenza catene da neve",
                    "Controllo generale - Mezzo e Allestimento",
                    "Dispositivi di Emergenza (Sirena primaria, secondaria, lampeggianti, strobo e faro brandeggiabile)",
                    "Avviamento Motore"
                ])
            ]
            
        # Aggiunge i controlli della personale checklist (DPI) per tutti
        for dpi in dpi_controlli:
            if not any(c["nome"] == dpi["nome"] for c in self.controlli):
                self.controlli.append(dpi)
        
        self.risposte = {}
        self.setup_ui()
        self.update_current_check()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # 1. Header block
        self.header_bg = QWidget()
        self.header_bg.setStyleSheet("background-color: #2b2b2b; border-radius: 6px; padding: 10px;")
        header_layout = QVBoxLayout(self.header_bg)
        
        self.lbl_veicolo = QLabel(f"Veicolo: {self.targa} (70) - Inizio")
        self.lbl_veicolo.setAlignment(Qt.AlignCenter)
        self.lbl_veicolo.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        
        self.lbl_status = QLabel(f"N. Controlli Restanti {len(self.controlli)} Totale Controlli restanti {len(self.controlli)} ({self.ruolo})")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("font-size: 11px; color: #aaaaaa;")
        
        header_layout.addWidget(self.lbl_veicolo)
        header_layout.addWidget(self.lbl_status)
        main_layout.addWidget(self.header_bg)
        
        # 2. Category & Item Banner
        self.banner_bg = QWidget()
        self.banner_bg.setStyleSheet("background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 15px;")
        banner_layout = QVBoxLayout(self.banner_bg)
        
        self.lbl_categoria = QLabel("800-Materiale Vario")
        self.lbl_categoria.setAlignment(Qt.AlignCenter)
        self.lbl_categoria.setStyleSheet("font-size: 12px; font-weight: bold; color: #155724;")
        
        self.lbl_nome = QLabel("Biancheria e Pulizia")
        self.lbl_nome.setAlignment(Qt.AlignCenter)
        self.lbl_nome.setStyleSheet("font-size: 16px; font-weight: bold; color: #155724;")
        
        banner_layout.addWidget(self.lbl_categoria)
        banner_layout.addWidget(self.lbl_nome)
        main_layout.addWidget(self.banner_bg)
        
        # 3. Input Area
        self.input_area = QWidget()
        self.input_layout = QVBoxLayout(self.input_area)
        main_layout.addWidget(self.input_area)
        
        # Spacer
        main_layout.addStretch()
        
        # 4. Bottom Action buttons
        bottom_actions = QHBoxLayout()
        
        self.btn_posponi = QPushButton("⏮️ Posponi")
        self.btn_posponi.setStyleSheet("background-color: #555555; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.btn_posponi.clicked.connect(self.posponi_controllo)
        
        self.btn_ometti = QPushButton("❌ Ometti")
        self.btn_ometti.setStyleSheet("background-color: #cc0000; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.btn_ometti.clicked.connect(self.ometti_controllo)
        
        self.btn_upload = QPushButton("☁️ Upload")
        self.btn_upload.setStyleSheet("background-color: #555555; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.btn_upload.clicked.connect(self.upload_foto)
        
        self.btn_invia = QPushButton("✔️ Completa")
        self.btn_invia.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        self.btn_invia.clicked.connect(self.completa_checklist)
        
        bottom_actions.addWidget(self.btn_posponi)
        bottom_actions.addWidget(self.btn_ometti)
        bottom_actions.addWidget(self.btn_upload)
        bottom_actions.addWidget(self.btn_invia)
        
        main_layout.addLayout(bottom_actions)
        self.setLayout(main_layout)
        
    def update_current_check(self):
        restanti = len(self.controlli) - self.current_index
        self.lbl_status.setText(f"N. Controlli Restanti {restanti} Totale Controlli restanti {len(self.controlli)} ({self.ruolo})")
        
        controllo = self.controlli[self.current_index]
        self.lbl_categoria.setText(controllo["categoria"])
        self.lbl_nome.setText(controllo["nome"])
        
        # Clear layout safely (recursive removal to avoid overlaps)
        self.clear_layout(self.input_layout)
                
        tipo = controllo["tipo"]
        if tipo == "ok_ko":
            row = QHBoxLayout()
            btn_ok = QPushButton("OK")
            btn_ok.setStyleSheet("background-color: #28a745; color: white; font-size: 20px; font-weight: bold; padding: 25px; border-radius: 6px;")
            btn_ok.clicked.connect(lambda: self.rispondi("OK"))
            
            btn_ko = QPushButton("KO")
            btn_ko.setStyleSheet("background-color: #dc3545; color: white; font-size: 20px; font-weight: bold; padding: 25px; border-radius: 6px;")
            btn_ko.clicked.connect(lambda: self.rispondi("KO"))
            
            row.addWidget(btn_ok)
            row.addWidget(btn_ko)
            self.input_layout.addLayout(row)
            
        elif tipo == "scelta":
            row = QHBoxLayout()
            for opzione in controllo["opzioni"]:
                btn_opz = QPushButton(opzione)
                btn_opz.setStyleSheet("background-color: #444444; color: white; font-size: 16px; font-weight: bold; padding: 20px; border-radius: 6px;")
                # Use default arguments in lambda to capture loop variables correctly
                btn_opz.clicked.connect(lambda checked, o=opzione: self.rispondi(o))
                row.addWidget(btn_opz)
            self.input_layout.addLayout(row)
            
        elif tipo == "atmosfere":
            form = QVBoxLayout()
            lbl_atm = QLabel("Atmosfere:")
            lbl_atm.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
            lbl_atm.setAlignment(Qt.AlignCenter)
            form.addWidget(lbl_atm)
            
            self.edit_atm = QLineEdit("200")
            self.edit_atm.setAlignment(Qt.AlignCenter)
            self.edit_atm.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px; background-color: #444; color: white;")
            form.addWidget(self.edit_atm)
            
            btn_conferma = QPushButton("Conferma Atmosfere")
            btn_conferma.setStyleSheet("background-color: #007bff; color: white; font-size: 16px; font-weight: bold; padding: 15px; border-radius: 6px;")
            btn_conferma.clicked.connect(lambda: self.rispondi(self.edit_atm.text().strip()))
            form.addWidget(btn_conferma)
            
            self.input_layout.addLayout(form)
            
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
                else:
                    sublayout = item.layout()
                    if sublayout is not None:
                        self.clear_layout(sublayout)

    def rispondi(self, valore):
        controllo = self.controlli[self.current_index]
        self.risposte[controllo["nome"]] = valore
        
        if self.current_index < len(self.controlli) - 1:
            self.current_index += 1
            self.update_current_check()
        else:
            self.fine_checklist()
            
    def posponi_controllo(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_current_check()
            
    def ometti_controllo(self):
        controllo = self.controlli[self.current_index]
        self.risposte[controllo["nome"]] = "OAC"
        if self.current_index < len(self.controlli) - 1:
            self.current_index += 1
            self.update_current_check()
        else:
            self.fine_checklist()
            
    def upload_foto(self):
        QMessageBox.information(self, "Upload Foto", "📸 Foto allegata con successo al controllo.")
        
    def completa_checklist(self):
        self.fine_checklist()
        
    def fine_checklist(self):
        ha_ko = any(v == "KO" for v in self.risposte.values())
        self.checklist.controlliMeccanici = not ha_ko
        self.checklist.dispositiviPresenti = not ha_ko
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Checklist Completata")
        msg.setText("La checklist è stata completata.")
        msg.setIcon(QMessageBox.Information)
        msg.addButton("Click per Proseguire", QMessageBox.AcceptRole)
        msg.exec_()
        self.accept()

class CompilaResocontoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📝 Resoconto Fine Turno")
        layout = QFormLayout()
        
        self.km_edit = QLineEdit("50")
        self.ore_edit = QLineEdit("6")
        self.note_edit = QLineEdit("Intervento ordinario di assistenza.")
        
        layout.addRow("Chilometri percorsi:", self.km_edit)
        layout.addRow("Ore effettive lavorate:", self.ore_edit)
        layout.addRow("Note intervento:", self.note_edit)
        
        btn = QPushButton("Invia Resoconto")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)
        self.setLayout(layout)
        
    def get_dati(self) -> tuple[int, int, str]:
        return (
            int(self.km_edit.text().strip() or 0),
            int(self.ore_edit.text().strip() or 0),
            self.note_edit.text().strip()
        )

class MainWindow(QWidget):
    def __init__(self, sistema, callback_logout=None):
        super().__init__()
        self.sistema = sistema
        self.callback_logout = callback_logout
        
        # Preserve the logged in user retrieved from login
        prev_logged_user = self.sistema.logged_user
        
        # Synchronize with Firebase Firestore
        self.sistema.sincronizza_con_firebase()
        
        # If the database sync returned no volunteers, populate with local demo data as fallback
        if not self.sistema.volontari:
            self.sistema = self.setup_sistema()
            
        # Restore the logged-in user (re-pointing to the synced instance from Firebase)
        if prev_logged_user:
            synced_user = self.sistema.get_volontario(prev_logged_user.cod_fiscale)
            if synced_user:
                self.sistema.logged_user = synced_user
            else:
                self.sistema.logged_user = prev_logged_user
            
        # Ensure the logged-in user is added to the system list of volunteers
        if self.sistema.logged_user:
            if not self.sistema.get_volontario(self.sistema.logged_user.cod_fiscale):
                self.sistema.aggiungi_volontario(self.sistema.logged_user)

        # Controllers
        self.utente_controller = GestioneUtenteController()
        self.flotta_controller = GestioneFlottaController()
        self.turni_controller = GestioneTurniController()
        self.formazione_controller = GestioneFormazioneController()

        # Window configuration
        self.setWindowTitle("🚑 Gestione Volontari - Croce Rossa Italiana")
        self.resize(800, 600)

        # Dark theme styling
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QTableWidget {
                background-color: #242424;
                gridline-color: #333333;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                color: #e0e0e0;
            }
            QTableWidget QLineEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #ff5252;
                border-radius: 4px;
                padding: 2px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #d32f2f;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #d32f2f;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #1e1e1e;
                border-radius: 8px;
            }
            QTabBar {
                border-bottom: 2px solid #2b2b2b;
            }
            QTabBar::tab {
                background: #1a1a1a;
                border: none;
                border-bottom: 2px solid transparent;
                padding: 10px 20px;
                color: #888;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #1a1a1a;
                color: #ffffff;
                border-bottom: 2px solid #d32f2f;
            }
            QTabBar::tab:hover {
                color: #ffffff;
            }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid #d32f2f;
            }
            QPushButton {
                background-color: #d32f2f;
                color: #ffffff;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ef5350;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #1a1a1a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #444444;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # Main Layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)
        
        # Header Container Frame
        header_container = QFrame()
        header_container.setObjectName("TopHeader")
        header_container.setStyleSheet("""
            QFrame#TopHeader {
                background-color: #242424;
                border: 1px solid #333;
                border-radius: 8px;
            }
        """)
        self.header_layout = QHBoxLayout(header_container)
        self.header_layout.setContentsMargins(15, 12, 15, 12)
        
        self.user_label = QLabel()
        self.user_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        self.header_layout.addWidget(self.user_label)
        
        # Actions
        self.header_layout.addStretch()
        
        # Edit Profile Button
        btn_modifica_dati = QPushButton("Modifica Profilo")
        btn_modifica_dati.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: 1px solid #555;
                color: #eee;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        btn_modifica_dati.clicked.connect(self.modifica_dati_volontario)
        self.header_layout.addWidget(btn_modifica_dati)
        
        # Logout Button
        btn_logout = QPushButton("Esci")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #b71c1c;
                color: white;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        btn_logout.clicked.connect(self.azione_logout)
        self.header_layout.addWidget(btn_logout)
        
        self.main_layout.addWidget(header_container)
        
        # Tab Widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        self.setLayout(self.main_layout)
        self.update_ui()

    def update_user_label(self):
        user = self.sistema.logged_user
        if user:
            self.user_label.setText(f"👤 <b>{user.get_nome_completo()}</b> | Ruolo: <font color='#ff5252'><b>{user.ruolo.upper()}</b></font>")
        else:
            self.user_label.setText("Nessun utente collegato.")

    def azione_logout(self):
        if self.callback_logout:
            self.callback_logout()
        else:
            self.close()

    def update_ui(self):
        self.update_user_label()
        self.tab_widget.clear()
        
        # Build tabs based on role
        user = self.sistema.logged_user
        if not user:
            return
            
        is_referente = isinstance(user, Referente)
        
        # 1. Dashboard Tab
        self.tab_widget.addTab(self.crea_tab_dashboard(is_referente), "📊 Dashboard")
        
        # 2. Turni Tab
        self.tab_widget.addTab(self.crea_tab_turni(is_referente), "🗓️ Turni")
        
        # 3. Flotta Tab
        self.tab_widget.addTab(self.crea_tab_flotta(is_referente), "🚐 Flotta")
        
        # 4. Formazione Tab
        self.tab_widget.addTab(self.crea_tab_formazione(is_referente), "🎓 Formazione")

    # --- TAB DASHBOARD ---
    def crea_tab_dashboard(self, is_referente):
        from PyQt5.QtWidgets import QScrollArea, QFrame
        
        # Outer widget and layout
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Scroll Area for clean mobile-like feel
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # 1. Welcome Card (Gradient red card)
        welcome_card = QFrame()
        welcome_card.setStyleSheet("""
            .QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d32f2f, stop:1 #ef5350);
                border-radius: 8px;
            }
            QLabel {
                background-color: transparent;
                color: #ffffff;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(20, 20, 20, 20)
        welcome_layout.setSpacing(5)
        
        user_name = self.sistema.logged_user.nome.capitalize()
        welcome_title = QLabel(f"<h2 style='color: white; margin: 0; font-family: Inter, Segoe UI, sans-serif;'>Bentornato, {user_name}! 👋</h2>")
        welcome_subtitle = QLabel(f"<p style='color: #ffebee; margin: 5px 0 0 0; font-size: 14px;'>Portale Croce Rossa Italiana • Ruolo: {self.sistema.logged_user.ruolo.capitalize()}</p>")
        welcome_title.setWordWrap(True)
        welcome_subtitle.setWordWrap(True)
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_subtitle)
        scroll_layout.addWidget(welcome_card)
        
        # 2. Volunteer Personal Metrics (Always visible)
        metrics_widget = QWidget()
        metrics_layout = QHBoxLayout(metrics_widget)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(15)
        
        # Card 1: Hours
        card_hours = QFrame()
        card_hours.setStyleSheet("""
            .QFrame {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 8px;
            }
            QLabel {
                background-color: transparent;
            }
        """)
        card_hours.setMinimumHeight(120)
        ch_layout = QVBoxLayout(card_hours)
        ch_layout.setContentsMargins(12, 12, 12, 12)
        ch_layout.setSpacing(6)
        
        ch_icon = QLabel("<span style='font-size: 20px;'>⏱️</span>")
        ch_val = QLabel(f"<span style='font-size: 18px; font-weight: bold; color: #ff5252;'>{self.sistema.logged_user.calcola_ore_totali():.1f} h</span>")
        ch_lbl = QLabel("<span style='color: #888; font-size: 11px;'>Monte Ore Servizio</span>")
        ch_icon.setWordWrap(True)
        ch_val.setWordWrap(True)
        ch_lbl.setWordWrap(True)
        
        ch_layout.addWidget(ch_icon)
        ch_layout.addWidget(ch_val)
        ch_layout.addWidget(ch_lbl)
        metrics_layout.addWidget(card_hours)
        
        # Card 2: Shift count
        card_shifts = QFrame()
        card_shifts.setStyleSheet("""
            .QFrame {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 8px;
            }
            QLabel {
                background-color: transparent;
            }
        """)
        card_shifts.setMinimumHeight(120)
        cs_layout = QVBoxLayout(card_shifts)
        cs_layout.setContentsMargins(12, 12, 12, 12)
        cs_layout.setSpacing(6)
        
        cs_icon = QLabel("<span style='font-size: 20px;'>🗓️</span>")
        cs_val = QLabel(f"<span style='font-size: 18px; font-weight: bold; color: #00e676;'>{len(self.sistema.logged_user.turni_assegnati)}</span>")
        cs_lbl = QLabel("<span style='color: #888; font-size: 11px;'>Turni Prenotati</span>")
        cs_icon.setWordWrap(True)
        cs_val.setWordWrap(True)
        cs_lbl.setWordWrap(True)
        
        cs_layout.addWidget(cs_icon)
        cs_layout.addWidget(cs_val)
        cs_layout.addWidget(cs_lbl)
        metrics_layout.addWidget(card_shifts)
        
        # Card 3: Licenses
        card_lics = QFrame()
        card_lics.setStyleSheet("""
            .QFrame {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 8px;
            }
            QLabel {
                background-color: transparent;
            }
        """)
        card_lics.setMinimumHeight(120)
        cl_layout = QVBoxLayout(card_lics)
        cl_layout.setContentsMargins(12, 12, 12, 12)
        cl_layout.setSpacing(6)
        
        cl_icon = QLabel("<span style='font-size: 20px;'>💳</span>")
        lics_str = ", ".join(self.sistema.logged_user.patenti) if self.sistema.logged_user.patenti else "Nessuna"
        cl_val = QLabel(f"<span style='font-size: 14px; font-weight: bold; color: #40c4ff;'>{lics_str}</span>")
        cl_lbl = QLabel("<span style='color: #888; font-size: 11px;'>Patenti Abilitate</span>")
        cl_icon.setWordWrap(True)
        cl_val.setWordWrap(True)
        cl_lbl.setWordWrap(True)
        
        cl_layout.addWidget(cl_icon)
        cl_layout.addWidget(cl_val)
        cl_layout.addWidget(cl_lbl)
        metrics_layout.addWidget(card_lics)
        
        scroll_layout.addWidget(metrics_widget)
        
        # 3. Referente / Coordinator Section (Only visible for Referente)
        if is_referente:
            admin_card = QFrame()
            admin_card.setStyleSheet("""
                .QFrame {
                    background-color: #2b2b2b;
                    border: 1px solid #444;
                    border-radius: 8px;
                }
                QLabel {
                    background-color: transparent;
                }
            """)
            admin_card.setMinimumHeight(110)
            ac_layout = QVBoxLayout(admin_card)
            ac_layout.setContentsMargins(15, 15, 15, 15)
            ac_layout.setSpacing(5)
            
            lbl_title = QLabel("<h3 style='color: white; margin: 0; font-family: Inter, sans-serif;'>🛠️ Centro di Controllo Coordinatore</h3>")
            lbl_desc = QLabel(
                "<p style='color: #ccc; line-height: 1.4; font-size: 12px; margin: 5px 0 0 0;'>"
                "Dal menu superiore puoi gestire l'intera flotta veicoli della Croce Rossa, pianificare "
                "e pubblicare i turni di servizio per i volontari, ed attestare le certificazioni e le qualifiche "
                "formative abilitanti dei soccorritori."
                "</p>"
            )
            lbl_title.setWordWrap(True)
            lbl_desc.setWordWrap(True)
            ac_layout.addWidget(lbl_title)
            ac_layout.addWidget(lbl_desc)
            scroll_layout.addWidget(admin_card)
            
            # Quick stats for coordinator
            stats_widget = QWidget()
            stats_layout = QHBoxLayout(stats_widget)
            stats_layout.setContentsMargins(0, 0, 0, 0)
            stats_layout.setSpacing(15)
            
            # Stat 1: Volontari
            card_v = QFrame()
            card_v.setStyleSheet("""
                .QFrame {
                    background-color: #1e1e1e;
                    border: 1px solid #333;
                    border-radius: 8px;
                }
                QLabel {
                    background-color: transparent;
                }
            """)
            card_v.setMinimumHeight(85)
            cv_lay = QVBoxLayout(card_v)
            cv_lay.setContentsMargins(10, 10, 10, 10)
            cv_lay.setSpacing(4)
            cv_val = QLabel(f"<span style='font-size: 16px; font-weight: bold; color: white;'>{len(self.sistema.volontari)}</span>")
            cv_lbl = QLabel("<span style='color: #888; font-size: 11px;'>Volontari Registrati</span>")
            cv_val.setWordWrap(True)
            cv_lbl.setWordWrap(True)
            cv_lay.addWidget(cv_val)
            cv_lay.addWidget(cv_lbl)
            stats_layout.addWidget(card_v)
            
            # Stat 2: Mezzi
            card_m = QFrame()
            card_m.setStyleSheet("""
                .QFrame {
                    background-color: #1e1e1e;
                    border: 1px solid #333;
                    border-radius: 8px;
                }
                QLabel {
                    background-color: transparent;
                }
            """)
            card_m.setMinimumHeight(85)
            cm_lay = QVBoxLayout(card_m)
            cm_lay.setContentsMargins(10, 10, 10, 10)
            cm_lay.setSpacing(4)
            cm_val = QLabel(f"<span style='font-size: 16px; font-weight: bold; color: white;'>{len(self.sistema.mezzi)}</span>")
            cm_lbl = QLabel("<span style='color: #888; font-size: 11px;'>Mezzi in Flotta</span>")
            cm_val.setWordWrap(True)
            cm_lbl.setWordWrap(True)
            cm_lay.addWidget(cm_val)
            cm_lay.addWidget(cm_lbl)
            stats_layout.addWidget(card_m)
            
            # Stat 3: Turni
            card_t = QFrame()
            card_t.setStyleSheet("""
                .QFrame {
                    background-color: #1e1e1e;
                    border: 1px solid #333;
                    border-radius: 8px;
                }
                QLabel {
                    background-color: transparent;
                }
            """)
            card_t.setMinimumHeight(85)
            ct_lay = QVBoxLayout(card_t)
            ct_lay.setContentsMargins(10, 10, 10, 10)
            ct_lay.setSpacing(4)
            ct_val = QLabel(f"<span style='font-size: 16px; font-weight: bold; color: white;'>{len(self.sistema.turni)}</span>")
            ct_lbl = QLabel("<span style='color: #888; font-size: 11px;'>Turni Totali</span>")
            ct_val.setWordWrap(True)
            ct_lbl.setWordWrap(True)
            ct_lay.addWidget(ct_val)
            ct_lay.addWidget(ct_lbl)
            stats_layout.addWidget(card_t)
            
            scroll_layout.addWidget(stats_widget)
            
        # 4. Assigned Shifts Section (Always visible)
        title_shifts = QLabel("<h3 style='color: white; font-family: Inter, sans-serif;'>🗓️ I Miei Turni Assegnati & Dettagli:</h3>")
        scroll_layout.addWidget(title_shifts)
        
        if not self.sistema.logged_user.turni_assegnati:
            no_shift_lbl = QLabel("<p style='color: #888; font-style: italic;'>Nessun turno assegnato al momento.</p>")
            scroll_layout.addWidget(no_shift_lbl)
        else:
            for turno in self.sistema.logged_user.turni_assegnati:
                shift_card = QFrame()
                shift_card.setStyleSheet(".QFrame { background-color: #1e1e1e; border: 1px solid #333; border-radius: 6px; }")
                sc_layout = QHBoxLayout(shift_card)
                sc_layout.setContentsMargins(15, 15, 15, 15)
                
                # Left side: Date Badge
                date_layout = QVBoxLayout()
                lbl_d = QLabel(f"<span style='font-size: 15px; font-weight: bold; color: white;'>{turno.data}</span>")
                lbl_t = QLabel(f"<span style='font-size: 13px; color: #888;'>{turno.fascia_oraria}</span>")
                date_layout.addWidget(lbl_d)
                date_layout.addWidget(lbl_t)
                sc_layout.addLayout(date_layout)
                
                # Center: Service & Role Badges
                details_layout = QVBoxLayout()
                lbl_s = QLabel(f"<span style='font-size: 14px; font-weight: bold; color: #ff5252;'>{turno.tipoServizio}</span>")
                
                # Find assigned role
                v_role = turno.volontari_ruoli.get(str(self.sistema.logged_user.cod_fiscale), "Soccorritore")
                lbl_r = QLabel(f"<span style='background-color: #444; color: #ddd; padding: 3px 6px; border-radius: 4px; font-size: 11px;'>Ruolo: {v_role}</span>")
                details_layout.addWidget(lbl_s)
                details_layout.addWidget(lbl_r)
                sc_layout.addLayout(details_layout)
                
                # Right side: Hours worked / Status
                right_layout = QVBoxLayout()
                right_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                ore_eff = self.sistema.logged_user.ore_lavorate.get(turno.id_turno, 0.0)
                if ore_eff > 0:
                    lbl_status = QLabel(f"<span style='color: #00e676; font-weight: bold; font-size: 13px;'>✓ Completato ({ore_eff:.1f} h)</span>")
                else:
                    lbl_status = QLabel("<span style='color: #ffb300; font-weight: bold; font-size: 13px;'>⏳ In Attesa</span>")
                right_layout.addWidget(lbl_status)
                sc_layout.addLayout(right_layout)
                
                scroll_layout.addWidget(shift_card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget

    # --- TAB TURNI ---
    def crea_tab_turni(self, is_referente):
        from PyQt5.QtWidgets import QScrollArea, QFrame
        
        # Outer widget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(25)
        
        # Section 1: Coordinator Shift Management (Visible ONLY for Referente)
        if is_referente:
            admin_section = QWidget()
            admin_layout = QVBoxLayout(admin_section)
            admin_layout.setContentsMargins(0, 0, 0, 0)
            admin_layout.setSpacing(10)
            
            admin_layout.addWidget(QLabel("<h3 style='color: white; font-family: Inter, sans-serif;'>🛠️ Pianificazione Turni di Servizio (Gestione Referente):</h3>"))
            
            self.tbl_tutti_turni = QTableWidget(0, 8)
            self.tbl_tutti_turni.setEditTriggers(QAbstractItemView.DoubleClicked)
            # pyrefly: ignore [missing-attribute]
            self.tbl_tutti_turni.itemChanged.connect(self.on_turno_cell_changed)
            self.tbl_tutti_turni.setHorizontalHeaderLabels(["ID", "Data", "Orario", "Luogo", "Servizio", "Persone Richieste", "Iscritti", "Stato"])
            self.tbl_tutti_turni.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.tbl_tutti_turni.verticalHeader().setDefaultSectionSize(36)
            self.tbl_tutti_turni.verticalHeader().setVisible(False)
            self.tbl_tutti_turni.setMinimumHeight(200)
            admin_layout.addWidget(self.tbl_tutti_turni)
            
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(10)
            
            btn_crea = QPushButton("🆕 Crea Nuovo Turno")
            btn_crea.clicked.connect(self.azione_crea_turno)
            btn_layout.addWidget(btn_crea)
            
            btn_modifica_turno = QPushButton("✏️ Modifica Turno")
            btn_modifica_turno.clicked.connect(self.azione_modifica_turno)
            btn_layout.addWidget(btn_modifica_turno)
            
            btn_elimina = QPushButton("🗑️ Elimina Turno")
            btn_elimina.clicked.connect(self.azione_elimina_turno)
            btn_layout.addWidget(btn_elimina)
            
            admin_layout.addLayout(btn_layout)
            scroll_layout.addWidget(admin_section)
            
        # Section 2: Volunteer Booking (Visible for BOTH Referente and Volontario)
        booking_section = QWidget()
        booking_layout = QVBoxLayout(booking_section)
        booking_layout.setContentsMargins(0, 0, 0, 0)
        booking_layout.setSpacing(10)
        
        booking_layout.addWidget(QLabel("<h3 style='color: white; font-family: Inter, sans-serif;'>🔗 Turni Disponibili per l'Iscrizione:</h3>"))
        
        self.tbl_turni_disp = QTableWidget(0, 6)
        self.tbl_turni_disp.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_turni_disp.setHorizontalHeaderLabels(["ID", "Data", "Orario", "Luogo", "Servizio", "Patente Richiesta"])
        self.tbl_turni_disp.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_turni_disp.verticalHeader().setDefaultSectionSize(36)
        self.tbl_turni_disp.verticalHeader().setVisible(False)
        self.tbl_turni_disp.setMinimumHeight(150)
        booking_layout.addWidget(self.tbl_turni_disp)
        
        btn_prenota = QPushButton("🔗 Prenota Turno Selezionato")
        btn_prenota.clicked.connect(self.azione_prenota_turno)
        booking_layout.addWidget(btn_prenota)
        
        scroll_layout.addWidget(booking_section)
        
        # Section 3: Personal Assigned Shifts (Visible for BOTH Referente and Volontario)
        personal_section = QWidget()
        personal_layout = QVBoxLayout(personal_section)
        personal_layout.setContentsMargins(0, 0, 0, 0)
        personal_layout.setSpacing(10)
        
        personal_layout.addWidget(QLabel("<h3 style='color: white; font-family: Inter, sans-serif;'>📋 I Miei Turni Assegnati:</h3>"))
        
        self.tbl_miei_turni = QTableWidget(0, 6)
        self.tbl_miei_turni.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_miei_turni.setHorizontalHeaderLabels(["ID", "Data", "Orario", "Luogo", "Servizio", "Stato"])
        self.tbl_miei_turni.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_miei_turni.verticalHeader().setDefaultSectionSize(36)
        self.tbl_miei_turni.verticalHeader().setVisible(False)
        self.tbl_miei_turni.setMinimumHeight(150)
        personal_layout.addWidget(self.tbl_miei_turni)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        btn_cancella = QPushButton("❌ Annulla Assegnazione")
        btn_cancella.clicked.connect(self.azione_annulla_turno)
        actions_layout.addWidget(btn_cancella)
        
        btn_checklist = QPushButton("📋 Compila Checklist Veicolo")
        btn_checklist.clicked.connect(self.azione_compila_checklist)
        actions_layout.addWidget(btn_checklist)
        
        btn_resoconto = QPushButton("📝 Resoconto Fine Turno")
        btn_resoconto.clicked.connect(self.azione_compila_resoconto)
        actions_layout.addWidget(btn_resoconto)
        
        personal_layout.addLayout(actions_layout)
        scroll_layout.addWidget(personal_section)
        
        # Populate tables
        self.popola_tabelle_turni_volontario()
        if is_referente:
            self.popola_tabella_turni_admin()
            
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget
    def popola_tabelle_turni_volontario(self):
        # 1. Available shifts
        self.tbl_turni_disp.setRowCount(0)
        disponibili = [t for t in self.sistema.turni if t.stato in ["Proposto", "Aperto"] and not any(str(v.cod_fiscale) == str(self.sistema.logged_user.cod_fiscale) for v in t.volontari_assegnati)]
        for t in disponibili:
            row = self.tbl_turni_disp.rowCount()
            self.tbl_turni_disp.insertRow(row)
            self.tbl_turni_disp.setItem(row, 0, QTableWidgetItem(str(t.id)))
            self.tbl_turni_disp.setItem(row, 1, QTableWidgetItem(t.data))
            self.tbl_turni_disp.setItem(row, 2, QTableWidgetItem(t.fascia_oraria))
            self.tbl_turni_disp.setItem(row, 3, QTableWidgetItem(t.luogo))
            self.tbl_turni_disp.setItem(row, 4, QTableWidgetItem(t.tipoServizio))
            self.tbl_turni_disp.setItem(row, 5, QTableWidgetItem(t.patenteRichiesta))
            
        # 2. My shifts
        self.tbl_miei_turni.setRowCount(0)
        miei = self.sistema.logged_user.turni_assegnati
        for t in miei:
            row = self.tbl_miei_turni.rowCount()
            self.tbl_miei_turni.insertRow(row)
            self.tbl_miei_turni.setItem(row, 0, QTableWidgetItem(str(t.id)))
            self.tbl_miei_turni.setItem(row, 1, QTableWidgetItem(t.data))
            self.tbl_miei_turni.setItem(row, 2, QTableWidgetItem(t.fascia_oraria))
            self.tbl_miei_turni.setItem(row, 3, QTableWidgetItem(t.luogo))
            self.tbl_miei_turni.setItem(row, 4, QTableWidgetItem(t.tipoServizio))
            self.tbl_miei_turni.setItem(row, 5, QTableWidgetItem(t.stato))

    def popola_tabella_turni_admin(self):
        self.tbl_tutti_turni.blockSignals(True)
        self.tbl_tutti_turni.setRowCount(0)
        for t in self.sistema.turni:
            row = self.tbl_tutti_turni.rowCount()
            self.tbl_tutti_turni.insertRow(row)
            self.tbl_tutti_turni.setItem(row, 0, QTableWidgetItem(str(t.id)))
            self.tbl_tutti_turni.setItem(row, 1, QTableWidgetItem(t.data))
            self.tbl_tutti_turni.setItem(row, 2, QTableWidgetItem(t.fascia_oraria))
            self.tbl_tutti_turni.setItem(row, 3, QTableWidgetItem(t.luogo))
            self.tbl_tutti_turni.setItem(row, 4, QTableWidgetItem(t.tipoServizio))
            self.tbl_tutti_turni.setItem(row, 5, QTableWidgetItem(str(t.personeRichieste)))
            self.tbl_tutti_turni.setItem(row, 6, QTableWidgetItem(str(len(t.volontari_assegnati))))
            self.tbl_tutti_turni.setItem(row, 7, QTableWidgetItem(t.stato))
        self.tbl_tutti_turni.blockSignals(False)

    def azione_prenota_turno(self):
        row = self.tbl_turni_disp.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un turno da prenotare.")
            return
        id_turno = self.tbl_turni_disp.item(row, 0).text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        
        if turno:
            # Check if user is already registered for this shift
            if any(str(v.cod_fiscale) == str(self.sistema.logged_user.cod_fiscale) for v in turno.volontari_assegnati):
                QMessageBox.warning(self, "Attenzione", "Sei già prenotato per questo turno!")
                return
                
            # Richiede il ruolo all'iscrizione
            ruolo, ok = QInputDialog.getItem(
                self, 
                "Ruolo nel Turno", 
                "Seleziona il tuo ruolo per questo turno:", 
                ["Autista Tipo A", "Autista Tipo B", "Soccorritore Tipo A", "Soccorritore Tipo B"], 
                0, 
                False
            )
            if not ok or not ruolo:
                return
                
            # Verifica fabbisogno del ruolo nel turno — bloccante, nessuna eccezione
            req_count = getattr(turno, "persone_richieste", {}).get(ruolo, 0)
            booked_count = sum(1 for v in turno.volontari_assegnati if (turno.volontari_ruoli.get(str(v.cod_fiscale)) or "").strip() == ruolo)
            if booked_count >= req_count:
                QMessageBox.warning(
                    self,
                    "Ruolo Non Disponibile",
                    f"❌ Il ruolo '{ruolo}' non è più disponibile per questo turno.\n"
                    f"Il fabbisogno pianificato è già stato coperto ({booked_count}/{req_count}).\n\n"
                    "Seleziona un ruolo diverso o scegli un altro turno."
                )
                return
                    
            if "Autista" in ruolo:
                patente_richiesta = str(turno.patenteRichiesta or "").strip()
                if patente_richiesta:
                    volontario_patenti = [str(p).strip().upper() for p in (self.sistema.logged_user.patenti or [])]
                    if patente_richiesta.upper() not in volontario_patenti:
                        QMessageBox.warning(
                            self, 
                            "Patente Richiesta Mancante", 
                            f"❌ Non puoi prenotarti come Autista per questo turno.\n"
                            f"È richiesta la patente '{patente_richiesta}', ma le tue patenti registrate sono: {', '.join(volontario_patenti) or 'Nessuna'}."
                        )
                        return
            
            # Verify using Turni Controller
            self.turni_controller.prenotaTurno(turno.id, self.sistema.logged_user.cod_fiscale, ruolo)
            # Make assignments in system
            self.sistema.logged_user.prenota_turno(turno)
            turno.aggiungiVolontario(self.sistema.logged_user)
            turno.volontari_ruoli[str(self.sistema.logged_user.cod_fiscale)] = ruolo
            
            QMessageBox.information(self, "Successo", f"✅ Turno prenotato correttamente come {ruolo}!")
            self.update_ui()

    def azione_annulla_turno(self):
        row = self.tbl_miei_turni.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un turno da annullare.")
            return
        id_turno = self.tbl_miei_turni.item(row, 0).text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        
        if turno:
            # Delegate to controller
            self.turni_controller.annullaPrenotazione(turno)
            # Remove local assignment
            self.sistema.logged_user.annulla_prenotazione(turno)
            turno.rimuoviVolontario(self.sistema.logged_user)
            QMessageBox.information(self, "Successo", "❌ Prenotazione annullata.")
            self.update_ui()

    def azione_compila_checklist(self):
        row = self.tbl_miei_turni.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona il turno associato alla checklist.")
            return
            
        id_item = self.tbl_miei_turni.item(row, 0)
        if not id_item:
            return
        id_turno = id_item.text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        if not turno:
            return
            
        # Determina la targa del veicolo associato al turno
        targa = "CRI 302 AJ"
        for m in self.sistema.mezzi:
            if any(str(t.id) == str(turno.id) for t in m.turni_assegnati):
                targa = m.targa
                break
                
        # Legge il ruolo inserito all'iscrizione
        ruolo = turno.volontari_ruoli.get(str(self.sistema.logged_user.cod_fiscale))
        if not ruolo:
            # Fallback se non trovato
            ruolo, ok = QInputDialog.getItem(
                self, 
                "Ruolo nel Turno", 
                "Seleziona il tuo ruolo per compilare la checklist:", 
                ["Autista Tipo A", "Autista Tipo B", "Soccorritore Tipo A", "Soccorritore Tipo B"], 
                0, 
                False
            )
            if not ok or not ruolo:
                return
            
        # Inizializza l'oggetto checklist se non presente
        if not hasattr(turno, 'checklist_obj') or not turno.checklist_obj:
            turno.checklist_obj = Checklist(
                id=f"CL_{turno.id}",
                controlliMeccanici=False,
                dispositiviMediciRichiesti=["Defibrillatore", "Barella"],
                dispositiviPresenti=False
            )
            
        self.flotta_controller.compilaChecklist(turno.checklist_obj)
        
        # Apri il Wizard specifico per il ruolo e veicolo
        dialog = CompilaChecklistDialog(turno.checklist_obj, ruolo, targa, self)
        if dialog.exec_():
            self.update_ui()

    def azione_compila_resoconto(self):
        row = self.tbl_miei_turni.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona il turno da completare.")
            return
        id_turno = self.tbl_miei_turni.item(row, 0).text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        
        if turno:
            dialog = CompilaResocontoDialog()
            if dialog.exec_():
                km, ore, note = dialog.get_dati()
                
                # Update model
                self.sistema.logged_user.compila_report_turno(turno, float(ore))
                turno.cambia_stato("Concluso")
                
                # Save using Fleet controller
                r = Report(id="REP_" + str(turno.id), kmPercorsi=km, noteIntervento=note, oreEffettive=ore)
                self.flotta_controller.salvaReport(r)
                
                QMessageBox.information(self, "Successo", f"✅ Resoconto registrato. Ore inserite nel libretto: {ore} ore.")
                self.update_ui()

    def azione_crea_turno(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        dialog = CreaTurnoDialog()
        if dialog.exec_():
            t = dialog.get_turno()
            self.turni_controller.creaTurno(t)
            self.sistema.aggiungi_turno(t)
            QMessageBox.information(self, "Successo", "✅ Nuovo turno creato e pubblicato nel catalogo.")
            self.update_ui()

    def azione_elimina_turno(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        row = self.tbl_tutti_turni.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un turno da eliminare.")
            return
        id_turno = self.tbl_tutti_turni.item(row, 0).text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        
        if turno:
            self.turni_controller.annullaPrenotazione(turno)
            self.sistema.turni.remove(turno)
            QMessageBox.information(self, "Successo", "🗑️ Turno rimosso.")
            self.update_ui()

    # --- TAB FLOTTA ---
    def crea_tab_flotta(self, is_referente):
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>Stato Veicoli Flotta Croce Rossa:</b>"))
        self.tbl_mezzi = QTableWidget(0, 5)
        if is_referente:
            self.tbl_mezzi.setEditTriggers(QAbstractItemView.DoubleClicked)
            # pyrefly: ignore [missing-attribute]
            self.tbl_mezzi.itemChanged.connect(self.on_mezzo_cell_changed)
        else:
            self.tbl_mezzi.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_mezzi.setHorizontalHeaderLabels(["Targa", "Tipo", "Stato", "Chilometri", "Disponibilità"])
        self.tbl_mezzi.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_mezzi.verticalHeader().setDefaultSectionSize(36)
        self.tbl_mezzi.verticalHeader().setVisible(False)
        layout.addWidget(self.tbl_mezzi)
        
        if is_referente:
            btn_layout = QHBoxLayout()
            btn_aggiungi = QPushButton("🚐 Aggiungi Nuovo Mezzo")
            btn_aggiungi.clicked.connect(self.azione_aggiungi_mezzo)
            btn_layout.addWidget(btn_aggiungi)
            
            btn_officina = QPushButton("🔧 Invia in Officina")
            btn_officina.clicked.connect(self.azione_invia_officina)
            btn_layout.addWidget(btn_officina)
            
            btn_ripara = QPushButton("🟢 Termina Riparazione")
            btn_ripara.clicked.connect(self.azione_fine_riparazione)
            btn_layout.addWidget(btn_ripara)
            
            btn_modifica_mezzo = QPushButton("✏️ Modifica Mezzo")
            btn_modifica_mezzo.clicked.connect(self.azione_modifica_mezzo)
            btn_layout.addWidget(btn_modifica_mezzo)
            
            btn_radia = QPushButton("🗑️ Radia Mezzo")
            btn_radia.clicked.connect(self.azione_radia_veicolo)
            btn_layout.addWidget(btn_radia)
            
            layout.addLayout(btn_layout)
            
        self.popola_tabella_mezzi()
        widget.setLayout(layout)
        return widget

    def popola_tabella_mezzi(self):
        self.tbl_mezzi.blockSignals(True)
        self.tbl_mezzi.setRowCount(0)
        for m in self.sistema.mezzi:
            row = self.tbl_mezzi.rowCount()
            self.tbl_mezzi.insertRow(row)
            self.tbl_mezzi.setItem(row, 0, QTableWidgetItem(m.targa))
            self.tbl_mezzi.setItem(row, 1, QTableWidgetItem(m.tipo))
            self.tbl_mezzi.setItem(row, 2, QTableWidgetItem(m.stato))
            self.tbl_mezzi.setItem(row, 3, QTableWidgetItem(str(m.chilometraggioTotale) + " km"))
            disp_str = "Disponibile" if m.disponibile else "Non Disponibile"
            self.tbl_mezzi.setItem(row, 4, QTableWidgetItem(disp_str))
        self.tbl_mezzi.blockSignals(False)

    def azione_aggiungi_mezzo(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        dialog = CreaMezzoDialog()
        if dialog.exec_():
            m = dialog.get_mezzo()
            self.flotta_controller.aggiungiMezzo(m)
            self.sistema.aggiungi_mezzo(m)
            QMessageBox.information(self, "Successo", "✅ Nuovo veicolo aggiunto alla flotta.")
            self.update_ui()

    def azione_invia_officina(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        row = self.tbl_mezzi.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un mezzo.")
            return
        targa = self.tbl_mezzi.item(row, 0).text()
        m = next((mezzo for mezzo in self.sistema.mezzi if mezzo.targa == targa), None)
        if m:
            m.inviaInOfficina()
            self.flotta_controller.aggiungiMezzo(m)
            QMessageBox.information(self, "Flotta", f"🔧 Il veicolo {m.targa} è stato inviato in riparazione.")
            self.update_ui()

    def azione_fine_riparazione(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        row = self.tbl_mezzi.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un mezzo.")
            return
        targa = self.tbl_mezzi.item(row, 0).text()
        m = next((mezzo for mezzo in self.sistema.mezzi if mezzo.targa == targa), None)
        if m:
            m.fineRiparazione()
            self.flotta_controller.aggiungiMezzo(m)
            QMessageBox.information(self, "Flotta", f"🟢 Il veicolo {m.targa} è ora disponibile per i turni.")
            self.update_ui()

    def azione_radia_veicolo(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        row = self.tbl_mezzi.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un mezzo.")
            return
        targa = self.tbl_mezzi.item(row, 0).text()
        m = next((mezzo for mezzo in self.sistema.mezzi if mezzo.targa == targa), None)
        if m:
            m.radiazioneVeicolo()
            self.flotta_controller.aggiungiMezzo(m)
            QMessageBox.information(self, "Flotta", f"🗑️ Il veicolo {m.targa} è stato radiato.")
            self.update_ui()

    # --- TAB FORMAZIONE ---
    def crea_tab_formazione(self, is_referente):
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>Certificazioni e Corsi Formativi Croce Rossa:</b>"))
        self.tbl_corsi = QTableWidget(0, 5)
        if is_referente:
            self.tbl_corsi.setEditTriggers(QAbstractItemView.DoubleClicked)
            # pyrefly: ignore [missing-attribute]
            self.tbl_corsi.itemChanged.connect(self.on_corso_cell_changed)
        else:
            self.tbl_corsi.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_corsi.setHorizontalHeaderLabels(["ID", "Titolo", "Data Inizio", "Data Fine", "Stato"])
        self.tbl_corsi.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_corsi.verticalHeader().setDefaultSectionSize(36)
        self.tbl_corsi.verticalHeader().setVisible(False)
        layout.addWidget(self.tbl_corsi)
        
        if not is_referente:
            btn_iscrivi = QPushButton("🎓 Iscriviti al Corso Selezionato")
            btn_iscrivi.clicked.connect(self.azione_iscrivi_corso)
            layout.addWidget(btn_iscrivi)
        else:
            btn_layout = QHBoxLayout()
            btn_crea = QPushButton("🎓 Crea Nuovo Corso")
            btn_crea.clicked.connect(self.azione_crea_corso)
            btn_layout.addWidget(btn_crea)
            
            btn_modifica_corso = QPushButton("✏️ Modifica Corso")
            btn_modifica_corso.clicked.connect(self.azione_modifica_corso)
            btn_layout.addWidget(btn_modifica_corso)
            
            btn_attesta = QPushButton("🏆 Attesta Certificazione Volontario")
            btn_attesta.clicked.connect(self.azione_attesta_partecipazione)
            btn_layout.addWidget(btn_attesta)
            layout.addLayout(btn_layout)
            
        self.popola_tabella_corsi()
        widget.setLayout(layout)
        return widget

    def popola_tabella_corsi(self):
        self.tbl_corsi.blockSignals(True)
        self.tbl_corsi.setRowCount(0)
        for c in self.sistema.corsi:
            row = self.tbl_corsi.rowCount()
            self.tbl_corsi.insertRow(row)
            self.tbl_corsi.setItem(row, 0, QTableWidgetItem(c.id))
            self.tbl_corsi.setItem(row, 1, QTableWidgetItem(c.titolo))
            self.tbl_corsi.setItem(row, 2, QTableWidgetItem(c.dataInizio))
            self.tbl_corsi.setItem(row, 3, QTableWidgetItem(c.dataFine))
            self.tbl_corsi.setItem(row, 4, QTableWidgetItem(c.stato))
        self.tbl_corsi.blockSignals(False)

    def azione_iscrivi_corso(self):
        row = self.tbl_corsi.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un corso.")
            return
        id_corso = self.tbl_corsi.item(row, 0).text()
        c = next((corso for corso in self.sistema.corsi if corso.id == id_corso), None)
        
        if c:
            # Check if user is already enrolled or has completed this course
            if any(corso.id == c.id for corso in self.sistema.logged_user.formazione) or \
               any(corso.id == c.id for corso in self.sistema.logged_user.corsi_frequentati):
                QMessageBox.warning(self, "Attenzione", "Sei già iscritto o hai già completato questo corso!")
                return
            self.formazione_controller.iscriviVolontario(self.sistema.logged_user, c.id)
            self.sistema.logged_user.iscriviti_al_corso(c)
            QMessageBox.information(self, "Formazione", f"✅ Richiesta iscrizione inviata per: {c.titolo}")
            self.update_ui()

    def azione_crea_corso(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        dialog = CreaCorsoDialog()
        if dialog.exec_():
            c = dialog.get_corso()
            self.formazione_controller.creaCorso(c)
            self.sistema.aggiungi_corso(c)
            QMessageBox.information(self, "Successo", "✅ Corso aggiunto al catalogo di formazione.")
            self.update_ui()

    def azione_attesta_partecipazione(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        row = self.tbl_corsi.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un corso.")
            return
        id_corso = self.tbl_corsi.item(row, 0).text()
        c = next((corso for corso in self.sistema.corsi if corso.id == id_corso), None)
        
        if c:
            # Let selection of user
            nomi = [v.get_nome_completo() for v in self.sistema.volontari if v.ruolo.lower() == "volontario"]
            item, ok = QInputDialog.getItem(self, "Seleziona Volontario", "Scegli il volontario da certificare:", nomi, 0, False)
            if ok and item:
                volontario = next((v for v in self.sistema.volontari if v.get_nome_completo() == item), None)
                if volontario:
                    self.formazione_controller.attestaPartecipazione(c.id, [volontario])
                    volontario.corsi_frequentati.append(c)
                    volontario.aggiungiQualifica(c.titolo)
                    volontario.aggiorna_firestore()
                    QMessageBox.information(self, "Successo", f"🏆 Brevetto / Qualifica '{c.titolo}' rilasciato a {volontario.get_nome_completo()}!")
                    self.update_ui()


    def azione_modifica_turno(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        row = self.tbl_tutti_turni.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un turno dalla lista.")
            return
        id_turno = self.tbl_tutti_turni.item(row, 0).text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        if not turno:
            return
        dialog = ModificaTurnoDialog(turno, self)
        if dialog.exec_():
            dialog.apply_to(turno)
            turno.aggiorna_firestore()
            QMessageBox.information(self, "Successo", f"✅ Turno {turno.id} aggiornato correttamente.")
            self.update_ui()

    def azione_modifica_mezzo(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        row = self.tbl_mezzi.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un mezzo dalla lista.")
            return
        targa = self.tbl_mezzi.item(row, 0).text()
        mezzo = next((m for m in self.sistema.mezzi if m.targa == targa), None)
        if not mezzo:
            return
        dialog = ModificaMezzoDialog(mezzo, self)
        if dialog.exec_():
            dialog.apply_to(mezzo)
            mezzo.aggiorna_firestore()
            QMessageBox.information(self, "Successo", f"✅ Mezzo {mezzo.targa} aggiornato correttamente.")
            self.update_ui()

    def azione_modifica_corso(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        row = self.tbl_corsi.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un corso dalla lista.")
            return
        id_corso = self.tbl_corsi.item(row, 0).text()
        corso = next((c for c in self.sistema.corsi if c.id == id_corso), None)
        if not corso:
            return
        dialog = ModificaCorsoDialog(corso, self)
        if dialog.exec_():
            dialog.apply_to(corso)
            corso.aggiorna_firestore()
            QMessageBox.information(self, "Successo", f"✅ Corso '{corso.titolo}' aggiornato correttamente.")
            self.update_ui()

    def modifica_dati_volontario(self):
        dialog = ModificaDatiDialog(self.sistema.logged_user)
        if dialog.exec_():
            self.update_ui()

    def on_turno_cell_changed(self, item):
        if getattr(self, '_populating', False):
            return
        row = item.row()
        col = item.column()
        if col == 0 or col == 6: # ID or Iscritti cannot be edited
            return
        id_item = self.tbl_tutti_turni.item(row, 0)
        if not id_item:
            return
        id_turno = id_item.text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        if not turno:
            return
            
        new_val = item.text().strip()
        if col == 1:
            turno.data = new_val
        elif col == 2:
            turno.fascia_oraria = new_val
        elif col == 3:
            turno.luogo = new_val
        elif col == 4:
            turno.tipoServizio = new_val
        elif col == 5:
            try:
                turno.personeRichieste = int(new_val)
            except ValueError:
                QMessageBox.warning(self, "Errore", "Persone richieste deve essere un numero intero.")
                self.popola_tabella_turni_admin()
                return
        elif col == 7:
            turno.stato = new_val
            
        try:
            turno.aggiorna_firestore()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile salvare le modifiche su Firebase: {e}")
            self.popola_tabella_turni_admin()

    def on_mezzo_cell_changed(self, item):
        if getattr(self, '_populating', False):
            return
        row = item.row()
        col = item.column()
        targa_item = self.tbl_mezzi.item(row, 0)
        if not targa_item:
            return
        targa = targa_item.text()
        mezzo = next((m for m in self.sistema.mezzi if m.targa == targa), None)
        if not mezzo:
            return
            
        new_val = item.text().strip()
        if col == 0:
            QMessageBox.warning(self, "Errore", "La targa non può essere modificata direttamente.")
            self.popola_tabella_mezzi()
            return
        elif col == 1:
            mezzo.tipo = new_val
        elif col == 2:
            mezzo.stato = new_val
        elif col == 3:
            new_val_clean = new_val.replace(" km", "").strip()
            try:
                mezzo.chilometraggioTotale = float(new_val_clean)
            except ValueError:
                QMessageBox.warning(self, "Errore", "Il chilometraggio deve essere un numero.")
                self.popola_tabella_mezzi()
                return
        elif col == 4:
            mezzo.disponibile = (new_val.lower() in ["sì", "si", "true", "yes", "ok"])
            
        try:
            mezzo.aggiorna_firestore()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile salvare su Firebase: {e}")
            self.popola_tabella_mezzi()

    def on_corso_cell_changed(self, item):
        if getattr(self, '_populating', False):
            return
        row = item.row()
        col = item.column()
        if col == 0:
            return
        id_item = self.tbl_corsi.item(row, 0)
        if not id_item:
            return
        id_corso = id_item.text()
        corso = next((c for c in self.sistema.corsi if c.id == id_corso), None)
        if not corso:
            return
            
        new_val = item.text().strip()
        if col == 1:
            corso.titolo = new_val
        elif col == 2:
            corso.dataInizio = new_val
        elif col == 3:
            corso.dataFine = new_val
        elif col == 4:
            corso.stato = new_val
            
        try:
            corso.aggiorna_firestore()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile salvare su Firebase: {e}")
            self.popola_tabella_corsi()

    def setup_sistema(self):
        sistema = Sistema()

        referente = Referente(
            cod_fiscale=1,
            nome="Luca",
            cognome="Rossi",
            email="luca.rossi@example.com",
            nascita="1980-03-15",
            telefono="1234567890",
            curriculum="curriculum.pdf",
            patenti=["B"],
            formazione=[],
            compagnia_appartenenza="CRI Roma",
            disponibilita=["Lunedì", "Venerdì"],
            area_gestita="Formazione"
        )

        volontario = Volontario(
            cod_fiscale=2,
            nome="Anna",
            cognome="Verdi",
            email="anna.verdi@example.com",
            nascita="1995-07-10",
            telefono="0987654321",
            curriculum="cv_anna.pdf",
            patenti=["B"],
            formazione=[],
            compagnia_appartenenza="CRI Roma",
            disponibilita=["Lunedì", "Mercoledì"],
            ruolo="volontario"
        )

        sistema.assegna_referente(volontario.cod_fiscale, referente.cod_fiscale)
        sistema.aggiungi_volontario(referente)
        sistema.aggiungi_volontario(volontario)

        mezzo = Mezzo(
            targa="AB123CD",
            tipo="Ambulanza",
            chilometraggio=50000,
            stato="Pulito, Revisione OK",
            dispositivi_richiesti=["Defibrillatore", "Barelle"],
            checklist=["Controllo olio", "Presenza DPI"]
        )
        sistema.aggiungi_mezzo(mezzo)

        corso = Corso(
            id="C01",
            titolo="Trauma Base",
            nome="Trauma Base",
            dataInizio="2025-09-01",
            esito=False,
            dataFine="2025-09-15",
            checklist=[
                {"item": "Materiale consegnato", "completato": False},
                {"item": "Firma partecipanti", "completato": False}
            ],
            scadenza="2026-09-01"
        )
        sistema.aggiungi_corso(corso)
        sistema.carica_corso_al_volontario(volontario.cod_fiscale, corso)
        referente.attesta_partecipazione(volontario, corso)

        turno = Turno(
            id_turno=301,
            data="2025-09-10",
            fascia_oraria="08:00 - 14:00",
            tipoServizio="A",
            personeRichieste=1,
            checklist=False,
            luogo="CRI Roma",
            paziente="Mario Rossi",
            tempoExtra="30 min",
            dispositivi_richiesti=["Defibrillatore"],
            corso_richiesto="Trauma Base"
        )
        sistema.aggiungi_turno(turno)
        sistema.assegna_turno(volontario.cod_fiscale, turno)
        sistema.assegna_mezzo_a_turno(mezzo, turno)
        turno.completa_checklist()
        turno.cambia_stato("Confermato")
        volontario.compila_report_turno(turno, 6.0)

        return sistema
