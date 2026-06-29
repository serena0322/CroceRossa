from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QMessageBox, QCheckBox, QHBoxLayout, QWidget, QDateEdit, QFileDialog
)
from PyQt5.QtCore import Qt, QDate

class ModificaDatiDialog(QDialog):
    def __init__(self, volontario, parent=None):
        super().__init__(parent)
        self.volontario = volontario
        self.setWindowTitle("Modifica dati personali")
        self.setMinimumWidth(480)

        # Style Sheet for homogeneous premium dark look
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
                font-weight: bold;
            }
            QLineEdit, QDateEdit {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 1px solid #d32f2f;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 6px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.nome_edit = QLineEdit(volontario.nome)
        self.cognome_edit = QLineEdit(volontario.cognome)
        self.email_edit = QLineEdit(volontario.email)
        
        # date of birth QDateEdit
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
        
        # PDF curriculum row
        cv_row = QWidget()
        cv_layout = QHBoxLayout(cv_row)
        cv_layout.setContentsMargins(0, 0, 0, 0)
        cv_layout.setSpacing(10)
        
        has_cv = bool(volontario.curriculum and str(volontario.curriculum).endswith(".pdf"))
        cv_status = "Curriculum PDF: Caricato (Sì)" if has_cv else "Curriculum PDF: Non caricato (No)"
        self.lbl_cv_status = QLabel(cv_status)
        cv_layout.addWidget(self.lbl_cv_status)
        
        self.btn_carica_cv = QPushButton("📂 Carica CV PDF")
        self.btn_carica_cv.setStyleSheet("""
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
        # pyrefly: ignore [missing-attribute]
        self.btn_carica_cv.clicked.connect(self.carica_cv_pdf)
        cv_layout.addWidget(self.btn_carica_cv)
        
        self.btn_view_cv = QPushButton("👁️ Vedi CV PDF")
        self.btn_view_cv.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        # pyrefly: ignore [missing-attribute]
        self.btn_view_cv.clicked.connect(self.visualizza_cv_pdf)
        self.btn_view_cv.setVisible(has_cv)
        cv_layout.addWidget(self.btn_view_cv)

        self.patente_checkboxes = {}
        patente_widget = QWidget()
        patente_layout = QHBoxLayout(patente_widget)
        patente_layout.setContentsMargins(0, 0, 0, 0)
        patente_layout.setSpacing(15)
        
        for p in ["B", "C", "D", "E"]:
            cb = QCheckBox(p)
            cb.setChecked(p in volontario.patenti or p.lower() in [val.lower() for val in (volontario.patenti or [])])
            patente_layout.addWidget(cb)
            self.patente_checkboxes[p] = cb
            
        # PDF upload layout
        pdf_row = QWidget()
        pdf_layout = QHBoxLayout(pdf_row)
        pdf_layout.setContentsMargins(0, 0, 0, 0)
        pdf_layout.setSpacing(10)
        
        has_pdf = bool(getattr(volontario, 'patente_pdf_path', None))
        status_text = "Patente PDF: Caricata (Sì)" if has_pdf else "Patente PDF: Non caricata (No)"
        self.lbl_pdf_status = QLabel(status_text)
        pdf_layout.addWidget(self.lbl_pdf_status)
        
        self.btn_carica_pdf = QPushButton("📂 Carica PDF")
        self.btn_carica_pdf.setStyleSheet("""
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
        # pyrefly: ignore [missing-attribute]
        self.btn_carica_pdf.clicked.connect(self.carica_pdf_patente)
        pdf_layout.addWidget(self.btn_carica_pdf)
        
        self.btn_view_pdf = QPushButton("👁️ Vedi PDF")
        self.btn_view_pdf.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        # pyrefly: ignore [missing-attribute]
        self.btn_view_pdf.clicked.connect(self.visualizza_pdf_patente)
        self.btn_view_pdf.setVisible(has_pdf)
        pdf_layout.addWidget(self.btn_view_pdf)
            
        self.compagnia_edit = QLineEdit(volontario.compagnia_appartenenza)
        self.disponibilita_edit = QLineEdit(", ".join(volontario.disponibilita))

        layout.addWidget(QLabel("Nome:"))
        layout.addWidget(self.nome_edit)
        layout.addWidget(QLabel("Cognome:"))
        layout.addWidget(self.cognome_edit)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_edit)
        layout.addWidget(QLabel("Data di nascita:"))
        layout.addWidget(self.nascita_edit)
        layout.addWidget(QLabel("Telefono:"))
        layout.addWidget(self.telefono_edit)
        layout.addWidget(QLabel("Curriculum Vitae (PDF):"))
        layout.addWidget(cv_row)
        layout.addWidget(QLabel("Patenti abilitate:"))
        layout.addWidget(patente_widget)
        layout.addWidget(pdf_row)
        layout.addWidget(QLabel("Compagnia di appartenenza:"))
        layout.addWidget(self.compagnia_edit)
        layout.addWidget(QLabel("Disponibilità (es. lunedì, martedì):"))
        layout.addWidget(self.disponibilita_edit)

        # Spacer to push button down
        layout.addSpacing(10)
        
        salva_btn = QPushButton("Salva Dati")
        salva_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        # pyrefly: ignore [missing-attribute]
        salva_btn.clicked.connect(self.salva_dati)
        layout.addWidget(salva_btn)

        self.setLayout(layout)

    def carica_cv_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona PDF Curriculum", "", "PDF Files (*.pdf)")
        if file_path:
            import os
            import shutil
            dest_dir = os.path.abspath("curricula_pdf")
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            dest_path = os.path.join(dest_dir, f"{self.volontario.cod_fiscale}_curriculum.pdf")
            try:
                shutil.copy(file_path, dest_path)
                self.volontario.curriculum = f"curricula_pdf/{self.volontario.cod_fiscale}_curriculum.pdf"
                self.lbl_cv_status.setText("Curriculum PDF: Caricato (Sì)")
                self.btn_view_cv.setVisible(True)
                QMessageBox.information(self, "Successo", "✅ PDF Curriculum caricato correttamente!")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"❌ Errore durante il caricamento del file: {e}")

    def visualizza_cv_pdf(self):
        import os
        import sys
        import subprocess
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
            QMessageBox.warning(self, "Errore", "Impossibile trovare il file PDF caricato.")

    def carica_pdf_patente(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona PDF Patente", "", "PDF Files (*.pdf)")
        if file_path:
            import os
            import shutil
            dest_dir = os.path.abspath("patenti_pdf")
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            dest_path = os.path.join(dest_dir, f"{self.volontario.cod_fiscale}_patente.pdf")
            try:
                shutil.copy(file_path, dest_path)
                self.volontario.patente_pdf_path = f"patenti_pdf/{self.volontario.cod_fiscale}_patente.pdf"
                self.lbl_pdf_status.setText("Patente PDF: Caricata (Sì)")
                self.btn_view_pdf.setVisible(True)
                QMessageBox.information(self, "Successo", "✅ PDF Patente caricato correttamente!")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"❌ Errore durante il caricamento del file: {e}")

    def visualizza_pdf_patente(self):
        import os
        import sys
        import subprocess
        path = os.path.abspath(self.volontario.patente_pdf_path)
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
            QMessageBox.warning(self, "Errore", "Impossibile trovare il file PDF caricato.")

    def salva_dati(self):
        self.volontario.nome = self.nome_edit.text().strip()
        self.volontario.cognome = self.cognome_edit.text().strip()
        nuova_email = self.email_edit.text().strip()
        if nuova_email != self.volontario.email:
            self.volontario.aggiorna_email(nuova_email)
        self.volontario.nascita = self.nascita_edit.date().toString("dd/MM/yyyy")
        self.volontario.telefono = self.telefono_edit.text().strip()
        self.volontario.patenti = [p for p, cb in self.patente_checkboxes.items() if cb.isChecked()]
        self.volontario.compagnia_appartenenza = self.compagnia_edit.text().strip()
        self.volontario.disponibilita = [d.strip() for d in self.disponibilita_edit.text().split(",") if d.strip()]

        try:
            self.volontario.aggiorna_firestore()
            QMessageBox.information(self, "Successo", "✅ Dati aggiornati con successo.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"❌ Errore nel salvataggio: {e}")
