# type: ignore
# layout/MainWindow.py
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QFormLayout, QLineEdit, QComboBox, QDialog, QCheckBox, QInputDialog,
    QAbstractItemView, QFrame, QTextEdit, QFileDialog, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from Sistema import Sistema
from Referente import Referente
from Volontario import Volontario
from Mezzo import Mezzo
from Turno import Turno
from Corso import Corso
from Checklist import Checklist
from Report import Report
from layout.modifica_dati_dialog import ModificaDatiDialog
from layout.dettaglio_corso_dialog import DettaglioCorsoDialog

# Importing controllers for business logic delegation
from GestioneUtenteController import GestioneUtenteController
from GestioneFlottaController import GestioneFlottaController
from GestioneTurniController import GestioneTurniController
from GestioneFormazioneController import GestioneFormazioneController

class CreaTurnoDialog(QDialog):
    def __init__(self, mezzi=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🆕 Crea Nuovo Turno")
        self.mezzi_list = list(mezzi) if mezzi else []
        layout = QFormLayout()
        
        from PyQt5.QtWidgets import QSpinBox
        
        import uuid
        self.generated_id = str(uuid.uuid4())[:8].upper()
        self.id_edit = QLineEdit(self.generated_id)
        self.id_edit.setReadOnly(True)
        self.data_edit = QLineEdit("2026-07-15")
        self.luogo_prelevamento_edit = QLineEdit("Sede Centrale CRI")
        self.luogo_destinazione_edit = QLineEdit("Ospedale Regionale")
        self.ora_inizio_edit = QLineEdit("08:00")
        self.ora_fine_edit = QLineEdit("14:00")
        self.patente_combo = QComboBox()
        self.patente_combo.addItems(["Nessuna", "B", "C", "D", "E"])
        self.patente_combo.setCurrentText("B")
        self.paziente_nome_edit = QLineEdit("")
        self.paziente_cf_edit = QLineEdit("")

        # Mezzo selection combo
        self.mezzo_combo = QComboBox()
        self.mezzo_combo.addItem("⚪ Nessun mezzo assegnato (Da assegnare)", "")
        for m in self.mezzi_list:
            disp_tag = "🟢 Disponibile" if m.disponibile else f"🟡 {m.stato}"
            self.mezzo_combo.addItem(f"🚑 {m.targa} — {m.tipo} ({disp_tag})", m.targa)
        
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
        layout.addRow("Luogo Prelevamento:", self.luogo_prelevamento_edit)
        layout.addRow("Luogo Destinazione:", self.luogo_destinazione_edit)
        layout.addRow("Ora Inizio:", self.ora_inizio_edit)
        layout.addRow("Ora Fine:", self.ora_fine_edit)
        layout.addRow("Veicolo Assegnato:", self.mezzo_combo)
        layout.addRow("Patente Richiesta:", self.patente_combo)
        layout.addRow("Nome/Cognome Paziente:", self.paziente_nome_edit)
        layout.addRow("Codice Fiscale Paziente:", self.paziente_cf_edit)
        
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
        
    def get_selected_targa(self) -> str:
        return self.mezzo_combo.currentData() or ""

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
            luogoPrelevamento=self.luogo_prelevamento_edit.text().strip(),
            luogoDestinazione=self.luogo_destinazione_edit.text().strip(),
            oraInizio=self.ora_inizio_edit.text().strip(),
            oraFine=self.ora_fine_edit.text().strip(),
            patenteRichiesta=pat_val,
            paziente_nome=self.paziente_nome_edit.text().strip(),
            paziente_cf=self.paziente_cf_edit.text().strip(),
            personeRichieste=tot_persone,
            tipoServizio=self.servizio_edit.text().strip(),
            mezzo_targa=self.get_selected_targa()
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
        from PyQt5.QtWidgets import QSpinBox
        self.setWindowTitle("🎓 Crea Nuovo Corso Formativo")
        layout = QFormLayout()
        
        import uuid
        self.generated_id = str(uuid.uuid4())[:8].upper()
        self.id_edit = QLineEdit(self.generated_id)
        self.id_edit.setReadOnly(True)
        self.titolo_edit = QLineEdit("Corso BLSD")
        self.direttore_edit = QLineEdit("Dott. M. Rossi")
        self.luogo_edit = QLineEdit("Sede Centrale CRI")
        self.orari_edit = QLineEdit("Sabato 09:00 - 18:00")
        self.inizio_edit = QLineEdit("2026-10-01")
        self.fine_edit = QLineEdit("2026-10-15")
        self.mesi_edit = QLineEdit("24")
        self.qualifica_edit = QLineEdit("Certificazione BLSD")
        self.requisiti_edit = QLineEdit("Volontario attivo CRI")
        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 100)
        self.max_spin.setValue(20)
        
        layout.addRow("ID Corso (Generato):", self.id_edit)
        layout.addRow("Titolo Corso:", self.titolo_edit)
        layout.addRow("Direttore del Corso:", self.direttore_edit)
        layout.addRow("Luogo di Svolgimento:", self.luogo_edit)
        layout.addRow("Orari del Corso:", self.orari_edit)
        layout.addRow("Data Inizio:", self.inizio_edit)
        layout.addRow("Data Fine:", self.fine_edit)
        layout.addRow("Mesi Validità:", self.mesi_edit)
        layout.addRow("Qualifica Rilasciata:", self.qualifica_edit)
        layout.addRow("Requisiti Iscrizione:", self.requisiti_edit)
        layout.addRow("Capienza Massima (Posti):", self.max_spin)
        
        self.btn = QPushButton("Crea")
        self.btn.clicked.connect(self.accept)
        layout.addRow(self.btn)
        self.setLayout(layout)
        
    def get_corso(self) -> Corso:
        return Corso(
            id=self.generated_id,
            titolo=self.titolo_edit.text().strip(),
            direttore=self.direttore_edit.text().strip(),
            luogo=self.luogo_edit.text().strip(),
            orari=self.orari_edit.text().strip(),
            dataInizio=self.inizio_edit.text().strip(),
            dataFine=self.fine_edit.text().strip(),
            mesiValidita=int(self.mesi_edit.text().strip() or 12),
            qualificaRilasciata=self.qualifica_edit.text().strip(),
            requisitiIscrizione=self.requisiti_edit.text().strip(),
            maxPartecipanti=self.max_spin.value()
        )

class ModificaTurnoDialog(QDialog):
    def __init__(self, turno, mezzi=None, parent=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import QSpinBox
        self.setWindowTitle(f"✏️ Modifica Turno — {turno.id}")
        self.setMinimumWidth(440)
        self.mezzi_list = list(mezzi) if mezzi else []
        self.turno = turno
        layout = QFormLayout()

        self.data_edit = QLineEdit(turno.data)
        self.luogo_prelevamento_edit = QLineEdit(getattr(turno, "luogoPrelevamento", "") or turno.luogo)
        self.luogo_destinazione_edit = QLineEdit(getattr(turno, "luogoDestinazione", "") or turno.luogo)
        self.ora_inizio_edit = QLineEdit(turno.oraInizio)
        self.ora_fine_edit = QLineEdit(turno.oraFine)
        self.servizio_edit = QLineEdit(turno.tipoServizio)
        self.paziente_nome_edit = QLineEdit(getattr(turno, "paziente_nome", "") or getattr(turno, "paziente", ""))
        self.paziente_cf_edit = QLineEdit(getattr(turno, "paziente_cf", ""))

        # Mezzo selection
        self.mezzo_combo = QComboBox()
        self.mezzo_combo.addItem("⚪ Nessun mezzo assegnato (Da assegnare)", "")
        cur_targa = getattr(turno, "mezzo_targa", "") or (turno.mezzo.targa if getattr(turno, "mezzo", None) else "")
        selected_idx = 0
        for idx, m in enumerate(self.mezzi_list):
            is_current = (m.targa == cur_targa)
            tag = "🔹 (Attuale)" if is_current else ("🟢 Disp." if m.disponibile else f"🟡 {m.stato}")
            self.mezzo_combo.addItem(f"🚑 {m.targa} — {m.tipo} [{tag}]", m.targa)
            if is_current:
                selected_idx = idx + 1
        self.mezzo_combo.setCurrentIndex(selected_idx)

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
        layout.addRow("Luogo Prelevamento:", self.luogo_prelevamento_edit)
        layout.addRow("Luogo Destinazione:", self.luogo_destinazione_edit)
        layout.addRow("Ora Inizio:", self.ora_inizio_edit)
        layout.addRow("Ora Fine:", self.ora_fine_edit)
        layout.addRow("Veicolo Assegnato:", self.mezzo_combo)
        layout.addRow("Tipo Servizio:", self.servizio_edit)
        layout.addRow("Nome/Cognome Paziente:", self.paziente_nome_edit)
        layout.addRow("Codice Fiscale Paziente:", self.paziente_cf_edit)
        layout.addRow("Patente Richiesta:", self.patente_combo)
        layout.addRow("Stato:", self.stato_combo)
        layout.addRow(QLabel("<i>Fabbisogno per ruolo:</i>"))
        layout.addRow(" - Autista Tipo A:", self.req_autista_a)
        layout.addRow(" - Autista Tipo B:", self.req_autista_b)
        layout.addRow(" - Soccorritore Tipo A:", self.req_soccorritore_a)
        layout.addRow(" - Soccorritore Tipo B:", self.req_soccorritore_b)

        # Gestione ruoli operativi per i volontari attualmente iscritti
        self.volontari_ruoli_combos = {}
        if getattr(turno, "volontari_assegnati", []):
            layout.addRow(QLabel("<br><b>👥 Volontari Iscritti & Ruolo Spettante:</b>"))
            for v in turno.volontari_assegnati:
                combo_v = QComboBox()
                combo_v.addItems(["Autista Tipo A", "Autista Tipo B", "Soccorritore Tipo A", "Soccorritore Tipo B"])
                cur_r = ""
                for k_cf, r_v in getattr(turno, "volontari_ruoli", {}).items():
                    if k_cf.strip().upper() == str(v.cod_fiscale).strip().upper():
                        cur_r = r_v
                        break
                if not cur_r:
                    cur_r = "Autista Tipo A" if "Emergenza" in getattr(turno, "tipoServizio", "") else "Soccorritore Tipo B"
                combo_v.setCurrentText(cur_r)
                self.volontari_ruoli_combos[str(v.cod_fiscale)] = combo_v
                layout.addRow(f" • {v.get_nome_completo()}:", combo_v)

        btn = QPushButton("💾 Salva Modifiche")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)
        self.setLayout(layout)

    def apply_to(self, turno, flotta_controller=None, mezzi=None):
        turno.data = self.data_edit.text().strip()
        turno.luogoPrelevamento = self.luogo_prelevamento_edit.text().strip()
        turno.luogoDestinazione = self.luogo_destinazione_edit.text().strip()
        pat = self.patente_combo.currentText()
        turno.patenteRichiesta = "" if pat == "Nessuna" else pat
        turno.paziente_nome = self.paziente_nome_edit.text().strip()
        turno.paziente_cf = self.paziente_cf_edit.text().strip()
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

        # Aggiorna ruoli dei volontari
        if not hasattr(turno, "volontari_ruoli") or turno.volontari_ruoli is None:
            turno.volontari_ruoli = {}
        for cf, combo in self.volontari_ruoli_combos.items():
            turno.volontari_ruoli[cf] = combo.currentText()

        nuova_targa = self.mezzo_combo.currentData() or ""
        vecchia_targa = getattr(turno, "mezzo_targa", "") or (turno.mezzo.targa if getattr(turno, "mezzo", None) else "")
        if nuova_targa != vecchia_targa:
            mezzi_list = mezzi if mezzi is not None else self.mezzi_list
            nuovo_mezzo = next((m for m in mezzi_list if m.targa == nuova_targa), None) if nuova_targa else None
            if flotta_controller:
                flotta_controller.assegnaMezzoATurno(nuovo_mezzo, turno)
            else:
                if nuovo_mezzo:
                    turno.assegna_mezzo(nuovo_mezzo)
                else:
                    turno.rimuovi_mezzo()
        
        try:
            turno.aggiorna_firestore()
        except Exception as e:
            print(f"⚠️ Errore aggiornamento turno in Firestore: {e}")


class AssegnaMezzoDialog(QDialog):
    def __init__(self, mezzi, turni, preselected_mezzo=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔗 Assegna Mezzo a Turno")
        self.setMinimumWidth(480)
        self.mezzi = list(mezzi)
        self.turni = list(turni)
        layout = QFormLayout()

        self.mezzo_combo = QComboBox()
        sel_m_idx = 0
        for idx, m in enumerate(self.mezzi):
            disp = "🟢 Disponibile" if m.disponibile else f"🟡 {m.stato}"
            self.mezzo_combo.addItem(f"🚑 {m.targa} — {m.tipo} [{disp}]", m.targa)
            if preselected_mezzo and m.targa == preselected_mezzo.targa:
                sel_m_idx = idx
        self.mezzo_combo.setCurrentIndex(sel_m_idx)

        self.turno_combo = QComboBox()
        self.turno_combo.addItem("⚪ Nessun turno (Libera / non assegnare)", "")
        for t in self.turni:
            current_m = f" (Mezzo: {t.mezzo_targa})" if getattr(t, "mezzo_targa", "") else " (Senza mezzo)"
            self.turno_combo.addItem(f"📅 {t.data} [{t.fascia_oraria}] — {t.tipoServizio} ({t.luogo}){current_m}", str(t.id))

        layout.addRow("Seleziona Veicolo:", self.mezzo_combo)
        layout.addRow("Assegna al Turno:", self.turno_combo)

        btn_box = QHBoxLayout()
        btn_ok = QPushButton("✅ Assegna Veicolo")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Annulla")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addRow(btn_box)

        self.setLayout(layout)

    def get_selected(self):
        targa = self.mezzo_combo.currentData()
        turno_id = self.turno_combo.currentData()
        mezzo = next((m for m in self.mezzi if m.targa == targa), None) if targa else None
        turno = next((t for t in self.turni if str(t.id) == turno_id), None) if turno_id else None
        return mezzo, turno


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
        from PyQt5.QtWidgets import QSpinBox
        self.setWindowTitle(f"✏️ Modifica Corso — {corso.titolo}")
        self.setMinimumWidth(400)
        layout = QFormLayout()

        self.titolo_edit = QLineEdit(corso.titolo)
        self.direttore_edit = QLineEdit(getattr(corso, "direttore", ""))
        self.luogo_edit = QLineEdit(getattr(corso, "luogo", ""))
        self.orari_edit = QLineEdit(getattr(corso, "orari", ""))
        self.inizio_edit = QLineEdit(corso.dataInizio)
        self.fine_edit = QLineEdit(corso.dataFine)
        self.mesi_edit = QLineEdit(str(getattr(corso, "mesiValidita", 24)))
        self.qualifica_edit = QLineEdit(getattr(corso, "qualificaRilasciata", ""))
        self.requisiti_edit = QLineEdit(getattr(corso, "requisitiIscrizione", ""))
        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 100)
        self.max_spin.setValue(int(getattr(corso, "maxPartecipanti", 20) or 20))

        self.stato_combo = QComboBox()
        self.stato_combo.addItems(["Pianificato", "Aperto", "In Corso", "Concluso", "Annullato"])
        self.stato_combo.setCurrentText(corso.stato or "Pianificato")

        layout.addRow("Titolo Corso:", self.titolo_edit)
        layout.addRow("Direttore del Corso:", self.direttore_edit)
        layout.addRow("Luogo di Svolgimento:", self.luogo_edit)
        layout.addRow("Orari del Corso:", self.orari_edit)
        layout.addRow("Data Inizio:", self.inizio_edit)
        layout.addRow("Data Fine:", self.fine_edit)
        layout.addRow("Mesi Validità:", self.mesi_edit)
        layout.addRow("Qualifica Rilasciata:", self.qualifica_edit)
        layout.addRow("Requisiti Iscrizione:", self.requisiti_edit)
        layout.addRow("Capienza Massima (Posti):", self.max_spin)
        layout.addRow("Stato:", self.stato_combo)

        btn = QPushButton("💾 Salva Modifiche")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)
        self.setLayout(layout)

    def apply_to(self, corso):
        corso.titolo = self.titolo_edit.text().strip()
        corso.direttore = self.direttore_edit.text().strip()
        corso.luogo = self.luogo_edit.text().strip()
        corso.orari = self.orari_edit.text().strip()
        corso.dataInizio = self.inizio_edit.text().strip()
        corso.dataFine = self.fine_edit.text().strip()
        try:
            corso.mesiValidita = int(self.mesi_edit.text().strip())
        except ValueError:
            pass
        corso.qualificaRilasciata = self.qualifica_edit.text().strip()
        corso.requisitiIscrizione = self.requisiti_edit.text().strip()
        corso.maxPartecipanti = self.max_spin.value()
        corso.stato = self.stato_combo.currentText()


