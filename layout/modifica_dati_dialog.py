import os
import shutil
import subprocess
import sys
import hashlib
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QCheckBox, QHBoxLayout, QWidget, QDateEdit, QFileDialog,
    QScrollArea, QFrame, QGridLayout, QFormLayout, QComboBox
)
from PyQt5.QtCore import Qt, QDate





class ModificaDatiDialog(QDialog):
    """
    Finestra per la modifica del profilo personale e operativo del volontario CRI.
    Completamente responsive con ScrollArea centrale e Sticky Footer fisso in basso
    per garantire la visibilità costante del pulsante di salvataggio su qualsiasi schermo.
    """
    def __init__(self, volontario, parent=None):
        super().__init__(parent)
        self.volontario = volontario
        self.setWindowTitle("👤 Profilo Operativo & Dati Personali — Croce Rossa Italiana")
        self.resize(650, 720)
        self.setMinimumSize(480, 520)

        # Stile moderno dark
        self.setStyleSheet("""
            QDialog {
                background-color: #141414;
            }
            QWidget {
                color: #e0e0e0;
                font-family: "Helvetica Neue", Arial, sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QLineEdit, QDateEdit, QComboBox {
                background-color: #242424;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 7px 10px;
                color: #ffffff;
                min-height: 20px;
                font-size: 13px;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1px solid #e53935;
                background-color: #2a2a2a;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                color: #ffffff;
                selection-background-color: #e53935;
                selection-color: #ffffff;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 4px;
            }
            QCheckBox {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #555555;
                background-color: #242424;
            }
            QCheckBox::indicator:hover {
                border-color: #e53935;
            }
            QCheckBox::indicator:checked {
                background-color: #e53935;
                border-color: #ef5350;
            }
        """)

        # Layout radice della finestra (senza margini per contenere header, scroll e sticky footer)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Header Fisso Superiore
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #2e2e2e;")
        h_lay = QVBoxLayout(header_widget)
        h_lay.setContentsMargins(24, 16, 24, 16)
        h_lay.setSpacing(4)
        
        lbl_title = QLabel("👤 Profilo Operativo & Dati Personali")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        lbl_subtitle = QLabel("Gestisci anagrafica, documento di guida (PDF) ed estrapolazione dati patente")
        lbl_subtitle.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        h_lay.addWidget(lbl_title)
        h_lay.addWidget(lbl_subtitle)
        root_layout.addWidget(header_widget)

        # 2. Area Scorrevole Centrale (QScrollArea per evitare qualsiasi taglio su schermi compatti)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #141414;
                border: none;
            }
            QScrollBar:vertical {
                background: #141414;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #333333;
                min-height: 25px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #555555;
            }
        """)

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #141414;")
        
        # Max-width wrapper: su schermi larghi mantiene il form compatto e centrato
        outer_content_layout = QHBoxLayout(content_widget)
        outer_content_layout.setContentsMargins(15, 15, 15, 15)
        outer_content_layout.setAlignment(Qt.AlignHCenter)

        inner_card = QWidget()
        inner_card.setMaximumWidth(700)
        inner_layout = QVBoxLayout(inner_card)
        inner_layout.setContentsMargins(10, 5, 10, 15)
        inner_layout.setSpacing(16)

        # --- SEZIONE 1: Dati Anagrafici & Contatti ---
        sec1 = self._crea_card("👤 Dati Anagrafici & Recapiti")
        s1_lay = QGridLayout()
        s1_lay.setSpacing(12)

        self.nome_edit = QLineEdit(volontario.nome)
        self.cognome_edit = QLineEdit(volontario.cognome)
        self.cf_edit = QLineEdit(str(getattr(volontario, 'cod_fiscale', '')))
        self.cf_edit.setPlaceholderText("Es. RSSMRA85M01H501Z (16 caratteri)")
        self.email_edit = QLineEdit(volontario.email)

        self.nascita_edit = QDateEdit()
        self.nascita_edit.setCalendarPopup(True)
        self.nascita_edit.setDisplayFormat("dd/MM/yyyy")
        orig_date = volontario.nascita or ""
        qdate = QDate.fromString(orig_date, "dd/MM/yyyy")
        if not qdate.isValid():
            qdate = QDate.fromString(orig_date, "yyyy-MM-dd")
        if not qdate.isValid():
            qdate = QDate.currentDate().addYears(-20)
        self.nascita_edit.setDate(qdate)

        self.telefono_edit = QLineEdit(volontario.telefono)

        # Riga 0
        s1_lay.addWidget(QLabel("<b>Nome:</b>"), 0, 0)
        s1_lay.addWidget(self.nome_edit, 1, 0)
        s1_lay.addWidget(QLabel("<b>Cognome:</b>"), 0, 1)
        s1_lay.addWidget(self.cognome_edit, 1, 1)

        # Riga 1
        s1_lay.addWidget(QLabel("<b>Codice Fiscale:</b>"), 2, 0)
        s1_lay.addWidget(self.cf_edit, 3, 0)
        s1_lay.addWidget(QLabel("<b>Email:</b>"), 2, 1)
        s1_lay.addWidget(self.email_edit, 3, 1)

        # Riga 2
        s1_lay.addWidget(QLabel("<b>Data di Nascita:</b>"), 4, 0)
        s1_lay.addWidget(self.nascita_edit, 5, 0)
        s1_lay.addWidget(QLabel("<b>Telefono:</b>"), 4, 1)
        s1_lay.addWidget(self.telefono_edit, 5, 1)

        # Riga 3: Ruolo Operativo
        self.ruolo_combo = QComboBox()
        self.ruolo_combo.addItem("🚑 Volontario Operativo", "volontario")
        self.ruolo_combo.addItem("📋 Referente / Coordinatore", "referente")

        ruolo_attuale = str(getattr(volontario, "ruolo", "volontario") or "volontario").lower()
        idx_r = self.ruolo_combo.findData(ruolo_attuale)
        if idx_r >= 0:
            self.ruolo_combo.setCurrentIndex(idx_r)

        s1_lay.addWidget(QLabel("<b>Ruolo Operativo nel Sistema:</b>"), 6, 0)
        s1_lay.addWidget(self.ruolo_combo, 7, 0, 1, 2)

        sec1.layout().addLayout(s1_lay)
        inner_layout.addWidget(sec1)

        # --- SEZIONE 2: Patente di Guida & Documento Allegato ---
        sec2 = self._crea_card("🚗 Patente di Guida & Documento Allegato")
        s2_lay = QVBoxLayout()
        s2_lay.setSpacing(14)

        # 1. Box Caricamento & Estrapolazione Dati da PDF
        pdf_box = QFrame()
        pdf_box.setStyleSheet("background-color: #0f1e33; border: 1px solid #1e3f66; border-radius: 8px;")
        pdf_box_layout = QVBoxLayout(pdf_box)
        pdf_box_layout.setContentsMargins(16, 14, 16, 14)
        pdf_box_layout.setSpacing(10)

        pdf_head = QHBoxLayout()
        lbl_pdf_t = QLabel("📄 <b>Documento Patente (PDF o Scansione)</b>")
        lbl_pdf_t.setStyleSheet("color: #64b5f6; font-size: 13px; font-weight: bold; border: none; background: transparent;")
        pdf_head.addWidget(lbl_pdf_t)
        pdf_head.addStretch()

        self.btn_carica_pdf = QPushButton("📂 Allega PDF ed Estrapola Dati")
        self.btn_carica_pdf.setToolTip("Seleziona il PDF o la scansione della patente: il sistema convalidata il file ed estrapolerà i dati in automatico.")
        self.btn_carica_pdf.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                border: 1px solid #0055aa;
            }
            QPushButton:hover {
                background-color: #0077ee;
            }
            QPushButton:pressed {
                background-color: #004499;
            }
        """)
        self.btn_carica_pdf.clicked.connect(lambda: self.carica_pdf_patente())
        pdf_head.addWidget(self.btn_carica_pdf)
        pdf_box_layout.addLayout(pdf_head)

        lbl_pdf_hint = QLabel("💡 <i>Allegando il PDF della tua patente (digitale o scansionato), il sistema convalidata il documento ed estrapola in tempo reale numero di patente, scadenza e categorie di guida.</i>")
        lbl_pdf_hint.setStyleSheet("color: #90caf9; font-size: 11px; border: none; background: transparent;")
        lbl_pdf_hint.setWordWrap(True)
        pdf_box_layout.addWidget(lbl_pdf_hint)

        pdf_status_row = QHBoxLayout()
        self.lbl_pdf_status = QLabel()
        pdf_status_row.addWidget(self.lbl_pdf_status)
        pdf_status_row.addStretch()

        self.btn_view_pdf = QPushButton("👁️ Visualizza PDF Patente")
        self.btn_view_pdf.setStyleSheet("""
            QPushButton {
                background-color: #0288d1;
                color: white;
                padding: 6px 14px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #039be5;
            }
        """)
        self.btn_view_pdf.clicked.connect(self.visualizza_pdf_patente)
        has_pdf = self.ha_pdf_valido()
        self.btn_view_pdf.setVisible(has_pdf)
        pdf_status_row.addWidget(self.btn_view_pdf)
        pdf_box_layout.addLayout(pdf_status_row)

        s2_lay.addWidget(pdf_box)

        # 2. Campi Dati Patente (Estrapolati dal PDF o modificabili manualmente)
        patente_fields_box = QFrame()
        patente_fields_box.setStyleSheet("background-color: #1a1a1a; border: 1px solid #2d2d2d; border-radius: 8px;")
        pf_lay = QGridLayout(patente_fields_box)
        pf_lay.setContentsMargins(14, 14, 14, 14)
        pf_lay.setSpacing(12)

        # Riga 0: Numero Patente & Data Scadenza
        pf_lay.addWidget(QLabel("<b>Numero di Patente:</b>"), 0, 0)
        self.edit_numero_patente = QLineEdit(getattr(volontario, "numero_patente", "") or "")
        self.edit_numero_patente.setPlaceholderText("Es. U1482910A (estrapolato da PDF o manuale)")
        pf_lay.addWidget(self.edit_numero_patente, 1, 0)

        pf_lay.addWidget(QLabel("<b>Data di Scadenza Patente:</b>"), 0, 1)
        self.edit_scadenza_patente = QDateEdit()
        self.edit_scadenza_patente.setCalendarPopup(True)
        self.edit_scadenza_patente.setDisplayFormat("dd/MM/yyyy")
        scad_str = getattr(volontario, "scadenza_patente", "") or ""
        qscad = QDate.fromString(scad_str, "yyyy-MM-dd")
        if not qscad.isValid():
            qscad = QDate.fromString(scad_str, "dd/MM/yyyy")
        if not qscad.isValid():
            qscad = QDate.currentDate().addYears(10)
        self.edit_scadenza_patente.setDate(qscad)
        pf_lay.addWidget(self.edit_scadenza_patente, 1, 1)

        s2_lay.addWidget(patente_fields_box)

        # 3. Checkbox Categorie Abilitate
        s2_lay.addWidget(QLabel("<b>Categorie di Guida Abilitate nel Profilo:</b>"))
        
        self.patenti_pdf = dict(getattr(volontario, 'patenti_pdf', {}))
        self._updating_checkbox = False
        self.patente_checkboxes = {}
        
        patente_widget = QWidget()
        patente_layout = QHBoxLayout(patente_widget)
        patente_layout.setContentsMargins(0, 0, 0, 0)
        patente_layout.setSpacing(16)
        
        for p in ["B", "C", "D", "E"]:
            cb = QCheckBox(f"Patente {p}")
            has_p = p in (volontario.patenti or []) or p.lower() in [val.lower() for val in (volontario.patenti or [])]
            cb.setChecked(has_p)
            cb.toggled.connect(lambda checked, pat=p, checkbox=cb: self.on_patente_toggled(pat, checkbox, checked))
            patente_layout.addWidget(cb)
            self.patente_checkboxes[p] = cb
        patente_layout.addStretch()
        s2_lay.addWidget(patente_widget)

        self.aggiorna_stato_pdf()
        sec2.layout().addLayout(s2_lay)
        inner_layout.addWidget(sec2)

        # --- SEZIONE 3: Curriculum Vitae (PDF) ---
        sec3 = self._crea_card("📄 Curriculum Vitae (PDF)")
        cv_layout = QHBoxLayout()
        cv_layout.setContentsMargins(0, 0, 0, 0)
        cv_layout.setSpacing(10)
        
        has_cv = bool(volontario.curriculum and str(volontario.curriculum).endswith(".pdf"))
        cv_status = "Stato CV: ✅ Caricato regolarmente" if has_cv else "Stato CV: ⚪ Non caricato"
        self.lbl_cv_status = QLabel(cv_status)
        self.lbl_cv_status.setStyleSheet("color: #81c784;" if has_cv else "color: #aaaaaa;")
        cv_layout.addWidget(self.lbl_cv_status)
        cv_layout.addStretch()

        self.btn_carica_cv = QPushButton("📂 Carica CV PDF")
        self.btn_carica_cv.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                border: 1px solid #444;
                color: #eee;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #383838;
            }
        """)
        self.btn_carica_cv.clicked.connect(self.carica_cv_pdf)
        cv_layout.addWidget(self.btn_carica_cv)
        
        self.btn_view_cv = QPushButton("👁️ Vedi CV PDF")
        self.btn_view_cv.setStyleSheet("""
            QPushButton {
                background-color: #0288d1;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #039be5;
            }
        """)
        self.btn_view_cv.clicked.connect(self.visualizza_cv_pdf)
        self.btn_view_cv.setVisible(has_cv)
        cv_layout.addWidget(self.btn_view_cv)

        sec3.layout().addLayout(cv_layout)
        inner_layout.addWidget(sec3)

        # --- SEZIONE 4: Compagnia e Disponibilità ---
        sec4 = self._crea_card("🏢 Compagnia e Disponibilità Operativa")
        s4_lay = QVBoxLayout()
        s4_lay.setSpacing(10)

        s4_lay.addWidget(QLabel("<b>Compagnia di Appartenenza:</b>"))
        self.compagnia_edit = QLineEdit(volontario.compagnia_appartenenza)
        s4_lay.addWidget(self.compagnia_edit)

        s4_lay.addWidget(QLabel("<b>Giorni di Disponibilità Operativa (separati da virgola):</b>"))
        self.disponibilita_edit = QLineEdit(", ".join(volontario.disponibilita))
        self.disponibilita_edit.setPlaceholderText("Es. lunedì, mercoledì, sabato pomeriggio")
        s4_lay.addWidget(self.disponibilita_edit)

        sec4.layout().addLayout(s4_lay)
        inner_layout.addWidget(sec4)

        outer_content_layout.addWidget(inner_card)
        scroll_area.setWidget(content_widget)
        root_layout.addWidget(scroll_area, 1)

        # 3. Sticky Footer Fisso Inferiore (SEMPRE VISIBILE SU QUALSIASI SCHERMO!)
        footer_widget = QWidget()
        footer_widget.setStyleSheet("background-color: #181818; border-top: 1px solid #2e2e2e;")
        foot_lay = QHBoxLayout(footer_widget)
        foot_lay.setContentsMargins(24, 12, 24, 12)
        foot_lay.setSpacing(12)

        lbl_foot_hint = QLabel("💡 Tutte le modifiche vengono sincronizzate con il database centrale CRI")
        lbl_foot_hint.setStyleSheet("color: #777777; font-size: 12px;")
        foot_lay.addWidget(lbl_foot_hint)
        foot_lay.addStretch()

        btn_annulla = QPushButton("Annulla")
        btn_annulla.setStyleSheet("""
            QPushButton {
                background-color: #2e2e2e;
                color: #ffffff;
                font-weight: bold;
                padding: 9px 20px;
                border-radius: 6px;
                border: 1px solid #444444;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3e3e3e;
            }
        """)
        btn_annulla.clicked.connect(self.reject)
        foot_lay.addWidget(btn_annulla)

        self.salva_btn = QPushButton("💾 Salva Dati")
        self.salva_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: #ffffff;
                font-weight: bold;
                padding: 9px 26px;
                border-radius: 6px;
                border: 1px solid #1b5e20;
                font-size: 13px;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:pressed {
                background-color: #1b5e20;
            }
        """)
        self.salva_btn.clicked.connect(self.salva_dati)
        foot_lay.addWidget(self.salva_btn)

        root_layout.addWidget(footer_widget)

    def _crea_card(self, titolo: str) -> QFrame:
        """Crea una sezione a scheda con stile scuro, bordo sottile e titolo elegante."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1c1c1c;
                border: 1px solid #2e2e2e;
                border-radius: 8px;
            }
        """)
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(18, 14, 18, 16)
        c_lay.setSpacing(10)

        lbl = QLabel(f"<b>{titolo}</b>")
        lbl.setStyleSheet("font-size: 14px; color: #ff5252; border: none; background: transparent; margin-bottom: 2px;")
        c_lay.addWidget(lbl)
        return card

    def carica_cv_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona PDF Curriculum", "", "PDF Files (*.pdf)")
        if file_path:
            dest_dir = os.path.abspath("curricula_pdf")
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            dest_path = os.path.join(dest_dir, f"{self.volontario.cod_fiscale}_curriculum.pdf")
            try:
                shutil.copy(file_path, dest_path)
                self.volontario.curriculum = f"curricula_pdf/{self.volontario.cod_fiscale}_curriculum.pdf"
                self.lbl_cv_status.setText("Stato CV: ✅ Caricato regolarmente")
                self.lbl_cv_status.setStyleSheet("color: #81c784;")
                self.btn_view_cv.setVisible(True)
                QMessageBox.information(self, "Successo", "✅ Curriculum Vitae PDF caricato correttamente.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile salvare il file: {e}")

    def visualizza_cv_pdf(self):
        if not getattr(self.volontario, "curriculum", None):
            return
        path = os.path.abspath(self.volontario.curriculum)
        if os.path.exists(path):
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
            QMessageBox.warning(self, "Errore", "Impossibile trovare il file PDF del curriculum.")


    def ha_pdf_valido(self, patente=None) -> bool:
        """Verifica se per una data patente esiste un documento PDF valido e integro."""
        from pdf_validator import valida_pdf_patente

        if patente and patente in getattr(self, "patenti_pdf", {}):
            path = self.patenti_pdf[patente]
            if path and os.path.exists(os.path.abspath(path)):
                valido, _ = valida_pdf_patente(path)
                if valido:
                    return True

        gen_path = getattr(self.volontario, "patente_pdf_path", "")
        if gen_path and os.path.exists(os.path.abspath(gen_path)):
            valido, _ = valida_pdf_patente(gen_path)
            if valido:
                return True

        return False

    def on_patente_toggled(self, pat: str, cb: QCheckBox, checked: bool):
        if getattr(self, "_updating_checkbox", False):
            return

        if checked:
            if not self.ha_pdf_valido(pat):
                risp = QMessageBox.question(
                    self,
                    "📂 Documento Richiesto",
                    f"Per abilitare la patente '<b>{pat}</b>' è necessario allegare il relativo documento PDF.\n\n"
                    f"Desideri selezionare il file PDF adesso per estrapolare automaticamente i dati?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if risp == QMessageBox.Yes:
                    caricato = self.carica_pdf_patente(patente_target=pat)
                    if not caricato:
                        self._updating_checkbox = True
                        cb.setChecked(False)
                        self._updating_checkbox = False
                else:
                    self._updating_checkbox = True
                    cb.setChecked(False)
                    self._updating_checkbox = False
        self.aggiorna_stato_pdf()

    def aggiorna_stato_pdf(self):
        has_pdf = self.ha_pdf_valido()
        num_pat = getattr(self.volontario, "numero_patente", "") or (self.edit_numero_patente.text().strip() if hasattr(self, "edit_numero_patente") else "")
        if has_pdf:
            status_text = f"Documento: ✅ PDF Patente allegato e verificato (N. {num_pat or 'Registrato'})"
            self.lbl_pdf_status.setText(status_text)
            self.lbl_pdf_status.setStyleSheet("color: #00e676; font-size: 12px; font-weight: bold;")
        else:
            status_text = "Documento: ⚠️ Nessun PDF allegato. Clicca su 'Allega PDF' per caricare il file ed estrapolare i dati."
            self.lbl_pdf_status.setText(status_text)
            self.lbl_pdf_status.setStyleSheet("color: #ff9800; font-size: 12px;")
        if hasattr(self, "btn_view_pdf"):
            self.btn_view_pdf.setVisible(has_pdf)

    def carica_pdf_patente(self, patente_target=None) -> bool:
        titolo = f"Seleziona PDF Patente {patente_target}" if patente_target else "Seleziona PDF Patente"
        file_path, _ = QFileDialog.getOpenFileName(self, titolo, "", "File PDF (*.pdf)")
        if not file_path:
            return False

        from pdf_validator import valida_pdf_patente
        valido, err = valida_pdf_patente(file_path)
        if not valido:
            QMessageBox.critical(
                self,
                "File Non Valido",
                f"❌ Il file selezionato non supera i controlli di integrità:\n\n{err}\n\n"
                f"Assicurati di allegare un documento PDF valido e integro."
            )
            return False

        dest_dir = os.path.abspath("patenti_pdf")
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        cf = getattr(self.volontario, "cod_fiscale", "utente")
        dest_filename = f"{cf}_patente.pdf"
        dest_path = os.path.join(dest_dir, dest_filename)

        try:
            shutil.copy(file_path, dest_path)
            rel_path = f"patenti_pdf/{dest_filename}"
            self.volontario.patente_pdf_path = rel_path

            # --- ESTRAPOLAZIONE AUTOMATICA DATI DA PDF (TESTO O SCANSIONE) ---
            from patente_extractor import estrai_dati_patente_da_pdf
            dati_estratti = estrai_dati_patente_da_pdf(dest_path)

            campi_trovati = []

            # 1. Numero patente
            num_estratto = dati_estratti.get("numero_patente", "").strip().upper()
            if num_estratto:
                if hasattr(self, "edit_numero_patente"):
                    self.edit_numero_patente.setText(num_estratto)
                self.volontario.numero_patente = num_estratto
                campi_trovati.append(f"• Numero Patente: <b>{num_estratto}</b>")

            # 2. Data di scadenza
            scad_estratta = dati_estratti.get("data_scadenza", "").strip()
            if scad_estratta:
                qdate = QDate.fromString(scad_estratta, "yyyy-MM-dd")
                if not qdate.isValid():
                    qdate = QDate.fromString(scad_estratta, "dd/MM/yyyy")
                if qdate.isValid():
                    if hasattr(self, "edit_scadenza_patente"):
                        self.edit_scadenza_patente.setDate(qdate)
                    self.volontario.scadenza_patente = scad_estratta
                    campi_trovati.append(f"• Data di Scadenza: <b>{qdate.toString('dd/MM/yyyy')}</b>")

            # 3. Categorie abilitate
            cats_estratte = dati_estratti.get("categorie", ["B"])
            if cats_estratte:
                self._updating_checkbox = True
                for cat, cb in self.patente_checkboxes.items():
                    cb.setChecked(cat in cats_estratte)
                self._updating_checkbox = False
                self.volontario.patenti = list(cats_estratte)
                self.patenti_pdf = {c: rel_path for c in cats_estratte}
                self.volontario.patenti_pdf = self.patenti_pdf
                campi_trovati.append(f"• Categorie Rilevate: <b>{', '.join(cats_estratte)}</b>")
            elif patente_target:
                self.patenti_pdf[patente_target] = rel_path
                self.volontario.patenti_pdf = self.patenti_pdf

            self.aggiorna_stato_pdf()

            riepilogo = "\n".join(campi_trovati) if campi_trovati else "• Documento allegato e verificato regolarmente."
            QMessageBox.information(
                self,
                "✅ Dati Estrapolati dal PDF",
                f"Il documento PDF è stato verificato con successo e i dati sono stati estrapolati automaticamente:\n\n"
                f"{riepilogo}\n\n"
                f"I campi del profilo sono stati compilati. Puoi verificare o modificare i campi prima di salvare."
            )
            return True
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"❌ Errore durante l'elaborazione del file PDF: {e}")
            return False

    def visualizza_pdf_patente(self):
        # Prendi il primo file valido
        path = None
        for p_file in self.patenti_pdf.values():
            if os.path.exists(os.path.abspath(p_file)):
                path = os.path.abspath(p_file)
                break
        if not path and getattr(self.volontario, "patente_pdf_path", None):
            path = os.path.abspath(self.volontario.patente_pdf_path)

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
            QMessageBox.warning(self, "Errore", "Nessun file PDF verificato trovato.")

    def salva_dati(self):
        patenti_scelte = [p for p, cb in self.patente_checkboxes.items() if cb.isChecked()]

        # CONTROLLO DI SICUREZZA:
        # Se anche una sola patente è spuntata, deve esserci un documento PDF valido!
        if patenti_scelte:
            for p in patenti_scelte:
                if not self.ha_pdf_valido(p):
                    QMessageBox.critical(
                        self,
                        "🛑 Documento PDF Mancante",
                        f"Impossibile salvare il profilo!\n\n"
                        f"Hai selezionato la patente '{p}', ma non è stato allegato un documento PDF valido.\n\n"
                        f"Allega il file PDF tramite il pulsante '📂 Allega PDF ed Estrapola Dati' oppure deseleziona la patente per procedere."
                    )
                    return

        self.volontario.nome = self.nome_edit.text().strip()
        self.volontario.cognome = self.cognome_edit.text().strip()
        
        if hasattr(self, "cf_edit"):
            nuovo_cf = self.cf_edit.text().strip().upper()
            if nuovo_cf and len(nuovo_cf) == 16:
                self.volontario.cod_fiscale = nuovo_cf

        nuova_email = self.email_edit.text().strip()
        if nuova_email != self.volontario.email:
            self.volontario.aggiorna_email(nuova_email)

        self.volontario.nascita = self.nascita_edit.date().toString("dd/MM/yyyy")
        self.volontario.telefono = self.telefono_edit.text().strip()

        # Salva numero patente e scadenza inseriti o estrapolati da PDF
        if hasattr(self, "edit_numero_patente"):
            num_val = self.edit_numero_patente.text().strip().upper()
            if num_val:
                self.volontario.numero_patente = num_val
        if hasattr(self, "edit_scadenza_patente"):
            self.volontario.scadenza_patente = self.edit_scadenza_patente.date().toString("yyyy-MM-dd")

        self.volontario.patenti = patenti_scelte
        self.volontario.patenti_pdf = self.patenti_pdf
        self.volontario.compagnia_appartenenza = self.compagnia_edit.text().strip()
        self.volontario.disponibilita = [d.strip() for d in self.disponibilita_edit.text().split(",") if d.strip()]

        # Salva ruolo operativo se modificato
        if hasattr(self, "ruolo_combo"):
            nuovo_ruolo = str(self.ruolo_combo.currentData() or "volontario").lower()
            ruolo_attuale = str(getattr(self.volontario, "ruolo", "volontario") or "volontario").lower()
            if nuovo_ruolo != ruolo_attuale:
                if nuovo_ruolo == "referente" and ruolo_attuale != "referente":
                    from security_config import verifica_pin_referente
                    from PyQt5.QtWidgets import QInputDialog
                    pin_input, ok = QInputDialog.getText(
                        self,
                        "🔒 Autorizzazione Referente Richiesta",
                        "Per abilitare i privilegi di Referente / Coordinatore,\n"
                        "inserisci il PIN di sicurezza CRI del Comitato:",
                        QLineEdit.Password
                    )
                    if not ok or not verifica_pin_referente(pin_input):
                        QMessageBox.critical(
                            self,
                            "Autorizzazione Negata",
                            "❌ PIN di sicurezza errato o non fornito.\n\n"
                            "L'auto-promozione a Referente è stata bloccata per motivi di sicurezza."
                        )
                        idx_prev = self.ruolo_combo.findData(ruolo_attuale)
                        if idx_prev >= 0:
                            self.ruolo_combo.setCurrentIndex(idx_prev)
                        return

                self.volontario.ruolo = nuovo_ruolo
                if nuovo_ruolo == "referente":
                    from Referente import Referente
                    self.volontario.__class__ = Referente
                elif nuovo_ruolo == "volontario":
                    from Volontario import Volontario
                    self.volontario.__class__ = Volontario

                try:
                    from session_manager import save_session
                    save_session(self.volontario)
                except Exception:
                    pass

        try:
            self.volontario.aggiorna_firestore()
            QMessageBox.information(self, "Successo", "✅ Dati e abilitazioni salvati correttamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"❌ Errore nel salvataggio: {e}")