class CompilaChecklistDialog(QDialog):
    """
    Dialog per la compilazione della checklist operativa di fine turno.
    Fedele al mockup e ai diagrammi di sequenza SD_CompilaChecklist (Model Report):
    - Ogni ruolo (Autista A, Autista B, Soccorritore A, Soccorritore B) ha la sua specifica checklist.
    - Layout identico al mockup: Intestazione Utente + Ruolo, riga rossa divisoria, Categoria, Voce e pulsanti OK/KO o Scelta (Pieno, 3/4, 1/2, Riserva).
    - Navigazione passo-passo con pulsante 'Prossimo'.
    - Verifica idoneità finale: notifica anomalia se sono presenti KO o conferma di idoneità.
    """
    def __init__(self, checklist: Checklist, ruolo: str, utente_nome: str = "Mario Rossi", targa: str = "CRI 302 AJ", flotta_controller=None, turno=None, mezzi_disponibili=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 Checklist Operativa di Fine Turno - Croce Rossa Italiana")
        self.resize(540, 600)
        self.setStyleSheet("background-color: #ffffff; color: #212121;")
        
        self.checklist = checklist
        self.ruolo = ruolo
        self.utente_nome = utente_nome
        self.targa = targa
        self.flotta_controller = flotta_controller
        self.turno = turno
        self.mezzi_disponibili = list(mezzi_disponibili) if mezzi_disponibili else []
        self.current_index = 0
        
        # Recupera la lista di controlli specifica per il ruolo
        self.controlli = Checklist.getControlliPerRuolo(self.ruolo)
        self.risposte = dict(getattr(self.checklist, "risposte", {}))
        self._timer_avanzamento = None
        
        self.setup_ui()
        self.update_current_check()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)
        
        # 1. Header (Utente, Ruolo e Mezzo Assegnato con opzione Cambio)
        header_row1 = QHBoxLayout()
        self.lbl_utente = QLabel(f"👤 <b>Operatore:</b> {self.utente_nome}")
        self.lbl_utente.setStyleSheet("font-size: 13px; color: #424242;")
        self.lbl_ruolo = QLabel(f"🏷️ <b>Ruolo:</b> {self.ruolo}")
        self.lbl_ruolo.setStyleSheet("font-size: 13px; color: #424242;")
        header_row1.addWidget(self.lbl_utente)
        header_row1.addStretch()
        header_row1.addWidget(self.lbl_ruolo)
        main_layout.addLayout(header_row1)

        header_row2 = QHBoxLayout()
        self.lbl_mezzo = QLabel(f"🚑 <b>Veicolo:</b> <span style='color: #c62828; font-weight: bold;'>{self.targa}</span>")
        self.lbl_mezzo.setStyleSheet("font-size: 13px; color: #333333;")
        header_row2.addWidget(self.lbl_mezzo)
        header_row2.addStretch()

        if self.mezzi_disponibili and self.flotta_controller:
            self.btn_cambia_mezzo = QPushButton("🔄 Cambia Veicolo")
            self.btn_cambia_mezzo.setToolTip("Sostituisci il veicolo operativo se diverso da quello programmato")
            self.btn_cambia_mezzo.setStyleSheet("""
                QPushButton {
                    background-color: #f5f5f5;
                    color: #0277bd;
                    border: 1px solid #90caf9;
                    font-weight: bold;
                    font-size: 11px;
                    padding: 3px 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #e1f5fe;
                }
            """)
            self.btn_cambia_mezzo.clicked.connect(self._apri_cambio_mezzo)
            header_row2.addWidget(self.btn_cambia_mezzo)

        main_layout.addLayout(header_row2)
        
        # Linea divisoria rossa (come da mockup grafico)
        line_red = QFrame()
        line_red.setFrameShape(QFrame.HLine)
        line_red.setStyleSheet("border: none; background-color: #d32f2f; min-height: 2px; max-height: 2px; margin: 4px 0 12px 0;")
        main_layout.addWidget(line_red)

        # 2. Categoria (es. 100-Mezzo, 300-Ossigenoterapia)
        self.lbl_categoria = QLabel("100-Mezzo")
        self.lbl_categoria.setAlignment(Qt.AlignCenter)
        self.lbl_categoria.setStyleSheet("font-size: 13px; font-weight: 500; color: #555555; margin-top: 10px;")
        main_layout.addWidget(self.lbl_categoria)
        
        # 3. Nome Controllo / Domanda
        self.lbl_nome = QLabel("Dispositivi di Sicurezza (Cicalino retromarcia, sensore prossimità, telecamera)")
        self.lbl_nome.setAlignment(Qt.AlignCenter)
        self.lbl_nome.setWordWrap(True)
        self.lbl_nome.setStyleSheet("font-size: 18px; font-weight: bold; color: #111111; margin: 15px 0 10px 0; padding: 0 15px; line-height: 1.4;")
        main_layout.addWidget(self.lbl_nome)

        # 3.1 Istruzioni Operative / Note
        self.lbl_istruzioni = QLabel()
        self.lbl_istruzioni.setAlignment(Qt.AlignCenter)
        self.lbl_istruzioni.setWordWrap(True)
        self.lbl_istruzioni.setStyleSheet("font-size: 12px; color: #555555; background-color: #f7f9fa; border: 1px dashed #cfd8dc; border-radius: 6px; padding: 8px 14px; margin: 0 15px 15px 15px;")
        self.lbl_istruzioni.setVisible(False)
        main_layout.addWidget(self.lbl_istruzioni)
        
        # 4. Area Input (Pulsanti dinamici OK/KO o Scelta Carburante)
        self.input_area = QWidget()
        self.input_layout = QVBoxLayout(self.input_area)
        self.input_layout.setContentsMargins(0, 10, 0, 10)
        self.input_layout.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.input_area)
        
        main_layout.addStretch()
        
        # 5. Barra Inferiore di Navigazione
        bottom_bar = QHBoxLayout()
        
        self.btn_indietro = QPushButton("⬅️ Precedente")
        self.btn_indietro.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #555555;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e4e4e4;
            }
            QPushButton:disabled {
                background-color: #fafafa;
                color: #cccccc;
                border-color: #eeeeee;
            }
        """)
        self.btn_indietro.clicked.connect(self.vai_precedente)
        bottom_bar.addWidget(self.btn_indietro)
        
        self.lbl_progresso = QLabel("Controllo 1 di 8")
        self.lbl_progresso.setAlignment(Qt.AlignCenter)
        self.lbl_progresso.setStyleSheet("font-size: 12px; color: #888888; font-weight: bold;")
        bottom_bar.addWidget(self.lbl_progresso)
        
        bottom_bar.addStretch()
        
        self.btn_prossimo = QPushButton("Prossimo")
        self.btn_prossimo.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #212121;
                border: 1px solid #bdbdbd;
                border-radius: 6px;
                padding: 10px 26px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d5d5d5;
            }
        """)
        self.btn_prossimo.clicked.connect(self.vai_prossimo)
        bottom_bar.addWidget(self.btn_prossimo)
        
        main_layout.addLayout(bottom_bar)

    def _apri_cambio_mezzo(self):
        cur_m = next((m for m in self.mezzi_disponibili if m.targa == self.targa), None)
        turni_list = [self.turno] if self.turno else []
        dlg = AssegnaMezzoDialog(self.mezzi_disponibili, turni_list, preselected_mezzo=cur_m, parent=self)
        dlg.setWindowTitle("🔄 Sostituisci Mezzo per la Checklist")
        if dlg.exec_():
            nuovo_m, _ = dlg.get_selected()
            if nuovo_m:
                self.targa = nuovo_m.targa
                self.lbl_mezzo.setText(f"🚑 <b>Veicolo:</b> <span style='color: #c62828; font-weight: bold;'>{self.targa}</span>")
                if self.flotta_controller and self.turno:
                    self.flotta_controller.assegnaMezzoATurno(nuovo_m, self.turno)
                    if hasattr(self.parent(), "update_ui"):
                        self.parent().update_ui()
        
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
                        
    def update_current_check(self):
        totale = len(self.controlli)
        self.lbl_progresso.setText(f"Controllo {self.current_index + 1} di {totale}  •  ⚡ Avanzamento rapido")
        self.btn_indietro.setEnabled(self.current_index > 0)
        
        if self.current_index == totale - 1:
            self.btn_prossimo.setText("✔️ Salva e Concludi")
            self.btn_prossimo.setStyleSheet("""
                QPushButton {
                    background-color: #2e7d32;
                    color: white;
                    border: 1px solid #1b5e20;
                    border-radius: 6px;
                    padding: 10px 24px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1b5e20;
                }
            """)
        else:
            self.btn_prossimo.setText("Prossimo")
            self.btn_prossimo.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #212121;
                    border: 1px solid #bdbdbd;
                    border-radius: 6px;
                    padding: 10px 26px;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d5d5d5;
                }
            """)
            
        controllo = self.controlli[self.current_index]
        self.lbl_categoria.setText(controllo.get("categoria", "Controllo"))
        self.lbl_nome.setText(controllo.get("nome", ""))

        istr = controllo.get("istruzioni", "")
        if istr:
            self.lbl_istruzioni.setText(f"ℹ️ Istruzioni operative:\n{istr}")
            self.lbl_istruzioni.setVisible(True)
        else:
            self.lbl_istruzioni.setVisible(False)
        
        self.clear_layout(self.input_layout)
        valore_corrente = self.risposte.get(controllo["nome"])
        tipo = controllo.get("tipo", "ok_ko")
        
        if tipo == "ok_ko":
            row = QHBoxLayout()
            row.setSpacing(20)
            row.setAlignment(Qt.AlignCenter)
            
            self.btn_ok = QPushButton("OK")
            self.btn_ko = QPushButton("KO")
            
            self._aggiorna_stile_ok_ko(valore_corrente)
            
            self.btn_ok.clicked.connect(lambda: self._imposta_risposta("OK"))
            self.btn_ko.clicked.connect(lambda: self._imposta_risposta("KO"))
            
            row.addWidget(self.btn_ok)
            row.addWidget(self.btn_ko)
            self.input_layout.addLayout(row)
            
        elif tipo == "scelta":
            row = QHBoxLayout()
            row.setSpacing(12)
            row.setAlignment(Qt.AlignCenter)
            
            opzioni = controllo.get("opzioni", ["PIENO", "3/4", "1/2", "RISERVA"])
            self.scelta_pulsanti = {}
            for opz in opzioni:
                btn = QPushButton(opz)
                self.scelta_pulsanti[opz] = btn
                btn.clicked.connect(lambda checked, o=opz: self._imposta_risposta(o))
                row.addWidget(btn)
                
            self._aggiorna_stile_scelta(valore_corrente)
            self.input_layout.addLayout(row)
            
    def _aggiorna_stile_ok_ko(self, valore):
        # Stile OK (Pastel green / Dark green if active)
        if valore == "OK":
            self.btn_ok.setStyleSheet("background-color: #2e7d32; color: #ffffff; border: 2px solid #1b5e20; border-radius: 6px; font-size: 18px; font-weight: bold; min-height: 52px; min-width: 140px;")
        else:
            self.btn_ok.setStyleSheet("background-color: #c8e6c9; color: #1b5e20; border: 1px solid #81c784; border-radius: 6px; font-size: 18px; font-weight: bold; min-height: 52px; min-width: 140px;")
            
        # Stile KO (Pastel red / Dark red if active)
        if valore == "KO":
            self.btn_ko.setStyleSheet("background-color: #d32f2f; color: #ffffff; border: 2px solid #b71c1c; border-radius: 6px; font-size: 18px; font-weight: bold; min-height: 52px; min-width: 140px;")
        else:
            self.btn_ko.setStyleSheet("background-color: #ffcdd2; color: #b71c1c; border: 1px solid #e57373; border-radius: 6px; font-size: 18px; font-weight: bold; min-height: 52px; min-width: 140px;")

    def _aggiorna_stile_scelta(self, valore):
        colori_base = {
            "PIENO": ("#c8e6c9", "#1b5e20", "#81c784"),
            "3/4": ("#dcedc8", "#33691e", "#aed581"),
            "1/2": ("#fff59d", "#f57f17", "#fff176"),
            "RISERVA": ("#ffcdd2", "#b71c1c", "#e57373")
        }
        for opz, btn in self.scelta_pulsanti.items():
            bg_base, fg_base, border_base = colori_base.get(opz, ("#e0e0e0", "#212121", "#bdbdbd"))
            if opz == valore:
                btn.setStyleSheet(f"background-color: {border_base}; color: #000000; border: 2px solid {fg_base}; border-radius: 6px; font-size: 14px; font-weight: bold; min-height: 48px; min-width: 80px;")
            else:
                btn.setStyleSheet(f"background-color: {bg_base}; color: {fg_base}; border: 1px solid {border_base}; border-radius: 6px; font-size: 14px; font-weight: bold; min-height: 48px; min-width: 80px;")

    def _imposta_risposta(self, valore):
        controllo = self.controlli[self.current_index]
        self.risposte[controllo["nome"]] = valore
        tipo = controllo.get("tipo", "ok_ko")
        if tipo == "ok_ko":
            self._aggiorna_stile_ok_ko(valore)
        elif tipo == "scelta":
            self._aggiorna_stile_scelta(valore)

        # Avanzamento automatico immediato al controllo successivo (con 180ms per feedback visivo del clic)
        if hasattr(self, "_timer_avanzamento") and self._timer_avanzamento is not None:
            self._timer_avanzamento.stop()

        self._timer_avanzamento = QTimer(self)
        self._timer_avanzamento.setSingleShot(True)
        self._timer_avanzamento.timeout.connect(self._auto_avanza)
        self._timer_avanzamento.start(180)

    def _auto_avanza(self):
        self.vai_prossimo()
            
    def vai_precedente(self):
        if hasattr(self, "_timer_avanzamento") and self._timer_avanzamento is not None:
            self._timer_avanzamento.stop()
        if self.current_index > 0:
            self.current_index -= 1
            self.update_current_check()
            
    def vai_prossimo(self):
        if hasattr(self, "_timer_avanzamento") and self._timer_avanzamento is not None:
            self._timer_avanzamento.stop()
        controllo = self.controlli[self.current_index]
        if controllo["nome"] not in self.risposte:
            QMessageBox.information(self, "Selezione Richiesta", "Seleziona un'opzione (OK/KO o livello) prima di proseguire.")
            return
            
        if self.current_index < len(self.controlli) - 1:
            self.current_index += 1
            self.update_current_check()
        else:
            self.fine_checklist()

    def reject(self):
        if hasattr(self, "_timer_avanzamento") and self._timer_avanzamento is not None:
            self._timer_avanzamento.stop()
        super().reject()
            
    def fine_checklist(self):
        self.checklist.risposte = self.risposte
        self.checklist.ruoloCompilatore = self.ruolo
        
        # Esegue la verifica idoneità (SD_CompilaChecklist)
        idoneo = self.checklist.verificaIdoneita()
        
        if self.flotta_controller:
            self.flotta_controller.compilaChecklist(self.checklist)
            
        if idoneo:
            QMessageBox.information(
                self, 
                "Checklist Conclusa", 
                f"✅ Checklist per {self.ruolo} completata con successo!\n\nTutti i controlli risultano conformi. Il report è stato archiviato regolarmente."
            )
        else:
            anomalie = self.checklist.segnalaAnomalia()
            dettaglio = "\n• " + "\n• ".join(anomalie)
            QMessageBox.warning(
                self,
                "⚠️ Segnalazione Anomalia",
                f"Attenzione: durante la compilazione sono state rilevate anomalie bloccanti:{dettaglio}\n\n"
                f"È stata inviata una segnalazione automatica al referente di turno e al servizio manutenzione."
            )
        self.accept()

class CompilaResocontoDialog(QDialog):
    """
    Finestra per la compilazione del Resoconto Fine Turno (Boundary UI_Resoconto, SD_CompilaResoconto).
    Chiede all'operatore i kilometri finali risultanti sul quadro strumenti (tachimetro) del veicolo,
    calcolando in tempo reale la differenza di km percorsi ed evitando calcoli manuali a mente.
    """
    def __init__(self, turno=None, mezzo=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📝 Resoconto Operativo Fine Turno")
        self.setMinimumWidth(480)
        self.turno = turno
        self.mezzo = mezzo
        
        # Recupera mezzo se non passato direttamente
        if not self.mezzo and self.turno and getattr(self.turno, "mezzo", None):
            self.mezzo = self.turno.mezzo

        self.km_iniziali = 0
        if self.mezzo:
            self.km_iniziali = int(getattr(self.mezzo, "chilometraggioTotale", 0) or getattr(self.mezzo, "chilometraggio", 0) or 0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #e0e0e0;
                font-family: "Helvetica Neue", Arial;
                font-size: 13px;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #242424;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 6px 10px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #e53935;
            }
            QPushButton#SaveBtn {
                background-color: #2e7d32;
                color: white;
                font-weight: bold;
                padding: 9px 16px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton#SaveBtn:hover {
                background-color: #388e3c;
            }
            QPushButton#SaveBtn:disabled {
                background-color: #333333;
                color: #777777;
            }
        """)

        # Scheda Dettaglio Turno e Mezzo
        info_card = QFrame()
        info_card.setStyleSheet("background-color: #242424; border-radius: 8px; border: 1px solid #333333;")
        c_lay = QVBoxLayout(info_card)
        c_lay.setContentsMargins(14, 12, 14, 12)
        c_lay.setSpacing(5)

        t_serv = getattr(self.turno, "tipoServizio", "Servizio CRI") if self.turno else "Servizio CRI"
        t_data = getattr(self.turno, "data", "") if self.turno else ""
        t_ora = getattr(self.turno, "fascia_oraria", "") if self.turno else ""
        t_luogo = getattr(self.turno, "luogo", "") if self.turno else ""

        c_lay.addWidget(QLabel(f"<h3 style='margin:0; color:#ff5252;'>🚑 {t_serv}</h3>"))
        c_lay.addWidget(QLabel(f"<span style='color:#bbb;'>🗓️ <b>Data:</b> {t_data} &nbsp;|&nbsp; 🕒 <b>Orario:</b> {t_ora}</span>"))
        if t_luogo:
            c_lay.addWidget(QLabel(f"<span style='color:#bbb;'>📍 <b>Luogo / Destinazione:</b> {t_luogo}</span>"))

        if self.mezzo:
            targa = self.mezzo.targa
            tipo_m = getattr(self.mezzo, "tipo", "Ambulanza")
            c_lay.addWidget(QLabel(f"<span style='color:#64b5f6;'>🚐 <b>Veicolo:</b> {targa} — {tipo_m}</span>"))
            c_lay.addWidget(QLabel(f"<span style='color:#00e676;'>📟 <b>Chilometraggio Iniziale:</b> {self.km_iniziali:,} km</span>"))
        else:
            c_lay.addWidget(QLabel("<span style='color:#ffb74d;'>⚪ Nessun veicolo associato al turno</span>"))

        layout.addWidget(info_card)

        # Form Dati Resoconto
        form = QFormLayout()
        form.setSpacing(12)

        if self.mezzo:
            self.spin_km_finali = QSpinBox()
            self.spin_km_finali.setRange(0, 9999999)
            self.spin_km_finali.setValue(self.km_iniziali)
            self.spin_km_finali.setSuffix(" km")
            self.spin_km_finali.valueChanged.connect(self._on_km_changed)
            form.addRow("<b>Kilometri Risultanti sul Mezzo:</b>", self.spin_km_finali)

            self.lbl_km_calc = QLabel("<span style='color:#00e676; font-weight:bold;'>📈 Chilometri percorsi durante il turno: +0 km</span>")
            form.addRow("", self.lbl_km_calc)
        else:
            self.spin_km_finali = None
            self.spin_km_manuali = QSpinBox()
            self.spin_km_manuali.setRange(0, 10000)
            self.spin_km_manuali.setValue(0)
            self.spin_km_manuali.setSuffix(" km")
            form.addRow("<b>Chilometri Percorsi (se applicabile):</b>", self.spin_km_manuali)

        # Ore effettive
        self.spin_ore = QDoubleSpinBox()
        self.spin_ore.setRange(0.5, 24.0)
        self.spin_ore.setSingleStep(0.5)
        default_ore = 6.0
        if self.turno and getattr(self.turno, "oraInizio", "") and getattr(self.turno, "oraFine", ""):
            try:
                ini = int(self.turno.oraInizio.split(":")[0])
                fin = int(self.turno.oraFine.split(":")[0])
                diff = fin - ini if fin >= ini else (24 - ini + fin)
                if diff > 0:
                    default_ore = float(diff)
            except Exception:
                pass
        self.spin_ore.setValue(default_ore)
        self.spin_ore.setSuffix(" ore")
        form.addRow("<b>Ore Effettive Svolte:</b>", self.spin_ore)

        # Note intervento
        self.note_edit = QLineEdit("Servizio completato regolarmente senza anomalie.")
        form.addRow("Note Intervento:", self.note_edit)

        layout.addLayout(form)

        # Pulsanti azione
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_annulla = QPushButton("Annulla")
        btn_annulla.clicked.connect(self.reject)

        self.btn_salva = QPushButton("💾 Invia Resoconto Fine Turno")
        self.btn_salva.setObjectName("SaveBtn")
        self.btn_salva.clicked.connect(self.accept)

        btn_layout.addWidget(btn_annulla)
        btn_layout.addWidget(self.btn_salva)
        layout.addLayout(btn_layout)

    def _on_km_changed(self, val: int):
        if val < self.km_iniziali:
            diff = self.km_iniziali - val
            self.lbl_km_calc.setText(f"<span style='color:#ff5252;'>⚠️ I km finali ({val:,} km) non possono essere inferiori a quelli iniziali ({self.km_iniziali:,} km)! Meno {diff:,} km</span>")
            self.btn_salva.setEnabled(False)
        else:
            diff = val - self.km_iniziali
            self.lbl_km_calc.setText(f"<span style='color:#00e676; font-weight:bold;'>📈 Chilometri percorsi durante il turno: +{diff:,} km</span>")
            self.btn_salva.setEnabled(True)

    def get_dati(self) -> tuple[int, int, float, str]:
        """Restituisce: (km_finali, km_percorsi, ore_effettive, note)"""
        ore = float(self.spin_ore.value())
        note = self.note_edit.text().strip()
        if self.mezzo and self.spin_km_finali:
            km_finali = int(self.spin_km_finali.value())
            km_percorsi = max(0, km_finali - self.km_iniziali)
            return (km_finali, km_percorsi, ore, note)
        else:
            km_p = int(self.spin_km_manuali.value()) if hasattr(self, "spin_km_manuali") else 0
            return (km_p, km_p, ore, note)


class VisualizzaReportDialog(QDialog):
    """Dialog per la visualizzazione e l'esportazione del report attività in formato TXT o CSV."""
    def __init__(self, titolo: str, testo_report: str, volontario=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titolo)
        self.resize(680, 520)
        self.testo_report = testo_report
        self.volontario = volontario

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel(f"<h3 style='color: white; margin: 0;'>📄 {titolo}</h3>")
        layout.addWidget(header)

        self.txt_view = QTextEdit()
        self.txt_view.setReadOnly(True)
        self.txt_view.setText(testo_report)
        self.txt_view.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #e0e0e0;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        layout.addWidget(self.txt_view)

        btn_layout = QHBoxLayout()
        btn_txt = QPushButton("💾 Salva come file TXT")
        btn_txt.setStyleSheet("background-color: #2e7d32; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        btn_txt.clicked.connect(self.salva_txt)
        btn_layout.addWidget(btn_txt)

        btn_csv = QPushButton("📊 Esporta in CSV")
        btn_csv.setStyleSheet("background-color: #0277bd; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        btn_csv.clicked.connect(self.salva_csv)
        btn_layout.addWidget(btn_csv)

        btn_layout.addStretch()

        btn_chiudi = QPushButton("Chiudi")
        btn_chiudi.setStyleSheet("background-color: #424242; color: white; padding: 8px 16px; border-radius: 6px;")
        btn_chiudi.clicked.connect(self.accept)
        btn_layout.addWidget(btn_chiudi)

        layout.addLayout(btn_layout)

    def salva_txt(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salva Report Attività", "report_croce_rossa.txt", "Text Files (*.txt)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.testo_report)
                QMessageBox.information(self, "Successo", f"✅ Report salvato con successo in:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"❌ Impossibile salvare il file:\n{e}")

    def salva_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Esporta Report CSV", "report_attivita.csv", "CSV Files (*.csv)")
        if path:
            try:
                import csv
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Codice Fiscale", "Nome", "Cognome", "Email", "Data Turno", "Fascia Oraria", "Servizio", "Ore Lavorate"])
                    if self.volontario:
                        cf = getattr(self.volontario, "cod_fiscale", "")
                        nome = getattr(self.volontario, "nome", "")
                        cognome = getattr(self.volontario, "cognome", "")
                        email = getattr(self.volontario, "email", "")
                        turni = getattr(self.volontario, "turni_assegnati", [])
                        if not turni:
                            writer.writerow([cf, nome, cognome, email, "Nessuno", "", "", getattr(self.volontario, "monteOreTotale", 0)])
                        for t in turni:
                            ore = getattr(self.volontario, "ore_lavorate", {}).get(t.id_turno, 0.0)
                            writer.writerow([cf, nome, cognome, email, t.data, t.fascia_oraria, t.tipoServizio, f"{ore:.2f}"])
                    else:
                        writer.writerow(["Report Generale", "", "", "", "", "", "", ""])
                QMessageBox.information(self, "Successo", f"✅ File CSV esportato con successo in:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"❌ Impossibile esportare il file CSV:\n{e}")


class SchedaVolontarioDialog(QDialog):
    """Visualizza e gestisce il profilo dettagliato di un membro (Volontario / Operatore / Referente)."""
    def __init__(self, volontario, sistema, is_referente: bool, parent=None):
        super().__init__(parent)
        self.volontario = volontario
        self.sistema = sistema
        self.is_referente = is_referente
        self.setWindowTitle(f"👤 Scheda Membro: {volontario.get_nome_completo()}")
        self.resize(600, 560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header con ruolo colorato
        h_box = QHBoxLayout()
        titolo = QLabel(f"<h2 style='color: white; margin: 0;'>{volontario.get_nome_completo()}</h2>")
        h_box.addWidget(titolo)

        ruolo_str = str(getattr(volontario, "ruolo", "volontario")).capitalize()
        color_badge = "#2e7d32" if "volontario" in ruolo_str.lower() else ("#c62828" if "referente" in ruolo_str.lower() else "#0277bd")
        badge = QLabel(f"<span style='background-color: {color_badge}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 12px;'>{ruolo_str}</span>")
        h_box.addWidget(badge)
        h_box.addStretch()
        layout.addLayout(h_box)

        # Dati anagrafici e contatti
        form = QFormLayout()
        form.setSpacing(8)
        form.addRow("Codice Fiscale:", QLabel(f"<b>{volontario.cod_fiscale}</b>"))
        form.addRow("Email:", QLabel(volontario.email or "N/D"))
        form.addRow("Telefono:", QLabel(volontario.telefono or "N/D"))
        form.addRow("Data di nascita:", QLabel(volontario.data_nascita or "N/D"))
        form.addRow("Monte Ore Totale:", QLabel(f"<b style='color: #00e676;'>{getattr(volontario, 'monteOreTotale', 0)} ore</b>"))

        patenti_str = ", ".join(getattr(volontario, "patenti", [])) or "Nessuna patente specifica"
        patenti_widget = QWidget()
        pat_lay = QHBoxLayout(patenti_widget)
        pat_lay.setContentsMargins(0, 0, 0, 0)
        pat_lay.setSpacing(8)
        pat_lay.addWidget(QLabel(patenti_str))

        has_pat_pdf = False
        pdf_path_to_open = None
        if hasattr(volontario, "patenti_pdf") and volontario.patenti_pdf:
            import os
            for p_key, p_val in volontario.patenti_pdf.items():
                if os.path.exists(os.path.abspath(p_val)):
                    has_pat_pdf = True
                    pdf_path_to_open = os.path.abspath(p_val)
                    break
        if not has_pat_pdf and getattr(volontario, "patente_pdf_path", None):
            import os
            if os.path.exists(os.path.abspath(volontario.patente_pdf_path)):
                has_pat_pdf = True
                pdf_path_to_open = os.path.abspath(volontario.patente_pdf_path)



        if has_pat_pdf:
            btn_view_pat = QPushButton("👁️ Visualizza PDF Patente")
            btn_view_pat.setStyleSheet("background-color: #17a2b8; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
            btn_view_pat.clicked.connect(lambda _, p=pdf_path_to_open: self.apri_pdf(p))
            pat_lay.addWidget(btn_view_pat)
        elif getattr(volontario, "patenti", []):
            lbl_no_pdf = QLabel("<span style='color: #ff9800; font-size: 11px;'>⚠️ Nessun PDF allegato</span>")
            pat_lay.addWidget(lbl_no_pdf)
        pat_lay.addStretch()
        form.addRow("Patenti CRI:", patenti_widget)

        qualifiche_str = ", ".join(getattr(volontario, "qualifiche", [])) or "Nessuna qualifica registrata"
        form.addRow("Qualifiche / Brevetti:", QLabel(qualifiche_str))

        # Specializzazioni se operatore sanitario
        specs = getattr(volontario, "specializzazioni", [])
        if specs or "operatore" in ruolo_str.lower():
            specs_str = ", ".join(specs) if specs else "Nessuna indicata"
            form.addRow("Specializzazioni Sanitarie:", QLabel(f"<b style='color: #4fc3f7;'>{specs_str}</b>"))

        # Corsi Formativi (Effettuati e In Formazione)
        from GestioneFormazioneController import GestioneFormazioneController
        f_ctrl = GestioneFormazioneController()
        corsi_suddivisi = f_ctrl.ottieniCorsiSuddivisi(volontario, self.sistema)
        corsi_eff = corsi_suddivisi["effettuati"]
        corsi_inc = corsi_suddivisi["in_corso"]

        corsi_box = QWidget()
        corsi_lay = QVBoxLayout(corsi_box)
        corsi_lay.setContentsMargins(0, 0, 0, 0)
        corsi_lay.setSpacing(4)

        if corsi_eff:
            badge_list = [f"<span style='background-color: #2e7d32; color: white; padding: 2px 7px; border-radius: 4px; font-size: 11px; font-weight: bold;'>✅ {c.titolo or c.nome}</span>" for c in corsi_eff]
            corsi_lay.addWidget(QLabel(f"<b>Effettuati / Conseguiti ({len(corsi_eff)}):</b> " + " ".join(badge_list)))
        else:
            corsi_lay.addWidget(QLabel("<b>Effettuati:</b> <span style='color: #888;'>Nessun corso completato</span>"))

        if corsi_inc:
            badge_inc = [f"<span style='background-color: #ef6c00; color: white; padding: 2px 7px; border-radius: 4px; font-size: 11px; font-weight: bold;'>⏳ {c.titolo or c.nome}</span>" for c in corsi_inc]
            corsi_lay.addWidget(QLabel(f"<b>In Formazione / Da Svolgere ({len(corsi_inc)}):</b> " + " ".join(badge_inc)))

        form.addRow("Formazione CRI:", corsi_box)

        layout.addLayout(form)

        # Turni svolti
        turni = getattr(volontario, "turni_assegnati", [])
        lbl_turni = QLabel(f"<b>🗓️ Turni assegnati ({len(turni)}):</b>")
        layout.addWidget(lbl_turni)

        tbl_turni = QTableWidget(len(turni), 5)
        tbl_turni.setHorizontalHeaderLabels(["Data", "Orario", "Servizio", "Ruolo Spettante", "Ore"])
        tbl_turni.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tbl_turni.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tbl_turni.horizontalHeader().setMinimumSectionSize(70)
        tbl_turni.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        tbl_turni.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        tbl_turni.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        tbl_turni.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        tbl_turni.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        tbl_turni.setColumnWidth(0, 95)
        tbl_turni.setColumnWidth(1, 110)
        tbl_turni.setColumnWidth(3, 145)
        tbl_turni.setColumnWidth(4, 75)
        tbl_turni.verticalHeader().setVisible(False)
        tbl_turni.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tbl_turni.setMaximumHeight(140)

        v_cf = str(getattr(volontario, "cod_fiscale", "")).strip().upper()
        for r, t in enumerate(turni):
            tbl_turni.setItem(r, 0, QTableWidgetItem(t.data))
            tbl_turni.setItem(r, 1, QTableWidgetItem(t.fascia_oraria))
            tbl_turni.setItem(r, 2, QTableWidgetItem(t.tipoServizio))
            
            ruolo_t = ""
            for cf_k, r_val in getattr(t, "volontari_ruoli", {}).items():
                if cf_k.strip().upper() == v_cf:
                    ruolo_t = r_val
                    break
            if not ruolo_t:
                ruolo_t = "Autista Tipo A" if "Emergenza" in getattr(t, "tipoServizio", "") else "Soccorritore Tipo B"
            tbl_turni.setItem(r, 3, QTableWidgetItem(ruolo_t))
            
            ore = getattr(volontario, "ore_lavorate", {}).get(t.id_turno, 0.0)
            tbl_turni.setItem(r, 4, QTableWidgetItem(f"{ore:.1f} h"))
        layout.addWidget(tbl_turni)

        # Azioni
        btn_bar = QHBoxLayout()
        btn_report = QPushButton("📄 Report Attività")
        btn_report.setStyleSheet("background-color: #37474f; color: white; padding: 6px 12px; border-radius: 6px;")
        btn_report.clicked.connect(self.apri_report)
        btn_bar.addWidget(btn_report)

        if self.is_referente:
            btn_ruolo = QPushButton("🔄 Modifica Ruolo")
            btn_ruolo.setStyleSheet("background-color: #c62828; color: white; padding: 6px 12px; border-radius: 6px;")
            btn_ruolo.clicked.connect(self.cambia_ruolo)
            btn_bar.addWidget(btn_ruolo)

            btn_spec = QPushButton("➕ Agg. Specializzazione/Patente")
            btn_spec.setStyleSheet("background-color: #0277bd; color: white; padding: 6px 12px; border-radius: 6px;")
            btn_spec.clicked.connect(self.aggiungi_qualifica_o_spec)
            btn_bar.addWidget(btn_spec)

        btn_bar.addStretch()
        btn_ok = QPushButton("Chiudi")
        btn_ok.clicked.connect(self.accept)
        btn_bar.addWidget(btn_ok)

        layout.addLayout(btn_bar)

    def apri_pdf(self, path):
        import os, sys, subprocess
        if path and os.path.exists(path):
            try:
                if sys.platform == "darwin":
                    subprocess.call(["open", path])
                elif sys.platform == "win32":
                    os.startfile(path)
                else:
                    subprocess.call(["xdg-open", path])
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile aprire il file: {e}")
        else:
            QMessageBox.warning(self, "Errore", "File PDF non trovato.")

    def apri_report(self):
        testo = self.sistema.stampa_report_volontario(self.volontario.cod_fiscale)
        dlg = VisualizzaReportDialog(f"Report Attività — {self.volontario.get_nome_completo()}", testo, self.volontario, self)
        dlg.exec_()

    def cambia_ruolo(self):
        opzioni = ["volontario", "referente"]
        ruolo_attuale = str(getattr(self.volontario, "ruolo", "volontario")).lower()
        idx_default = opzioni.index(ruolo_attuale) if ruolo_attuale in opzioni else 0
        nuovo, ok = QInputDialog.getItem(self, "Modifica Ruolo Membro", f"Seleziona il nuovo ruolo per {self.volontario.get_nome_completo()}:", opzioni, idx_default, False)
        if ok and nuovo:
            self.volontario.ruolo = nuovo
            try:
                self.volontario.aggiorna_firestore()
                QMessageBox.information(self, "Ruolo Aggiornato", f"✅ Ruolo di {self.volontario.get_nome_completo()} aggiornato a '{nuovo}'.")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"❌ Errore aggiornamento ruolo su Firebase: {e}")

    def aggiungi_qualifica_o_spec(self):
        opzioni_tipo = ["Patente", "Qualifica", "Specializzazione Sanitaria"]
        tipo, ok = QInputDialog.getItem(self, "Tipo Attributo", "Cosa desideri aggiungere?", opzioni_tipo, 0, False)
        if not ok or not tipo:
            return
        valore, ok_v = QInputDialog.getText(self, f"Aggiungi {tipo}", f"Inserisci il nome della {tipo.lower()}:")
        if ok_v and valore.strip():
            valore_clean = valore.strip()
            if tipo == "Patente":
                from pdf_validator import valida_pdf_patente
                from patente_extractor import estrai_dati_patente_da_pdf
                import os
                import shutil

                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    f"Seleziona Documento PDF Patente '{valore_clean}'",
                    "",
                    "File PDF (*.pdf)"
                )
                if not file_path:
                    QMessageBox.warning(
                        self,
                        "Operazione Annullata",
                        f"⚠️ Aggiunta patente annullata: per registrare la patente '{valore_clean}' è obbligatorio allegare il relativo documento PDF valido."
                    )
                    return

                valido, motivo = valida_pdf_patente(file_path)
                if not valido:
                    QMessageBox.critical(
                        self,
                        "❌ Verifica di Sicurezza Fallita",
                        f"Il file selezionato per la patente '{valore_clean}' non è valido:\n\n"
                        f"⚠️ {motivo}\n\n"
                        f"La patente NON è stata aggiunta."
                    )
                    return

                dest_dir = os.path.abspath("patenti_pdf")
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                dest_filename = f"{self.volontario.cod_fiscale}_patente_{valore_clean}.pdf"
                dest_path = os.path.join(dest_dir, dest_filename)
                try:
                    shutil.copy(file_path, dest_path)
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"❌ Errore salvataggio del file PDF: {e}")
                    return

                rel_path = f"patenti_pdf/{dest_filename}"
                if not hasattr(self.volontario, "patenti_pdf") or self.volontario.patenti_pdf is None:
                    self.volontario.patenti_pdf = {}
                self.volontario.patenti_pdf[valore_clean] = rel_path
                self.volontario.patente_pdf_path = rel_path

                # Estrapolazione automatica dei dati dal PDF
                dati_estratti = estrai_dati_patente_da_pdf(dest_path)
                if dati_estratti.get("numero_patente"):
                    self.volontario.numero_patente = dati_estratti["numero_patente"]
                if dati_estratti.get("data_scadenza"):
                    self.volontario.scadenza_patente = dati_estratti["data_scadenza"]

                if not hasattr(self.volontario, "patenti") or self.volontario.patenti is None:
                    self.volontario.patenti = []
                if valore_clean not in self.volontario.patenti:
                    self.volontario.patenti.append(valore_clean)
            elif tipo == "Qualifica":
                if not hasattr(self.volontario, "qualifiche") or self.volontario.qualifiche is None:
                    self.volontario.qualifiche = []
                if valore_clean not in self.volontario.qualifiche:
                    self.volontario.qualifiche.append(valore_clean)
            else: # Specializzazione Sanitaria
                if not hasattr(self.volontario, "specializzazioni") or self.volontario.specializzazioni is None:
                    self.volontario.specializzazioni = []
                if valore_clean not in self.volontario.specializzazioni:
                    self.volontario.specializzazioni.append(valore_clean)
            try:
                self.volontario.aggiorna_firestore()
                QMessageBox.information(self, "Successo", f"✅ {tipo} '{valore_clean}' aggiunta con successo e verificata!")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"❌ Errore salvataggio: {e}")


class MainWindow(QWidget):
    def __init__(self, sistema, callback_logout=None, sync_on_start=False):
        super().__init__()
        self.sistema = sistema
        self.callback_logout = callback_logout
        
        # Preserve the logged in user retrieved from login
        prev_logged_user = self.sistema.logged_user
        
        # Synchronize with Firebase Firestore only if requested or if system has no volunteers yet
        if sync_on_start or not self.sistema.volontari:
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

        # RNF4 - Invio promemoria automatici 24 ore prima dell'inizio dei turni di servizio
        try:
            notificati = self.sistema.invia_promemoria_servizi_24h()
            if notificati:
                print(f"[RNF4] Inviati {len(notificati)} promemoria di turno per i servizi delle prossime 24h.")
        except Exception as e:
            print(f"[RNF4 Warning] Impossibile verificare promemoria turni 24h: {e}")

        # Window configuration
        self.setWindowTitle("🚑 Gestione Volontari - Croce Rossa Italiana")
        self.resize(980, 680)
        self.setMinimumSize(640, 480)

        # Dark theme styling with native Apple font stack
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
                font-family: "Helvetica Neue", Arial;
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
                padding: 6px 8px;
            }
            QTableWidget::item:selected {
                background-color: #3e1818;
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
                padding: 10px 14px;
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
                background-color: #e53935;
            }
            QScrollBar:horizontal {
                border: none;
                background-color: #1a1a1a;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #444444;
                min-width: 25px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #e53935;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                border: none;
                background: none;
                width: 0px;
                height: 0px;
            }
            QScrollBar::add-page, QScrollBar::sub-page {
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
                background-color: #212121;
                border: 1px solid #333333;
                border-radius: 8px;
            }
        """)
        self.header_layout = QHBoxLayout(header_container)
        self.header_layout.setContentsMargins(14, 10, 14, 10)
        self.header_layout.setSpacing(12)

        # Avatar circle with user initials
        self.lbl_avatar = QLabel()
        self.lbl_avatar.setFixedSize(38, 38)
        self.lbl_avatar.setAlignment(Qt.AlignCenter)
        self.lbl_avatar.setStyleSheet("""
            background-color: #c62828;
            color: white;
            font-weight: bold;
            font-size: 15px;
            border-radius: 19px;
            border: 2px solid #e53935;
        """)
        self.header_layout.addWidget(self.lbl_avatar)

        # User Info block
        self.user_label = QLabel()
        self.user_label.setStyleSheet("font-size: 13px; color: #ffffff;")
        self.header_layout.addWidget(self.user_label)

        # Status Badges
        self.lbl_badge_ore = QLabel()
        self.lbl_badge_ore.setStyleSheet("background-color: #2e7d32; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;")
        self.header_layout.addWidget(self.lbl_badge_ore)

        self.lbl_badge_patente = QLabel()  # Non aggiunto all'header per richiesta utente

        self.lbl_badge_corsi = QLabel()
        self.header_layout.addWidget(self.lbl_badge_corsi)

        self.header_layout.addStretch()

        # Action Button: Refresh Data
        btn_refresh = QPushButton("🔄 Aggiorna Dati")
        btn_refresh.setToolTip("Sincronizza in tempo reale i dati con Firebase Firestore")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #2b3548;
                border: 1px solid #3d4f6e;
                color: #90caf9;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #354560;
                color: #ffffff;
            }
        """)
        btn_refresh.clicked.connect(self.azione_ricarica_dati)
        self.header_layout.addWidget(btn_refresh)

        # Edit Profile Button
        btn_modifica_dati = QPushButton("👤 Profilo")
        btn_modifica_dati.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: 1px solid #555;
                color: #eee;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        btn_modifica_dati.clicked.connect(self.modifica_dati_volontario)
        self.header_layout.addWidget(btn_modifica_dati)

        # Logout Button
        btn_logout = QPushButton("🚪 Esci")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #b71c1c;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 5px;
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

    def mostra_toast(self, messaggio: str, tipo: str = "success", durata_ms: int = 3000):
        """Mostra una notifica toast non bloccante fluttuante a scomparsa automatica."""
        if not hasattr(self, "_toast_frame"):
            from PyQt5.QtCore import QTimer
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
                border: 1px solid rgba(255,255,255,0.2);
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_toast_frame") and self._toast_frame.isVisible():
            w = self._toast_frame.width()
            h = self._toast_frame.height()
            self._toast_frame.move((self.width() - w) // 2, self.height() - h - 25)

    def update_user_label(self):
        user = self.sistema.logged_user
        if user:
            nome_completo = user.get_nome_completo()
            inits = "".join([part[0].upper() for part in nome_completo.split()[:2]]) or "CR"
            self.lbl_avatar.setText(inits)

            ruolo_str = str(user.ruolo).capitalize()
            badge_color = "#2e7d32" if "volontario" in ruolo_str.lower() else ("#c62828" if "referente" in ruolo_str.lower() else "#0277bd")
            self.user_label.setText(
                f"<b>{nome_completo}</b> &nbsp;"
                f"<span style='background-color: {badge_color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold;'>{ruolo_str}</span>"
            )

            ore = getattr(user, "monteOreTotale", 0)
            self.lbl_badge_ore.setText(f"⏱️ {ore}h svolte")
            self.lbl_badge_ore.setStyleSheet("background-color: #2e7d32; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;")
            self.lbl_badge_ore.setVisible(True)

            self.lbl_badge_patente.setVisible(False)

            # Badge Corsi
            suddivisi = self.formazione_controller.ottieniCorsiSuddivisi(user, self.sistema)
            n_eff = len(suddivisi["effettuati"])
            n_inc = len(suddivisi["in_corso"])
            self.lbl_badge_corsi.setText(f"🎓 {n_eff} completati | {n_inc} in corso")
            self.lbl_badge_corsi.setStyleSheet("background-color: #00838f; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;")
            self.lbl_badge_corsi.setVisible(True)
        else:
            self.lbl_avatar.setText("?")
            self.user_label.setText("Nessun utente collegato.")
            self.lbl_badge_ore.setVisible(False)
            self.lbl_badge_patente.setVisible(False)
            self.lbl_badge_corsi.setVisible(False)

    def azione_ricarica_dati(self):
        try:
            self.sistema.sincronizza_con_firebase()
            self.update_ui()
            self.mostra_toast("🔄 Dati sincronizzati con successo da Firebase!", tipo="success")
        except Exception as e:
            self.mostra_toast(f"Errore sincronizzazione: {e}", tipo="error")

    def azione_logout(self):
        if self.callback_logout:
            self.callback_logout()
        else:
            self.close()

    def configura_tabella_responsive(self, tbl: QTableWidget, col_widths: dict = None, stretch_cols: list = None, min_section_size: int = 80):
        """
        Configura una tabella per una visualizzazione ottimale e responsive:
        - Mantiene la leggibilità delle colonne anche in finestre ridotte.
        - Attiva la barra di scorrimento orizzontale fluida quando lo spazio è insufficiente.
        - Assegna dimensioni minime adeguate e gestione proporzionale intelligente.
        - Seleziona l'intera riga (SelectRows) con SingleSelection.
        """
        header = tbl.horizontalHeader()
        header.setMinimumSectionSize(min_section_size)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tbl.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tbl.setWordWrap(False)
        tbl.setTextElideMode(Qt.ElideRight)

        count = tbl.columnCount()
        for col in range(count):
            if stretch_cols and col in stretch_cols:
                header.setSectionResizeMode(col, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QHeaderView.Interactive)

            if col_widths and col in col_widths:
                tbl.setColumnWidth(col, col_widths[col])

        if not stretch_cols:
            header.setStretchLastSection(True)

    def update_ui(self):
        self.update_user_label()
        self.tab_widget.clear()
        
        # Build tabs based on role
        user = self.sistema.logged_user
        if not user:
            return
            
        is_referente = isinstance(user, Referente) or getattr(user, "ruolo", "").lower() == "referente"
        
        # 1. Dashboard Tab
        self.tab_widget.addTab(self.crea_tab_dashboard(is_referente), "📊 Dashboard")
        
        # 2. Turni Tab
        self.tab_widget.addTab(self.crea_tab_turni(is_referente), "🗓️ Turni")
        
        # 3. Flotta Tab
        self.tab_widget.addTab(self.crea_tab_flotta(is_referente), "🚐 Flotta")
        
        # 4. Formazione Tab
        self.tab_widget.addTab(self.crea_tab_formazione(is_referente), "🎓 Formazione")

        # 5. Volontari e Rubrica Tab
        self.tab_widget.addTab(self.crea_tab_rubrica(is_referente), "👥 Volontari e Rubrica")

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
        welcome_title = QLabel(f"<h2 style='color: white; margin: 0;'>Bentornato, {user_name}! 👋</h2>")
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
            
            lbl_title = QLabel("<h3 style='color: white; margin: 0;'>🛠️ Centro di Controllo Coordinatore</h3>")
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

            # RF23 - Azione Backup Periodico
            btn_backup = QPushButton("💾 Esegui Backup Periodico del Sistema (RF23)")
            btn_backup.setStyleSheet("""
                QPushButton {
                    background-color: #2e7d32;
                    color: white;
                    font-weight: bold;
                    padding: 8px 14px;
                    border-radius: 6px;
                    border: none;
                    margin-top: 6px;
                }
                QPushButton:hover {
                    background-color: #388e3c;
                }
            """)
            btn_backup.clicked.connect(self.azione_esegui_backup)
            ac_layout.addWidget(btn_backup)

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

        # Sezione Avvisi Operativi & Scadenze (visibile se ci sono avvisi)
        avvisi = self.sistema.get_avvisi_sistema()
        if avvisi:
            avvisi_card = QFrame()
            avvisi_card.setStyleSheet("""
                .QFrame {
                    background-color: #1f1b18;
                    border: 1.5px solid #ff9800;
                    border-radius: 8px;
                }
            """)
            avv_lay = QVBoxLayout(avvisi_card)
            avv_lay.setContentsMargins(15, 12, 15, 12)
            avv_lay.setSpacing(6)

            avv_header = QLabel(f"<b style='color: #ffb74d; font-size: 13px;'>🔔 Avvisi Operativi e Scadenze Attive ({len(avvisi)}):</b>")
            avv_lay.addWidget(avv_header)

            for item in avvisi[:5]:  # Mostra fino a 5 avvisi principali
                col = "#ef5350" if item.get("livello") == "danger" else "#ffb74d"
                icona = "🚨" if item.get("livello") == "danger" else "⚠️"
                row_lbl = QLabel(f"<span style='color: {col}; font-weight: bold;'>{icona} {item.get('titolo')}:</span> <span style='color: #ccc; font-size: 12px;'>{item.get('dettaglio')}</span>")
                row_lbl.setWordWrap(True)
                avv_lay.addWidget(row_lbl)

            scroll_layout.addWidget(avvisi_card)

        # 4. Assigned Shifts Section (Always visible)
        header_shifts_lay = QHBoxLayout()
        title_shifts = QLabel("<h3 style='color: white; margin: 0;'>🗓️ I Miei Turni Assegnati & Dettagli:</h3>")
        header_shifts_lay.addWidget(title_shifts)

        btn_mio_report = QPushButton("📄 Scarica / Esporta Report Ore")
        btn_mio_report.setStyleSheet("""
            QPushButton {
                background-color: #37474f;
                color: #eceff1;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #546e7a;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
        """)
        btn_mio_report.clicked.connect(self.apri_report_personale)
        header_shifts_lay.addWidget(btn_mio_report)
        header_shifts_lay.addStretch()

        scroll_layout.addLayout(header_shifts_lay)
        
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
            
            admin_layout.addWidget(QLabel("<h3 style='color: white;'>🛠️ Pianificazione Turni di Servizio (Gestione Referente):</h3>"))
            
            self.tbl_tutti_turni = QTableWidget(0, 9)
            self.tbl_tutti_turni.setEditTriggers(QAbstractItemView.DoubleClicked)
            # pyrefly: ignore [missing-attribute]
            self.tbl_tutti_turni.itemChanged.connect(self.on_turno_cell_changed)
            self.tbl_tutti_turni.setHorizontalHeaderLabels(["ID", "Data", "Orario", "Luogo", "Servizio", "Veicolo", "Persone Richieste", "Iscritti", "Stato"])
            self.configura_tabella_responsive(
                self.tbl_tutti_turni,
                col_widths={0: 70, 1: 95, 2: 110, 3: 140, 4: 120, 5: 130, 6: 115, 7: 75, 8: 95},
                stretch_cols=[3, 4, 5],
                min_section_size=70
            )
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
        
        disp_header = QHBoxLayout()
        disp_header.addWidget(QLabel("<h3 style='color: white; margin: 0;'>🔗 Turni Disponibili per l'Iscrizione:</h3>"))
        disp_header.addStretch()

        self.chk_solo_compatibili = QCheckBox("🎯 Mostra solo turni compatibili con me")
        self.chk_solo_compatibili.setStyleSheet("color: #64b5f6; font-weight: bold; font-size: 12px;")
        self.chk_solo_compatibili.toggled.connect(self.popola_tabelle_turni_volontario)
        disp_header.addWidget(self.chk_solo_compatibili)

        self.chk_mostra_completi = QCheckBox("👁️ Mostra anche turni al completo")
        self.chk_mostra_completi.setStyleSheet("color: #888888; font-size: 12px;")
        self.chk_mostra_completi.setChecked(False)
        self.chk_mostra_completi.toggled.connect(self.popola_tabelle_turni_volontario)
        disp_header.addWidget(self.chk_mostra_completi)
        booking_layout.addLayout(disp_header)
        
        self.tbl_turni_disp = QTableWidget(0, 8)
        self.tbl_turni_disp.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_turni_disp.setHorizontalHeaderLabels(["ID", "Data", "Orario", "Luogo", "Servizio", "Veicolo", "Patente Richiesta", "Disponibilità Posti"])
        self.configura_tabella_responsive(
            self.tbl_turni_disp,
            col_widths={0: 70, 1: 95, 2: 110, 3: 140, 4: 120, 5: 130, 6: 120, 7: 140},
            stretch_cols=[3, 4, 5],
            min_section_size=70
        )
        self.tbl_turni_disp.verticalHeader().setDefaultSectionSize(36)
        self.tbl_turni_disp.verticalHeader().setVisible(False)
        self.tbl_turni_disp.setMinimumHeight(150)
        self.tbl_turni_disp.cellDoubleClicked.connect(lambda r, c: self.azione_prenota_turno())
        booking_layout.addWidget(self.tbl_turni_disp)
        
        btn_prenota = QPushButton("🔗 Prenota Turno Selezionato (o fai doppio clic)")
        btn_prenota.clicked.connect(self.azione_prenota_turno)
        booking_layout.addWidget(btn_prenota)
        
        scroll_layout.addWidget(booking_section)
        
        # Section 3: Personal Assigned Shifts (Visible for BOTH Referente and Volontario)
        personal_section = QWidget()
        personal_layout = QVBoxLayout(personal_section)
        personal_layout.setContentsMargins(0, 0, 0, 0)
        personal_layout.setSpacing(10)
        
        personal_layout.addWidget(QLabel("<h3 style='color: white; margin: 0;'>📋 I Miei Turni Assegnati:</h3>"))
        
        self.tbl_miei_turni = QTableWidget(0, 8)
        self.tbl_miei_turni.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_miei_turni.setHorizontalHeaderLabels(["ID", "Data", "Orario", "Luogo", "Servizio", "Il Tuo Ruolo", "Veicolo", "Stato"])
        self.configura_tabella_responsive(
            self.tbl_miei_turni,
            col_widths={0: 70, 1: 95, 2: 110, 3: 140, 4: 120, 5: 165, 6: 125, 7: 95},
            stretch_cols=[3, 4, 5, 6],
            min_section_size=70
        )
        self.tbl_miei_turni.verticalHeader().setDefaultSectionSize(36)
        self.tbl_miei_turni.verticalHeader().setVisible(False)
        self.tbl_miei_turni.setMinimumHeight(150)
        personal_layout.addWidget(self.tbl_miei_turni)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        btn_cancella = QPushButton("❌ Annulla Assegnazione")
        btn_cancella.clicked.connect(self.azione_annulla_turno)
        actions_layout.addWidget(btn_cancella)

        btn_esporta_ics = QPushButton("📅 Aggiungi a Calendario (.ics)")
        btn_esporta_ics.setToolTip("Esporta i turni in formato iCalendar per Apple Calendar, Google Calendar o Outlook")
        btn_esporta_ics.setStyleSheet("""
            QPushButton {
                background-color: #0277bd;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0288d1;
            }
        """)
        btn_esporta_ics.clicked.connect(self.esporta_calendario_ics)
        actions_layout.addWidget(btn_esporta_ics)

        btn_cambia_mezzo = QPushButton("🚐 Assegna / Cambia Mezzo")
        btn_cambia_mezzo.setToolTip("Consente all'autista o soccorritore di confermare o sostituire il mezzo operativo per questo turno")
        btn_cambia_mezzo.setStyleSheet("""
            QPushButton {
                background-color: #00897b;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00796b;
            }
        """)
        btn_cambia_mezzo.clicked.connect(self.azione_volontario_cambia_mezzo)
        actions_layout.addWidget(btn_cambia_mezzo)
        
        self.btn_checklist = QPushButton("📋 Compila Checklist Veicolo")
        self.btn_checklist.clicked.connect(self.azione_compila_checklist)
        actions_layout.addWidget(self.btn_checklist)
        
        self.tbl_miei_turni.itemSelectionChanged.connect(self._on_miei_turni_selection_changed)
        
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

    def esporta_calendario_ics(self):
        """Esporta i turni assegnati al volontario in formato standard iCalendar (.ics)."""
        from calendar_service import genera_file_ics
        user = self.sistema.logged_user
        turni = getattr(user, "turni_assegnati", [])
        if not turni:
            self.mostra_toast("Nessun turno assegnato da esportare.", tipo="warning")
            return

        default_filename = f"Turni_CRI_{user.cod_fiscale}.ics"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Esporta Turni su Calendario (.ics)",
            default_filename,
            "iCalendar Files (*.ics)"
        )
        if file_path:
            try:
                genera_file_ics(turni, user, file_path)
                self.mostra_toast("📅 Turni esportati con successo nel file .ics!", tipo="success")
            except Exception as e:
                QMessageBox.critical(self, "Errore Esportazione", f"Errore durante la creazione del file .ics: {e}")

    def popola_tabelle_turni_volontario(self):
        # 1. Available shifts
        self.tbl_turni_disp.setRowCount(0)
        user = self.sistema.logged_user
        user_cf = str(user.cod_fiscale) if user else ""

        mostra_completi = getattr(self, "chk_mostra_completi", None) and self.chk_mostra_completi.isChecked()
        stati_validi = ["Proposto", "Aperto", "Completo"] if mostra_completi else ["Proposto", "Aperto"]

        disponibili = [
            t for t in self.sistema.turni 
            if t.stato in stati_validi 
            and not any(str(v.cod_fiscale) == user_cf for v in t.volontari_assegnati)
            and (mostra_completi or not t.isCompleto())
        ]

        if getattr(self, "chk_solo_compatibili", None) and self.chk_solo_compatibili.isChecked() and user:
            disponibili = [t for t in disponibili if self.turni_controller.verificaCoperturaPatente(user, t)]

        for t in disponibili:
            row = self.tbl_turni_disp.rowCount()
            self.tbl_turni_disp.insertRow(row)
            self.tbl_turni_disp.setItem(row, 0, QTableWidgetItem(str(t.id)))
            self.tbl_turni_disp.setItem(row, 1, QTableWidgetItem(t.data))
            self.tbl_turni_disp.setItem(row, 2, QTableWidgetItem(t.fascia_oraria))
            item_luogo = QTableWidgetItem(t.luogo)
            if getattr(t, "luogoPrelevamento", None) or getattr(t, "luogoDestinazione", None):
                item_luogo.setToolTip(f"📍 Prelevamento: {t.luogoPrelevamento}\n🏁 Destinazione: {t.luogoDestinazione}")
            self.tbl_turni_disp.setItem(row, 3, item_luogo)
            self.tbl_turni_disp.setItem(row, 4, QTableWidgetItem(t.tipoServizio))
            
            # Veicolo assegnato
            veicolo_str = f"🚑 {t.mezzo.targa}" if getattr(t, "mezzo", None) else (f"🚑 {t.mezzo_targa}" if getattr(t, "mezzo_targa", "") else "⚪ Da assegnare")
            self.tbl_turni_disp.setItem(row, 5, QTableWidgetItem(veicolo_str))
            
            self.tbl_turni_disp.setItem(row, 6, QTableWidgetItem(t.patenteRichiesta or "Nessuna"))

            tot_req = t.personeRichieste or 1
            attuali = len(t.volontari_assegnati)
            if attuali >= tot_req:
                txt_chip = f"🟢 Al completo ({attuali}/{tot_req})"
            elif attuali > 0:
                txt_chip = f"🟡 Posti liberi ({attuali}/{tot_req})"
            else:
                txt_chip = f"🔴 Scoperto (0/{tot_req})"

            item_disp = QTableWidgetItem(txt_chip)
            item_disp.setTextAlignment(Qt.AlignCenter)
            self.tbl_turni_disp.setItem(row, 7, item_disp)
            
        # 2. My shifts
        self.tbl_miei_turni.setRowCount(0)
        miei = self.sistema.logged_user.turni_assegnati
        user_cf = str(getattr(self.sistema.logged_user, "cod_fiscale", "")).strip().upper()
        for t in miei:
            row = self.tbl_miei_turni.rowCount()
            self.tbl_miei_turni.insertRow(row)
            self.tbl_miei_turni.setItem(row, 0, QTableWidgetItem(str(t.id)))
            self.tbl_miei_turni.setItem(row, 1, QTableWidgetItem(t.data))
            self.tbl_miei_turni.setItem(row, 2, QTableWidgetItem(t.fascia_oraria))
            self.tbl_miei_turni.setItem(row, 3, QTableWidgetItem(t.luogo))
            self.tbl_miei_turni.setItem(row, 4, QTableWidgetItem(t.tipoServizio))
            
            # Il Tuo Ruolo nel turno (Ruolo che spetta all'utente)
            ruolo_raw = ""
            for cf_k, r_val in getattr(t, "volontari_ruoli", {}).items():
                if cf_k.strip().upper() == user_cf:
                    ruolo_raw = r_val
                    break

            if not ruolo_raw:
                if getattr(t, "patenteRichiesta", "") and any(p in getattr(self.sistema.logged_user, "patenti", []) for p in ["B", "C", "D", "E"]):
                    ruolo_raw = "Autista Tipo A" if "Emergenza" in getattr(t, "tipoServizio", "") else "Autista Tipo B"
                else:
                    ruolo_raw = "Soccorritore Tipo A" if "Emergenza" in getattr(t, "tipoServizio", "") else "Soccorritore Tipo B"
            
            icon = "🚗" if "Autista" in ruolo_raw else "🩺"
            item_ruolo = QTableWidgetItem(f"{icon} {ruolo_raw}")
            item_ruolo.setTextAlignment(Qt.AlignCenter)
            font_r = item_ruolo.font()
            font_r.setBold(True)
            item_ruolo.setFont(font_r)
            if "Autista" in ruolo_raw:
                item_ruolo.setForeground(QColor("#64b5f6"))
                item_ruolo.setToolTip(f"Ruolo spettante: {ruolo_raw} (Conducente veicolo di emergenza/ordinario)")
            else:
                item_ruolo.setForeground(QColor("#81c784"))
                item_ruolo.setToolTip(f"Ruolo spettante: {ruolo_raw} (Soccorritore / Assistenza sanitaria a bordo)")
            self.tbl_miei_turni.setItem(row, 5, item_ruolo)
            
            # Veicolo assegnato
            veicolo_str = f"🚑 {t.mezzo.targa}" if getattr(t, "mezzo", None) else (f"🚑 {t.mezzo_targa}" if getattr(t, "mezzo_targa", "") else "⚪ Da assegnare")
            self.tbl_miei_turni.setItem(row, 6, QTableWidgetItem(veicolo_str))
            
            stato_str = t.stato
            if getattr(t, "checklist", False):
                stato_str = f"{t.stato} (✅ Checklist OK)"
            item_stato = QTableWidgetItem(stato_str)
            if getattr(t, "checklist", False):
                item_stato.setForeground(QColor("#a5d6a7"))
                item_stato.setToolTip("Checklist del veicolo già completata con successo per questo turno.")
            self.tbl_miei_turni.setItem(row, 7, item_stato)

        self._on_miei_turni_selection_changed()

    def popola_tabella_turni_admin(self):
        self.tbl_tutti_turni.blockSignals(True)
        self.tbl_tutti_turni.setRowCount(0)
        for t in self.sistema.turni:
            row = self.tbl_tutti_turni.rowCount()
            self.tbl_tutti_turni.insertRow(row)
            self.tbl_tutti_turni.setItem(row, 0, QTableWidgetItem(str(t.id)))
            self.tbl_tutti_turni.setItem(row, 1, QTableWidgetItem(t.data))
            self.tbl_tutti_turni.setItem(row, 2, QTableWidgetItem(t.fascia_oraria))
            item_luogo = QTableWidgetItem(t.luogo)
            tip_parts = [f"📍 Prelevamento: {t.luogoPrelevamento}", f"🏁 Destinazione: {t.luogoDestinazione}"]
            paz_full = f"{getattr(t, 'paziente_nome', '')} {getattr(t, 'paziente_cognome', '')}".strip()
            if paz_full or getattr(t, "paziente_cf", ""):
                tip_parts.append(f"👤 Paziente: {paz_full} (CF: {getattr(t, 'paziente_cf', 'N/D')})")
            item_luogo.setToolTip("\n".join(tip_parts))
            self.tbl_tutti_turni.setItem(row, 3, item_luogo)
            self.tbl_tutti_turni.setItem(row, 4, QTableWidgetItem(t.tipoServizio))
            
            # Veicolo assegnato
            veicolo_str = f"🚑 {t.mezzo.targa}" if getattr(t, "mezzo", None) else (f"🚑 {t.mezzo_targa}" if getattr(t, "mezzo_targa", "") else "⚪ Da assegnare")
            self.tbl_tutti_turni.setItem(row, 5, QTableWidgetItem(veicolo_str))
            
            self.tbl_tutti_turni.setItem(row, 6, QTableWidgetItem(str(t.personeRichieste)))
            
            item_iscritti = QTableWidgetItem(str(len(t.volontari_assegnati)))
            if t.volontari_assegnati:
                dettagli = []
                for v in t.volontari_assegnati:
                    r_v = getattr(t, "volontari_ruoli", {}).get(str(v.cod_fiscale), "Soccorritore")
                    dettagli.append(f"• {v.get_nome_completo()}: {r_v}")
                item_iscritti.setToolTip("\n".join(dettagli))
            self.tbl_tutti_turni.setItem(row, 7, item_iscritti)
            
            self.tbl_tutti_turni.setItem(row, 8, QTableWidgetItem(t.stato))
        self.tbl_tutti_turni.blockSignals(False)

    def azione_prenota_turno(self):
        row = self.tbl_turni_disp.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un turno da prenotare dalla tabella.")
            return
        id_turno = self.tbl_turni_disp.item(row, 0).text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        
        if turno:
            # Controllo se il turno è già al completo
            if turno.isCompleto():
                QMessageBox.warning(self, "Turno al Completo", "Questo turno ha già raggiunto il numero massimo di volontari e non è più disponibile per nuove prenotazioni.")
                return

            # Controllo immediato se il volontario è già iscritto
            if any(str(v.cod_fiscale) == str(self.sistema.logged_user.cod_fiscale) for v in turno.volontari_assegnati):
                QMessageBox.warning(self, "Attenzione", "Sei già iscritto a questo turno!")
                return

            from layout.prenotazione_turno_dialog import PrenotazioneTurnoDialog
            dlg = PrenotazioneTurnoDialog(turno, self.sistema.logged_user, self.turni_controller, self)
            if dlg.exec_() != QDialog.Accepted:
                return

            ruolo = dlg.ruolo_selezionato
            if not ruolo:
                return

            # Salvataggio e assegnazione
            self.turni_controller.prenotaTurno(turno.id, self.sistema.logged_user.cod_fiscale, ruolo)
            self.sistema.logged_user.prenota_turno(turno)
            turno.aggiungiVolontario(self.sistema.logged_user)
            turno.volontari_ruoli[str(self.sistema.logged_user.cod_fiscale)] = ruolo

            try:
                self.sistema.logged_user.aggiorna_firestore()
            except Exception as e:
                print(f"⚠️ Errore aggiornamento profilo volontario su Firebase: {e}")

            self.update_ui()
            self.mostra_toast(f"✅ Iscrizione confermata al turno {turno.id} come {ruolo}!", tipo="success")

    def azione_annulla_turno(self):
        row = self.tbl_miei_turni.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un turno da annullare.")
            return
        id_turno = self.tbl_miei_turni.item(row, 0).text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        
        if turno:
            confirm = QMessageBox.question(
                self,
                "Conferma Annullamento",
                f"Sei sicuro di voler annullare la tua iscrizione al turno del {turno.data} ({turno.fascia_oraria})?\n\n"
                f"Il posto verrà reso nuovamente disponibile per gli altri volontari.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return

            # Delega al controller
            self.turni_controller.annullaPrenotazione(turno)
            self.sistema.logged_user.annulla_prenotazione(turno)
            turno.rimuoviVolontario(self.sistema.logged_user)
            if str(self.sistema.logged_user.cod_fiscale) in getattr(turno, "volontari_ruoli", {}):
                del turno.volontari_ruoli[str(self.sistema.logged_user.cod_fiscale)]

            try:
                self.sistema.logged_user.aggiorna_firestore()
            except Exception as e:
                print(f"⚠️ Errore aggiornamento profilo su Firebase: {e}")

            self.update_ui()
            self.mostra_toast(f"❌ Iscrizione al turno {turno.id} annullata.", tipo="info")

    def azione_volontario_cambia_mezzo(self):
        """Consente all'autista o volontario di abbinare o cambiare il mezzo del proprio turno."""
        row = self.tbl_miei_turni.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un turno dalla tabella 'I Miei Turni Assegnati'.")
            return
        id_item = self.tbl_miei_turni.item(row, 0)
        if not id_item:
            return
        id_turno = id_item.text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        if not turno:
            return

        cur_m = turno.mezzo or next((m for m in self.sistema.mezzi if m.targa == getattr(turno, "mezzo_targa", "")), None)
        dialog = AssegnaMezzoDialog(self.sistema.mezzi, [turno], preselected_mezzo=cur_m, parent=self)
        dialog.setWindowTitle(f"🚐 Assegna / Cambia Mezzo — Turno {turno.id}")
        if dialog.exec_():
            mezzo, _ = dialog.get_selected()
            if mezzo:
                self.flotta_controller.assegnaMezzoATurno(mezzo, turno)
                self.mostra_toast(f"✅ Mezzo {mezzo.targa} abbinato al turno {turno.id}!", tipo="success")
            else:
                self.flotta_controller.assegnaMezzoATurno(None, turno)
                self.mostra_toast(f"⚪ Mezzo rimosso dal turno {turno.id}.", tipo="info")
            self.update_ui()

    def azione_compila_checklist(self):
        row = self.tbl_miei_turni.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima il turno associato alla checklist dalla tabella 'I Miei Turni Assegnati'.")
            return
            
        id_item = self.tbl_miei_turni.item(row, 0)
        if not id_item:
            return
        id_turno = id_item.text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        if not turno:
            return
            
        # Controllo: se la checklist è già stata compilata per questo turno, blocca la ricompilazione
        if getattr(turno, "checklist", False):
            QMessageBox.information(
                self,
                "Checklist Già Completata",
                f"✅ La checklist per il turno {turno.id} ({turno.data} - {turno.fascia_oraria}) è già stata compilata e verificata con successo.\n\n"
                "I dispositivi di bordo e le dotazioni del mezzo risultano già conformi. Non è necessario compilarla nuovamente."
            )
            return
            
        # Determina la targa del veicolo associato al turno
        targa = getattr(turno, "mezzo_targa", "")
        if not targa and getattr(turno, "mezzo", None):
            targa = turno.mezzo.targa

        # Se il mezzo non è stato pre-assegnato dal Referente, proponi all'operatore di selezionarlo subito
        if not targa:
            cur_cf = str(getattr(self.sistema.logged_user, "cod_fiscale", ""))
            ruolo_user = turno.volontari_ruoli.get(cur_cf, "")
            ruolo_label = f" ({ruolo_user})" if ruolo_user else ""
            res = QMessageBox.question(
                self,
                "Assegnazione Mezzo",
                f"Il turno del {turno.data} non ha ancora un veicolo assegnato dal Referente.\n\n"
                f"Vuoi selezionare subito il mezzo con cui stai operando{ruolo_label}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if res == QMessageBox.Yes:
                dlg_sel = AssegnaMezzoDialog(self.sistema.mezzi, [turno], parent=self)
                dlg_sel.setWindowTitle("🚐 Seleziona Mezzo di Servizio")
                if dlg_sel.exec_():
                    m_scelto, _ = dlg_sel.get_selected()
                    if m_scelto:
                        self.flotta_controller.assegnaMezzoATurno(m_scelto, turno)
                        targa = m_scelto.targa
                        self.update_ui()
            if not targa:
                targa = "CRI 302 AJ"

        user = self.sistema.logged_user
        nome_utente = f"{getattr(user, 'nome', '')} {getattr(user, 'cognome', '')}".strip() or "Mario Rossi"
                
        # Legge il ruolo inserito all'iscrizione
        ruolo = turno.volontari_ruoli.get(str(getattr(user, "cod_fiscale", "")))
        if not ruolo:
            # Fallback con selezione tra i 4 ruoli del Model Report
            ruolo, ok = QInputDialog.getItem(
                self, 
                "Ruolo nel Turno", 
                "Seleziona il tuo ruolo operativo per la checklist:", 
                [
                    "Autista A (Emergenza)",
                    "Autista B (Ordinario)",
                    "Soccorritore (Vano Sanitario) - Tipo A",
                    "Soccorritore (Vano Sanitario) - Tipo B"
                ], 
                0, 
                False
            )
            if not ok or not ruolo:
                return
            turno.volontari_ruoli[str(getattr(user, "cod_fiscale", ""))] = ruolo
            
        # Inizializza l'oggetto checklist se non presente
        if not hasattr(turno, 'checklist_obj') or not turno.checklist_obj:
            turno.checklist_obj = Checklist(
                id=f"CL_{turno.id}",
                controlliMeccanici=False,
                dispositiviMediciRichiesti=["Defibrillatore", "Barella", "Bombola O2"],
                dispositiviPresenti=False,
                turnoAssegnato=turno,
                ruoloCompilatore=ruolo
            )
            
        # Apri il Wizard fedele al mockup grafico con possibilità di conferma/cambio mezzo
        dialog = CompilaChecklistDialog(
            checklist=turno.checklist_obj, 
            ruolo=ruolo, 
            utente_nome=nome_utente, 
            targa=targa, 
            flotta_controller=self.flotta_controller, 
            turno=turno,
            mezzi_disponibili=self.sistema.mezzi,
            parent=self
        )
        if dialog.exec_():
            turno.completa_checklist()
            try:
                turno.aggiorna_firestore()
            except Exception as e:
                print(f"⚠️ Errore salvataggio checklist turno: {e}")
            self.update_ui()
            self.mostra_toast("📋 Checklist registrata con successo!", tipo="success")

    def _on_miei_turni_selection_changed(self):
        row = self.tbl_miei_turni.currentRow()
        if not hasattr(self, "btn_checklist"):
            return
        if row < 0:
            self.btn_checklist.setText("📋 Compila Checklist Veicolo")
            self.btn_checklist.setStyleSheet("")
            return
        id_item = self.tbl_miei_turni.item(row, 0)
        if not id_item:
            return
        id_turno = id_item.text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        if turno and getattr(turno, "checklist", False):
            self.btn_checklist.setText("✅ Checklist Completata")
            self.btn_checklist.setToolTip("Checklist già compilata con successo per questo turno.")
            self.btn_checklist.setStyleSheet("""
                QPushButton {
                    background-color: #1b5e20;
                    color: #a5d6a7;
                    border: 1px solid #2e7d32;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        else:
            self.btn_checklist.setText("📋 Compila Checklist Veicolo")
            self.btn_checklist.setToolTip("Compila la checklist di verifica del mezzo prima della partenza")
            self.btn_checklist.setStyleSheet("")

    def azione_compila_resoconto(self):
        row = self.tbl_miei_turni.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona il turno da completare.")
            return
        id_turno = self.tbl_miei_turni.item(row, 0).text()
        turno = next((t for t in self.sistema.turni if str(t.id) == id_turno), None)
        
        if turno:
            mezzo_obj = turno.mezzo or next((m for m in self.sistema.mezzi if m.targa == getattr(turno, "mezzo_targa", "")), None)
            
            dialog = CompilaResocontoDialog(turno=turno, mezzo=mezzo_obj, parent=self)
            if dialog.exec_():
                km_finali, km_percorsi, ore, note = dialog.get_dati()
                
                # Update model
                if self.sistema.logged_user:
                    self.sistema.logged_user.compila_report_turno(turno, float(ore))
                    try:
                        self.sistema.logged_user.aggiorna_firestore()
                    except Exception as e:
                        print(f"⚠️ Errore salvataggio profilo volontario: {e}")
                
                turno.cambia_stato("Concluso")
                try:
                    turno.aggiorna_firestore()
                except Exception as e:
                    print(f"⚠️ Errore salvataggio turno: {e}")
                
                # Save using Fleet controller
                r = Report(
                    id="REP_" + str(turno.id),
                    kmPercorsi=km_percorsi,
                    noteIntervento=note,
                    oreEffettive=int(ore),
                    turnoEseguito=turno,
                    compilatoDa=self.sistema.logged_user
                )
                self.flotta_controller.salvaReport(r)
                
                # Aggiorna mezzo e chilometraggio totale risultante
                if mezzo_obj:
                    mezzo_obj.aggiornaKm(km_finali)
                    if mezzo_obj.isDismesso(400000):
                        mezzo_obj.radiazioneVeicolo()
                    else:
                        mezzo_obj.libera_mezzo()
                    try:
                        mezzo_obj.aggiorna_firestore()
                    except Exception as e:
                        print(f"⚠️ Errore salvataggio mezzo: {e}")
                
                self.mostra_toast(
                    f"Resoconto registrato! +{km_percorsi:,} km percorsi sul mezzo, {ore} ore accreditate.",
                    "success"
                )
                self.update_ui()

    def azione_esegui_backup(self):
        """RF23 - Esegue manualmente o on-demand un backup periodico dello stato del sistema."""
        success, msg = self.sistema.esegui_backup()
        if success:
            QMessageBox.information(
                self,
                "Backup Periodico Eseguito (RF23)",
                f"✅ Backup di sicurezza completato con successo!\n\nI dati correnti sono stati serializzati e archiviati in:\n{msg}"
            )
            self.mostra_toast("Backup periodico del sistema completato con successo!", "success")
        else:
            QMessageBox.critical(
                self,
                "Errore Backup (RF23)",
                f"❌ Errore durante l'esecuzione del backup:\n{msg}"
            )

    def azione_crea_turno(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        dialog = CreaTurnoDialog(self.sistema.mezzi, self)
        if dialog.exec_():
            t = dialog.get_turno()
            self.turni_controller.creaTurno(t, utente=self.sistema.logged_user)
            self.sistema.aggiungi_turno(t)
            sel_targa = dialog.get_selected_targa()
            if sel_targa:
                mezzo_obj = next((m for m in self.sistema.mezzi if m.targa == sel_targa), None)
                if mezzo_obj:
                    self.flotta_controller.assegnaMezzoATurno(mezzo_obj, t, utente=self.sistema.logged_user)
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
            self.turni_controller.eliminaTurno(turno, utente=self.sistema.logged_user)
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
        self.tbl_mezzi.setHorizontalHeaderLabels(["Targa", "Tipo", "Stato", "Chilometri", "Disponibilità / Turni"])
        self.configura_tabella_responsive(
            self.tbl_mezzi,
            col_widths={0: 110, 1: 130, 2: 150, 3: 110, 4: 170},
            stretch_cols=[2, 4],
            min_section_size=80
        )
        self.tbl_mezzi.verticalHeader().setDefaultSectionSize(36)
        self.tbl_mezzi.verticalHeader().setVisible(False)
        layout.addWidget(self.tbl_mezzi)
        
        if is_referente:
            btn_layout = QHBoxLayout()
            btn_aggiungi = QPushButton("🚐 Aggiungi Nuovo Mezzo")
            btn_aggiungi.clicked.connect(self.azione_aggiungi_mezzo)
            btn_layout.addWidget(btn_aggiungi)
            
            btn_assegna = QPushButton("🔗 Assegna Mezzo a Turno")
            btn_assegna.setStyleSheet("background-color: #00897b; color: white; font-weight: bold;")
            btn_assegna.clicked.connect(self.azione_assegna_mezzo_a_turno)
            btn_layout.addWidget(btn_assegna)

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
            if m.turni_assegnati:
                turni_str = ", ".join([f"{t.data}" for t in m.turni_assegnati])
                disp_str = f"🚑 Assegnato ({turni_str})"
            elif m.disponibile:
                disp_str = "🟢 Disponibile"
            else:
                disp_str = f"🟡 {m.stato}"
            self.tbl_mezzi.setItem(row, 4, QTableWidgetItem(disp_str))
        self.tbl_mezzi.blockSignals(False)

    def azione_assegna_mezzo_a_turno(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        row = self.tbl_mezzi.currentRow()
        preselected = None
        if row >= 0:
            targa = self.tbl_mezzi.item(row, 0).text()
            preselected = next((m for m in self.sistema.mezzi if m.targa == targa), None)
            
        dialog = AssegnaMezzoDialog(self.sistema.mezzi, self.sistema.turni, preselected, self)
        if dialog.exec_():
            mezzo, turno = dialog.get_selected()
            if turno and mezzo:
                self.flotta_controller.assegnaMezzoATurno(mezzo, turno)
                QMessageBox.information(self, "Successo", f"✅ Mezzo {mezzo.targa} assegnato al turno {turno.id} ({turno.data}).")
            elif turno and not mezzo:
                self.flotta_controller.assegnaMezzoATurno(None, turno)
                QMessageBox.information(self, "Successo", f"⚪ Mezzo rimosso dal turno {turno.id}.")
            elif preselected and not turno:
                for t in list(preselected.turni_assegnati):
                    self.flotta_controller.assegnaMezzoATurno(None, t)
                preselected.libera_mezzo()
                QMessageBox.information(self, "Successo", f"🟢 Mezzo {preselected.targa} liberato da tutti i turni.")
            self.update_ui()

    def azione_aggiungi_mezzo(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        dialog = CreaMezzoDialog()
        if dialog.exec_():
            m = dialog.get_mezzo()
            self.flotta_controller.aggiungiMezzo(m, utente=self.sistema.logged_user)
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
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # TabWidget interno per la formazione
        self.tab_formazione_sub = QTabWidget()
        self.tab_formazione_sub.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #1e1e1e;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #cccccc;
                padding: 7px 16px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #c62828;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #383838;
                color: white;
            }
        """)

        # Sub-tab 1: I MIEI CORSI
        sub1 = self._crea_subtab_miei_corsi(is_referente)
        self.tab_formazione_sub.addTab(sub1, "🎓 I Miei Corsi")

        # Sub-tab 2: CATALOGO COMPLETO CORSI CRI
        sub2 = self._crea_subtab_catalogo_corsi(is_referente)
        self.tab_formazione_sub.addTab(sub2, "📚 Catalogo Corsi CRI")

        layout.addWidget(self.tab_formazione_sub)
        return widget

    def _crea_subtab_miei_corsi(self, is_referente):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # 1. Header KPI Cards
        kpi_frame = QFrame()
        kpi_frame.setStyleSheet("background-color: #242424; border: 1px solid #383838; border-radius: 8px;")
        kpi_lay = QHBoxLayout(kpi_frame)
        kpi_lay.setContentsMargins(16, 12, 16, 12)
        kpi_lay.setSpacing(25)

        self.kpi_corsi_eff = QLabel()
        kpi_lay.addWidget(self.kpi_corsi_eff)

        self.kpi_corsi_inc = QLabel()
        kpi_lay.addWidget(self.kpi_corsi_inc)

        self.kpi_corsi_ore = QLabel()
        kpi_lay.addWidget(self.kpi_corsi_ore)

        kpi_lay.addStretch()
        layout.addWidget(kpi_frame)

        # 2. Barra Filtri e Titolo
        filter_bar = QHBoxLayout()
        lbl_sub_titolo = QLabel("<b>🎓 Registro Personale — Corsi Frequenti e in Corso:</b>")
        lbl_sub_titolo.setStyleSheet("font-size: 14px; color: #ffffff;")
        filter_bar.addWidget(lbl_sub_titolo)
        filter_bar.addStretch()

        self.btn_filtro_tutti = QPushButton("Tutti")
        self.btn_filtro_eff = QPushButton("🏆 Solo Effettuati / Superati")
        self.btn_filtro_inc = QPushButton("⏳ Solo Da Svolgere / In Corso")
        for btn in [self.btn_filtro_tutti, self.btn_filtro_eff, self.btn_filtro_inc]:
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d2d;
                    border: 1px solid #444;
                    color: #eee;
                    padding: 6px 14px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:checked {
                    background-color: #c62828;
                    color: white;
                    font-weight: bold;
                    border: 1px solid #e53935;
                }
            """)
        self.btn_filtro_tutti.setChecked(True)
        self.filtro_miei_corsi_stato = "tutti"

        self.btn_filtro_tutti.clicked.connect(lambda: self._imposta_filtro_miei_corsi("tutti"))
        self.btn_filtro_eff.clicked.connect(lambda: self._imposta_filtro_miei_corsi("effettuati"))
        self.btn_filtro_inc.clicked.connect(lambda: self._imposta_filtro_miei_corsi("in_corso"))

        filter_bar.addWidget(self.btn_filtro_tutti)
        filter_bar.addWidget(self.btn_filtro_eff)
        filter_bar.addWidget(self.btn_filtro_inc)
        layout.addLayout(filter_bar)

        # 3. Tabella "I Miei Corsi"
        self.tbl_miei_corsi = QTableWidget(0, 6)
        self.tbl_miei_corsi.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_miei_corsi.setHorizontalHeaderLabels([
            "ID", "Titolo Corso", "Periodo Svolgimento", "Stato Personale", "Qualifica / Brevetto", "Validità / Scadenza"
        ])
        self.configura_tabella_responsive(
            self.tbl_miei_corsi,
            col_widths={0: 75, 1: 180, 2: 195, 3: 175, 4: 160, 5: 145},
            stretch_cols=[1],
            min_section_size=75
        )
        self.tbl_miei_corsi.verticalHeader().setDefaultSectionSize(36)
        self.tbl_miei_corsi.verticalHeader().setVisible(False)
        self.tbl_miei_corsi.doubleClicked.connect(self.azione_dettaglio_mio_corso)
        layout.addWidget(self.tbl_miei_corsi)

        # 4. Barra Azioni sotto tabella
        actions_bar = QHBoxLayout()
        btn_dettagli = QPushButton("📜 Scheda & Attestato (PDF)")
        btn_dettagli.setStyleSheet("background-color: #0d47a1; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        btn_dettagli.clicked.connect(self.azione_dettaglio_mio_corso)
        actions_bar.addWidget(btn_dettagli)

        btn_rinuncia = QPushButton("❌ Rinuncia / Disiscriviti")
        btn_rinuncia.setStyleSheet("background-color: #37474f; color: white; padding: 8px 16px; border-radius: 6px;")
        btn_rinuncia.clicked.connect(self.azione_disiscrivi_corso)
        actions_bar.addWidget(btn_rinuncia)

        actions_bar.addStretch()
        btn_vai_catalogo = QPushButton("🔍 Catalogo Corsi CRI ➔")
        btn_vai_catalogo.setStyleSheet("background-color: #2e7d32; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        btn_vai_catalogo.clicked.connect(lambda: self.tab_formazione_sub.setCurrentIndex(1))
        actions_bar.addWidget(btn_vai_catalogo)

        layout.addLayout(actions_bar)
        self.popola_tabella_miei_corsi()
        return widget

    def _crea_subtab_catalogo_corsi(self, is_referente):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Barra di ricerca e titolo
        search_bar = QHBoxLayout()
        search_bar.addWidget(QLabel("<b>📚 Catalogo Corsi e Certificazioni CRI:</b>"))
        search_bar.addStretch()

        self.txt_cerca_corso = QLineEdit()
        self.txt_cerca_corso.setPlaceholderText("🔍 Cerca per titolo o competenza...")
        self.txt_cerca_corso.setStyleSheet("background-color: #2b2b2b; color: white; padding: 6px 12px; border-radius: 4px; border: 1px solid #444; min-width: 250px;")
        self.txt_cerca_corso.textChanged.connect(self.filtra_catalogo_corsi)
        search_bar.addWidget(self.txt_cerca_corso)
        layout.addLayout(search_bar)

        # Tabella Catalogo Corsi
        self.tbl_corsi = QTableWidget(0, 7)
        if is_referente:
            self.tbl_corsi.setEditTriggers(QAbstractItemView.DoubleClicked)
            # pyrefly: ignore [missing-attribute]
            self.tbl_corsi.itemChanged.connect(self.on_corso_cell_changed)
        else:
            self.tbl_corsi.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_corsi.setHorizontalHeaderLabels(["ID", "Titolo Corso", "Data Inizio", "Data Fine", "Posti", "Stato Corso", "Il Tuo Stato"])
        self.configura_tabella_responsive(
            self.tbl_corsi,
            col_widths={0: 75, 1: 190, 2: 95, 3: 95, 4: 85, 5: 105, 6: 150},
            stretch_cols=[1],
            min_section_size=75
        )
        self.tbl_corsi.verticalHeader().setDefaultSectionSize(36)
        self.tbl_corsi.verticalHeader().setVisible(False)
        self.tbl_corsi.doubleClicked.connect(self.azione_dettaglio_corso_catalogo)
        layout.addWidget(self.tbl_corsi)

        # Azioni Catalogo
        btn_layout = QHBoxLayout()
        btn_info = QPushButton("ℹ️ Programma & Dettagli")
        btn_info.setStyleSheet("background-color: #37474f; color: white; padding: 8px 14px; border-radius: 6px;")
        btn_info.clicked.connect(self.azione_dettaglio_corso_catalogo)
        btn_layout.addWidget(btn_info)

        if not is_referente:
            btn_iscrivi = QPushButton("📝 Iscriviti al Corso Selezionato")
            btn_iscrivi.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
            btn_iscrivi.clicked.connect(self.azione_iscrivi_corso)
            btn_layout.addWidget(btn_iscrivi)
        else:
            btn_crea = QPushButton("🎓 Crea Nuovo Corso")
            btn_crea.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 8px 14px; border-radius: 6px;")
            btn_crea.clicked.connect(self.azione_crea_corso)
            btn_layout.addWidget(btn_crea)

            btn_modifica_corso = QPushButton("✏️ Modifica Corso")
            btn_modifica_corso.setStyleSheet("background-color: #0277bd; color: white; padding: 8px 14px; border-radius: 6px;")
            btn_modifica_corso.clicked.connect(self.azione_modifica_corso)
            btn_layout.addWidget(btn_modifica_corso)

            btn_attesta = QPushButton("🏆 Attesta Certificazione Volontario")
            btn_attesta.setStyleSheet("background-color: #f57f17; color: white; font-weight: bold; padding: 8px 14px; border-radius: 6px;")
            btn_attesta.clicked.connect(self.azione_attesta_partecipazione)
            btn_layout.addWidget(btn_attesta)

            btn_elimina = QPushButton("🗑️ Elimina Corso")
            btn_elimina.setStyleSheet("background-color: #c62828; color: white; padding: 8px 14px; border-radius: 6px;")
            btn_elimina.clicked.connect(self.azione_elimina_corso)
            btn_layout.addWidget(btn_elimina)

        layout.addLayout(btn_layout)
        self.popola_tabella_corsi()
        return widget

    def _imposta_filtro_miei_corsi(self, stato: str):
        self.filtro_miei_corsi_stato = stato
        self.btn_filtro_tutti.setChecked(stato == "tutti")
        self.btn_filtro_eff.setChecked(stato == "effettuati")
        self.btn_filtro_inc.setChecked(stato == "in_corso")
        self.popola_tabella_miei_corsi()

    def popola_tabella_miei_corsi(self):
        user = self.sistema.logged_user
        if not user or not hasattr(self, "tbl_miei_corsi"):
            return
        
        suddivisi = self.formazione_controller.ottieniCorsiSuddivisi(user, self.sistema)
        effettuati = suddivisi["effettuati"]
        in_corso = suddivisi["in_corso"]

        # Aggiorna KPI cards
        tot_ore = sum(getattr(c, "mesiValidita", 1) * 10 for c in effettuati)
        self.kpi_corsi_eff.setText(
            f"<div style='font-size: 11px; color: #a5d6a7; font-weight: bold;'>CORSI EFFETTUATI</div>"
            f"<div style='font-size: 20px; font-weight: bold; color: #4caf50;'>🏆 {len(effettuati)} Conseguiti</div>"
        )
        self.kpi_corsi_inc.setText(
            f"<div style='font-size: 11px; color: #ffe082; font-weight: bold;'>CORSI DA EFFETTUARE</div>"
            f"<div style='font-size: 20px; font-weight: bold; color: #ffa726;'>⏳ {len(in_corso)} In Corso</div>"
        )
        self.kpi_corsi_ore.setText(
            f"<div style='font-size: 11px; color: #90caf9; font-weight: bold;'>MONTE ORE FORMATIVO</div>"
            f"<div style='font-size: 20px; font-weight: bold; color: #42a5f5;'>⏱️ {tot_ore}h Formazione</div>"
        )

        # Filtra corsi in base alla selezione (tutti / effettuati / in_corso)
        if self.filtro_miei_corsi_stato == "effettuati":
            elenco = [(c, "effettuato") for c in effettuati]
        elif self.filtro_miei_corsi_stato == "in_corso":
            elenco = [(c, "in_corso") for c in in_corso]
        else:
            elenco = [(c, "effettuato") for c in effettuati] + [(c, "in_corso") for c in in_corso]

        self.tbl_miei_corsi.setRowCount(0)
        self.miei_corsi_mappa = {}

        for r, (c, st) in enumerate(elenco):
            self.tbl_miei_corsi.insertRow(r)
            self.miei_corsi_mappa[r] = (c, st)

            self.tbl_miei_corsi.setItem(r, 0, QTableWidgetItem(str(c.id)))
            self.tbl_miei_corsi.setItem(r, 1, QTableWidgetItem(str(c.titolo or c.nome)))
            periodo = f"{c.dataInizio} ➔ {c.dataFine}" if (c.dataInizio or c.dataFine) else "In programmazione"
            self.tbl_miei_corsi.setItem(r, 2, QTableWidgetItem(periodo))

            # Badge Stato
            if st == "effettuato":
                item_stato = QTableWidgetItem("🟢 Effettuato / Superato")
                item_stato.setForeground(Qt.green)
            else:
                item_stato = QTableWidgetItem("🟡 Da Svolgere / Iscritto")
                item_stato.setForeground(Qt.yellow)
            self.tbl_miei_corsi.setItem(r, 3, item_stato)

            qualifica = getattr(c, "qualificaRilasciata", "") or c.titolo
            self.tbl_miei_corsi.setItem(r, 4, QTableWidgetItem(qualifica))

            scadenza = getattr(c, "scadenza", "") or "Illimitata"
            self.tbl_miei_corsi.setItem(r, 5, QTableWidgetItem(scadenza))

    def popola_tabella_corsi(self):
        if not hasattr(self, "tbl_corsi"):
            return
        self.tbl_corsi.blockSignals(True)
        self.tbl_corsi.setRowCount(0)

        user = self.sistema.logged_user
        suddivisi = self.formazione_controller.ottieniCorsiSuddivisi(user, self.sistema)
        eff_ids = {str(c.id) for c in suddivisi["effettuati"]}
        inc_ids = {str(c.id) for c in suddivisi["in_corso"]}

        filtro = getattr(self, "txt_cerca_corso", None)
        filtro_txt = filtro.text().strip().lower() if filtro else ""

        for c in self.sistema.corsi:
            titolo = str(c.titolo or c.nome or "")
            if filtro_txt and (filtro_txt not in titolo.lower() and filtro_txt not in str(c.id).lower()):
                continue

            row = self.tbl_corsi.rowCount()
            self.tbl_corsi.insertRow(row)
            self.tbl_corsi.setItem(row, 0, QTableWidgetItem(str(c.id)))
            self.tbl_corsi.setItem(row, 1, QTableWidgetItem(titolo))
            self.tbl_corsi.setItem(row, 2, QTableWidgetItem(str(c.dataInizio or "N/D")))
            self.tbl_corsi.setItem(row, 3, QTableWidgetItem(str(c.dataFine or "N/D")))

            # Posti
            max_p = getattr(c, "maxPartecipanti", 20)
            iscr_str = f"{len(c.partecipanti)} / {max_p}"
            item_posti = QTableWidgetItem(iscr_str)
            item_posti.setTextAlignment(Qt.AlignCenter)
            if c.is_completo():
                item_posti.setForeground(Qt.red)
            self.tbl_corsi.setItem(row, 4, item_posti)

            self.tbl_corsi.setItem(row, 5, QTableWidgetItem(str(c.stato or "Programmato")))

            # Il Tuo Stato
            cid = str(c.id)
            if cid in eff_ids:
                item_st = QTableWidgetItem("🟢 ✅ Già Effettuato")
                item_st.setForeground(Qt.green)
            elif cid in inc_ids:
                item_st = QTableWidgetItem("🟡 ⏳ Iscritto")
                item_st.setForeground(Qt.yellow)
            elif c.is_completo():
                item_st = QTableWidgetItem("🔴 Completo")
                item_st.setForeground(Qt.red)
            else:
                item_st = QTableWidgetItem("⚪ Disponibile")
            self.tbl_corsi.setItem(row, 6, item_st)

        self.tbl_corsi.blockSignals(False)

    def filtra_catalogo_corsi(self):
        self.popola_tabella_corsi()

    def azione_dettaglio_mio_corso(self):
        row = self.tbl_miei_corsi.currentRow()
        if row < 0 or row not in getattr(self, "miei_corsi_mappa", {}):
            QMessageBox.warning(self, "Selezione Richiesta", "Seleziona prima un corso dalla tabella 'I Miei Corsi'.")
            return
        c, st = self.miei_corsi_mappa[row]
        dlg = DettaglioCorsoDialog(c, self.sistema.logged_user, st, self.formazione_controller, self)
        if dlg.exec_() and dlg.cambiamento_effettuato:
            self.update_ui()

    def azione_dettaglio_corso_catalogo(self):
        row = self.tbl_corsi.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selezione Richiesta", "Seleziona prima un corso dalla tabella del catalogo.")
            return
        id_corso = self.tbl_corsi.item(row, 0).text()
        c = next((corso for corso in self.sistema.corsi if str(corso.id) == id_corso), None)
        if not c:
            return
        user = self.sistema.logged_user
        suddivisi = self.formazione_controller.ottieniCorsiSuddivisi(user, self.sistema)
        if any(str(x.id) == str(c.id) for x in suddivisi["effettuati"]):
            st = "effettuato"
        elif any(str(x.id) == str(c.id) for x in suddivisi["in_corso"]):
            st = "in_corso"
        else:
            st = "disponibile"
        dlg = DettaglioCorsoDialog(c, user, st, self.formazione_controller, self)
        if dlg.exec_() and dlg.cambiamento_effettuato:
            self.update_ui()

    def azione_disiscrivi_corso(self):
        row = self.tbl_miei_corsi.currentRow()
        if row < 0 or row not in getattr(self, "miei_corsi_mappa", {}):
            QMessageBox.warning(self, "Selezione Richiesta", "Seleziona un corso da rinunciare dalla tabella 'I Miei Corsi'.")
            return
        c, st = self.miei_corsi_mappa[row]
        if st == "effettuato":
            QMessageBox.information(self, "Informazione", "Non puoi disiscriverti da un corso che hai già completato ed effettuato!")
            return

        risposta = QMessageBox.question(
            self,
            "Conferma Rinuncia",
            f"Sei sicuro di voler rinunciare all'iscrizione per il corso '{c.titolo or c.nome}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if risposta == QMessageBox.Yes:
            self.formazione_controller.disiscriviVolontario(self.sistema.logged_user, c.id)
            self.mostra_toast(f"✅ Disiscritto dal corso {c.titolo}", tipo="info")
            self.update_ui()

    def azione_iscrivi_corso(self):
        row = self.tbl_corsi.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un corso dal catalogo.")
            return
        id_corso = self.tbl_corsi.item(row, 0).text()
        c = next((corso for corso in self.sistema.corsi if str(corso.id) == id_corso), None)
        
        if c:
            suddivisi = self.formazione_controller.ottieniCorsiSuddivisi(self.sistema.logged_user, self.sistema)
            if any(str(x.id) == str(c.id) for x in suddivisi["effettuati"]):
                QMessageBox.warning(self, "Attenzione", "Hai già completato ed effettuato questo corso con certificazione!")
                return
            if any(str(x.id) == str(c.id) for x in suddivisi["in_corso"]):
                QMessageBox.warning(self, "Attenzione", "Sei già iscritto a questo corso!")
                return

            self.formazione_controller.iscriviVolontario(self.sistema.logged_user, c.id)
            if hasattr(self.sistema.logged_user, "iscriviti_al_corso"):
                self.sistema.logged_user.iscriviti_al_corso(c)
            if hasattr(self.sistema.logged_user, "aggiorna_firestore"):
                try:
                    self.sistema.logged_user.aggiorna_firestore()
                except Exception:
                    pass
            self.mostra_toast(f"✅ Iscrizione confermata per: {c.titolo}", tipo="success")
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
            self.mostra_toast("✅ Corso aggiunto al catalogo di formazione.", tipo="success")
            self.update_ui()

    def azione_elimina_corso(self):
        if not self.sistema.logged_user or self.sistema.logged_user.ruolo != "referente":
            QMessageBox.critical(self, "Accesso Negato", "❌ Operazione consentita solo ai referenti.")
            return
        row = self.tbl_corsi.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona il corso da eliminare.")
            return
        id_corso = self.tbl_corsi.item(row, 0).text()
        c = next((corso for corso in self.sistema.corsi if str(corso.id) == id_corso), None)
        if not c:
            return
        risposta = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare definitivamente il corso '{c.titolo}' dal catalogo?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if risposta == QMessageBox.Yes:
            self.formazione_controller.eliminaCorso(c.id)
            if c in self.sistema.corsi:
                self.sistema.corsi.remove(c)
            self.mostra_toast(f"🗑️ Corso '{c.titolo}' eliminato.", tipo="warning")
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
        c = next((corso for corso in self.sistema.corsi if str(corso.id) == id_corso), None)
        
        if c:
            nomi = [v.get_nome_completo() for v in self.sistema.volontari if v.ruolo.lower() == "volontario"]
            item, ok = QInputDialog.getItem(self, "Seleziona Volontario", "Scegli il volontario da certificare:", nomi, 0, False)
            if ok and item:
                volontario = next((v for v in self.sistema.volontari if v.get_nome_completo() == item), None)
                if volontario:
                    self.formazione_controller.attestaPartecipazione(c.id, [volontario])
                    if c not in volontario.corsi_frequentati:
                        volontario.corsi_frequentati.append(c)
                    if c in volontario.formazione:
                        volontario.formazione.remove(c)
                    volontario.aggiungiQualifica(c.titolo)
                    volontario.aggiungiOreServizio(int(getattr(c, "mesiValidita", 1) * 10))
                    volontario.aggiorna_firestore()
                    self.mostra_toast(f"🏆 Brevetto '{c.titolo}' rilasciato a {volontario.get_nome_completo()}!", tipo="success")
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
        dialog = ModificaTurnoDialog(turno, self.sistema.mezzi, self)
        if dialog.exec_():
            dialog.apply_to(turno, self.flotta_controller, self.sistema.mezzi)
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
        if col == 0 or col == 7: # ID or Iscritti cannot be edited directly
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
            # Colonna Veicolo
            targa_clean = new_val.replace("🚑", "").strip()
            if not targa_clean or targa_clean.lower() in ["da assegnare", "non assegnato", "nessuno", ""]:
                self.flotta_controller.assegnaMezzoATurno(None, turno)
            else:
                mezzo_obj = next((m for m in self.sistema.mezzi if m.targa.strip().upper() == targa_clean.upper()), None)
                if mezzo_obj:
                    self.flotta_controller.assegnaMezzoATurno(mezzo_obj, turno)
                else:
                    QMessageBox.warning(self, "Attenzione", f"Nessun veicolo con targa '{targa_clean}' trovato nella flotta.")
                    self.popola_tabella_turni_admin()
                    return
        elif col == 6:
            try:
                turno.personeRichieste = int(new_val)
            except ValueError:
                QMessageBox.warning(self, "Errore", "Persone richieste deve essere un numero intero.")
                self.popola_tabella_turni_admin()
                return
        elif col == 8:
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
            try:
                num = int(new_val.split("/")[1] if "/" in new_val else new_val)
                corso.maxPartecipanti = max(1, num)
            except Exception:
                pass
        elif col == 5:
            corso.stato = new_val
            
        try:
            corso.aggiorna_firestore()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile salvare su Firebase: {e}")
    def crea_tab_rubrica(self, is_referente):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Header / Barra comandi superiore
        top_bar = QHBoxLayout()
        lbl_info = QLabel("<h3 style='color: white; margin: 0;'>👥 Rubrica e Anagrafica Personale CRI</h3>")
        top_bar.addWidget(lbl_info)
        top_bar.addStretch()

        # Barra di ricerca
        self.txt_cerca_volontario = QLineEdit()
        self.txt_cerca_volontario.setPlaceholderText("🔍 Cerca per nome, cognome, CF o ruolo...")
        self.txt_cerca_volontario.setFixedWidth(280)
        self.txt_cerca_volontario.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px 10px;
            }
        """)
        self.txt_cerca_volontario.textChanged.connect(self.filtra_volontari)
        top_bar.addWidget(self.txt_cerca_volontario)
        layout.addLayout(top_bar)

        # Tabella Volontari
        self.tbl_volontari = QTableWidget()
        self.tbl_volontari.setColumnCount(7)
        self.tbl_volontari.setHorizontalHeaderLabels([
            "Codice Fiscale", "Nominativo", "Ruolo", "Email", "Telefono", "Patenti", "Qualifiche / Specializzazioni"
        ])
        self.configura_tabella_responsive(
            self.tbl_volontari,
            col_widths={0: 150, 1: 150, 2: 110, 3: 160, 4: 110, 5: 100, 6: 200},
            stretch_cols=[1, 6],
            min_section_size=80
        )
        self.tbl_volontari.verticalHeader().setDefaultSectionSize(36)
        self.tbl_volontari.verticalHeader().setVisible(False)
        self.tbl_volontari.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_volontari.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_volontari.doubleClicked.connect(self.apri_scheda_volontario_selezionato)
        layout.addWidget(self.tbl_volontari)

        # Barra Azioni Inferiore
        bot_bar = QHBoxLayout()
        btn_scheda = QPushButton("👁️ Visualizza Scheda Dettaglio")
        btn_scheda.setStyleSheet("background-color: #37474f; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        btn_scheda.clicked.connect(self.apri_scheda_volontario_selezionato)
        bot_bar.addWidget(btn_scheda)

        btn_rep = QPushButton("📄 Esporta Report Personale")
        btn_rep.setStyleSheet("background-color: #0277bd; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        btn_rep.clicked.connect(self.apri_report_volontario_selezionato)
        bot_bar.addWidget(btn_rep)

        if is_referente:
            btn_ruolo = QPushButton("🔄 Modifica Ruolo Membro")
            btn_ruolo.setStyleSheet("background-color: #c62828; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
            btn_ruolo.clicked.connect(self.cambia_ruolo_volontario_selezionato)
            bot_bar.addWidget(btn_ruolo)

            btn_spec = QPushButton("➕ Aggiungi Qualifica / Spec.")
            btn_spec.setStyleSheet("background-color: #2e7d32; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
            btn_spec.clicked.connect(self.aggiungi_spec_volontario_selezionato)
            bot_bar.addWidget(btn_spec)

        bot_bar.addStretch()
        btn_refresh = QPushButton("🔄 Aggiorna Elenco")
        btn_refresh.clicked.connect(lambda: self.popola_tabella_volontari())
        bot_bar.addWidget(btn_refresh)

        layout.addLayout(bot_bar)

        self.popola_tabella_volontari()
        return widget

    def popola_tabella_volontari(self, filtro=""):
        if not hasattr(self, "tbl_volontari") or self.tbl_volontari is None:
            return
        membri = self.sistema.volontari
        filtro_lower = filtro.strip().lower()
        if filtro_lower:
            membri = [
                m for m in membri
                if filtro_lower in m.get_nome_completo().lower()
                or filtro_lower in str(m.cod_fiscale).lower()
                or filtro_lower in getattr(m, "ruolo", "").lower()
                or any(filtro_lower in str(p).lower() for p in getattr(m, "patenti", []))
                or any(filtro_lower in str(q).lower() for q in getattr(m, "qualifiche", []))
                or any(filtro_lower in str(s).lower() for s in getattr(m, "specializzazioni", []))
            ]

        self.tbl_volontari.setRowCount(len(membri))
        for r, m in enumerate(membri):
            self.tbl_volontari.setItem(r, 0, QTableWidgetItem(str(m.cod_fiscale)))
            self.tbl_volontari.setItem(r, 1, QTableWidgetItem(m.get_nome_completo()))

            ruolo_cap = str(getattr(m, "ruolo", "volontario")).capitalize()
            self.tbl_volontari.setItem(r, 2, QTableWidgetItem(ruolo_cap))
            self.tbl_volontari.setItem(r, 3, QTableWidgetItem(getattr(m, "email", "") or ""))
            self.tbl_volontari.setItem(r, 4, QTableWidgetItem(getattr(m, "telefono", "") or ""))

            patenti_txt = ", ".join(getattr(m, "patenti", [])) or "-"
            self.tbl_volontari.setItem(r, 5, QTableWidgetItem(patenti_txt))

            qual_and_spec = list(getattr(m, "qualifiche", []))
            if hasattr(m, "specializzazioni") and m.specializzazioni:
                qual_and_spec.extend([f"🩺 {s}" for s in m.specializzazioni])
            spec_txt = ", ".join(qual_and_spec) or "-"
            self.tbl_volontari.setItem(r, 6, QTableWidgetItem(spec_txt))

    def filtra_volontari(self, testo):
        self.popola_tabella_volontari(testo)

    def get_volontario_selezionato(self):
        if not hasattr(self, "tbl_volontari") or self.tbl_volontari is None:
            return None
        row = self.tbl_volontari.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un membro dalla tabella.")
            return None
        cf_item = self.tbl_volontari.item(row, 0)
        if not cf_item:
            return None
        cf = cf_item.text().strip()
        return self.sistema.get_volontario(cf)

    def apri_scheda_volontario_selezionato(self):
        v = self.get_volontario_selezionato()
        if v:
            is_referente = isinstance(self.sistema.logged_user, Referente) or getattr(self.sistema.logged_user, "ruolo", "").lower() == "referente"
            dlg = SchedaVolontarioDialog(v, self.sistema, is_referente, self)
            dlg.exec_()
            self.popola_tabella_volontari()

    def apri_report_volontario_selezionato(self):
        v = self.get_volontario_selezionato()
        if v:
            testo = self.sistema.stampa_report_volontario(v.cod_fiscale)
            dlg = VisualizzaReportDialog(f"Report Attività — {v.get_nome_completo()}", testo, v, self)
            dlg.exec_()

    def cambia_ruolo_volontario_selezionato(self):
        v = self.get_volontario_selezionato()
        if not v:
            return
        opzioni = ["volontario", "referente"]
        ruolo_attuale = str(getattr(v, "ruolo", "volontario")).lower()
        idx_default = opzioni.index(ruolo_attuale) if ruolo_attuale in opzioni else 0
        nuovo, ok = QInputDialog.getItem(self, "Modifica Ruolo Membro", f"Nuovo ruolo per {v.get_nome_completo()}:", opzioni, idx_default, False)
        if ok and nuovo:
            v.ruolo = nuovo
            try:
                v.aggiorna_firestore()
                QMessageBox.information(self, "Successo", f"✅ Ruolo aggiornato a '{nuovo}'.")
                self.popola_tabella_volontari()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"❌ Errore salvataggio: {e}")

    def aggiungi_spec_volontario_selezionato(self):
        v = self.get_volontario_selezionato()
        if not v:
            return
        opzioni_tipo = ["Patente", "Qualifica", "Specializzazione Sanitaria"]
        tipo, ok = QInputDialog.getItem(self, "Tipo Elemento", "Cosa desideri aggiungere?", opzioni_tipo, 0, False)
        if not ok or not tipo:
            return
        valore, ok_v = QInputDialog.getText(self, f"Aggiungi {tipo}", f"Nome della {tipo.lower()}:")
        if ok_v and valore.strip():
            valore_clean = valore.strip()
            if tipo == "Patente":
                if not hasattr(v, "patenti") or v.patenti is None:
                    v.patenti = []
                if valore_clean not in v.patenti:
                    v.patenti.append(valore_clean)
            elif tipo == "Qualifica":
                if not hasattr(v, "qualifiche") or v.qualifiche is None:
                    v.qualifiche = []
                if valore_clean not in v.qualifiche:
                    v.qualifiche.append(valore_clean)
            else:
                if not hasattr(v, "specializzazioni") or v.specializzazioni is None:
                    v.specializzazioni = []
                if valore_clean not in v.specializzazioni:
                    v.specializzazioni.append(valore_clean)
            try:
                v.aggiorna_firestore()
                QMessageBox.information(self, "Successo", f"✅ {tipo} '{valore_clean}' aggiunta!")
                self.popola_tabella_volontari()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"❌ Errore salvataggio: {e}")

    def apri_report_personale(self):
        user = self.sistema.logged_user
        if user:
            testo = self.sistema.stampa_report_volontario(user.cod_fiscale)
            dlg = VisualizzaReportDialog(f"Report Personale — {user.get_nome_completo()}", testo, user, self)
            dlg.exec_()

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
            comitato_appartenenza="CRI Roma",
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
            comitato_appartenenza="CRI Roma",
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
