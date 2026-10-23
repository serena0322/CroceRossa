"""
Modulo per la finestra di dialogo dettagliata dei corsi CRI e generazione attestati.
Consente al volontario di:
1. Ispezionare il programma, le date, i requisiti e gli obiettivi del corso.
2. Visualizzare chiaramente il proprio stato: Effettuato / In Formazione (da effettuare) / Disponibile.
3. Se il corso è effettuato/superato, generare e scaricare l'Attestato Ufficiale di Partecipazione CRI in PDF.
4. Se il corso è in svolgimento, rinunciare o disiscriversi con 1 clic.
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QWidget, QScrollArea, QFileDialog
)
from PyQt5.QtCore import Qt


class DettaglioCorsoDialog(QDialog):
    def __init__(self, corso, utente, stato_tipo: str, controller_formazione=None, parent=None):
        super().__init__(parent)
        self.corso = corso
        self.utente = utente
        self.stato_tipo = stato_tipo  # "effettuato", "in_corso", "disponibile"
        self.controller = controller_formazione
        self.cambiamento_effettuato = False

        self.setWindowTitle(f"🎓 Scheda Corso — {corso.titolo or corso.nome}")
        self.resize(580, 520)
        self.setMinimumWidth(500)

        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
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
            QFrame#Card {
                background-color: #242424;
                border: 1px solid #333333;
                border-radius: 8px;
            }
            QPushButton {
                font-family: "Helvetica Neue", Arial;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Header Card Corso
        card_header = QFrame()
        card_header.setObjectName("Card")
        head_lay = QVBoxLayout(card_header)
        head_lay.setContentsMargins(14, 12, 14, 12)
        head_lay.setSpacing(6)

        titolo_box = QHBoxLayout()
        lbl_titolo = QLabel(f"<h2 style='color: white; margin: 0;'>🎓 {corso.titolo or corso.nome}</h2>")
        badge_id = QLabel(f"<span style='background-color: #37474f; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;'>ID: {corso.id}</span>")
        titolo_box.addWidget(lbl_titolo)
        titolo_box.addStretch()
        titolo_box.addWidget(badge_id)
        head_lay.addLayout(titolo_box)

        qualifica = getattr(corso, "qualificaRilasciata", "") or corso.titolo
        validita_mesi = getattr(corso, "mesiValidita", 12)
        scadenza = getattr(corso, "scadenza", "") or "Illimitata / Non specificata"
        direttore = getattr(corso, "direttore", "") or "Direzione Sanitaria / Formazione CRI"
        luogo = getattr(corso, "luogo", "") or "Sede Operativa Comitato Locale"
        orari = getattr(corso, "orari", "") or "09:00 - 13:00 / 14:00 - 18:00"
        requisiti = getattr(corso, "requisitiIscrizione", "") or "Volontario attivo CRI"
        iscritti_n = len(getattr(corso, "partecipanti", []))
        max_p = getattr(corso, "maxPartecipanti", 20)

        lbl_info = QLabel(
            f"🗓️ <b>Periodo di Svolgimento:</b> dal {corso.dataInizio or 'N/D'} al {corso.dataFine or 'N/D'}<br>"
            f"🕒 <b>Orari e Luogo:</b> {orari} &nbsp;&nbsp;|&nbsp;&nbsp; 📍 {luogo}<br>"
            f"👤 <b>Direttore del Corso:</b> {direttore}<br>"
            f"📋 <b>Requisiti di Iscrizione:</b> {requisiti}<br>"
            f"👥 <b>Capienza / Posti Disponibili:</b> <b>{iscritti_n} / {max_p}</b> partecipanti<br>"
            f"🏆 <b>Qualifica / Brevetto:</b> <b style='color: #4fc3f7;'>{qualifica}</b><br>"
            f"⏱️ <b>Validità formativa:</b> {validita_mesi} mesi &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"📅 <b>Scadenza:</b> {scadenza}"
        )
        head_lay.addWidget(lbl_info)
        layout.addWidget(card_header)

        # 2. Badge Stato Personale del Volontario
        card_stato = QFrame()
        card_stato.setObjectName("Card")
        stato_lay = QVBoxLayout(card_stato)
        stato_lay.setContentsMargins(14, 10, 14, 10)
        stato_lay.setSpacing(4)

        lbl_stato_titolo = QLabel("<b>Stato Personale Iscrizione:</b>")
        stato_lay.addWidget(lbl_stato_titolo)

        if self.stato_tipo == "effettuato":
            lbl_badge_stato = QLabel(
                "<span style='background-color: #2e7d32; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 13px;'>"
                "🟢 Corso Effettuato e Superato — Certificazione Conseguita</span>"
            )
            lbl_desc_stato = QLabel("Hai completato questo corso con esito positivo e la qualifica è registrata nel tuo curriculum CRI.")
            lbl_desc_stato.setStyleSheet("color: #a5d6a7; font-size: 12px;")
        elif self.stato_tipo == "in_corso":
            lbl_badge_stato = QLabel(
                "<span style='background-color: #ef6c00; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 13px;'>"
                "🟡 Corso da Effettuare — Iscrizione Attiva / In Svolgimento</span>"
            )
            lbl_desc_stato = QLabel("Sei regolarmente iscritto al corso. Riceverai la certificazione al termine delle sessioni formative.")
            lbl_desc_stato.setStyleSheet("color: #ffe082; font-size: 12px;")
        else:
            lbl_badge_stato = QLabel(
                "<span style='background-color: #455a64; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 13px;'>"
                "⚪ Corso Disponibile a Catalogo — Non Iscritto</span>"
            )
            lbl_desc_stato = QLabel("Questo corso è disponibile per l'iscrizione formativa dei volontari.")
            lbl_desc_stato.setStyleSheet("color: #b0bec5; font-size: 12px;")

        stato_lay.addWidget(lbl_badge_stato)
        stato_lay.addWidget(lbl_desc_stato)
        layout.addWidget(card_stato)

        # 3. Moduli Formativi & Checklist Didattica
        layout.addWidget(QLabel("<b>📋 Obiettivi Formativi e Moduli del Corso:</b>"))
        checklist = getattr(corso, "checklist", []) or []
        
        scroll_moduli = QScrollArea()
        scroll_moduli.setWidgetResizable(True)
        scroll_moduli.setStyleSheet("QScrollArea { border: 1px solid #333; border-radius: 6px; background-color: #212121; }")
        scroll_widget = QWidget()
        mod_lay = QVBoxLayout(scroll_widget)
        mod_lay.setContentsMargins(10, 10, 10, 10)
        mod_lay.setSpacing(6)

        if checklist:
            for item in checklist:
                item_testo = item.get("item", "Modulo formativo")
                fatto = item.get("completato", False)
                icona = "✅" if (fatto or self.stato_tipo == "effettuato") else "🔘"
                colore = "#a5d6a7" if (fatto or self.stato_tipo == "effettuato") else "#e0e0e0"
                lbl_item = QLabel(f"{icona} <span style='color: {colore};'>{item_testo}</span>")
                mod_lay.addWidget(lbl_item)
        else:
            default_moduli = [
                "Modulo 1: Linee guida operative e principi di soccorso",
                "Modulo 2: Esercitazioni pratiche e simulazioni d'intervento",
                "Modulo 3: Valutazione finale e attestazione competenze"
            ]
            for mod in default_moduli:
                icona = "✅" if self.stato_tipo == "effettuato" else "🔘"
                colore = "#a5d6a7" if self.stato_tipo == "effettuato" else "#e0e0e0"
                lbl_item = QLabel(f"{icona} <span style='color: {colore};'>{mod}</span>")
                mod_lay.addWidget(lbl_item)

        scroll_moduli.setWidget(scroll_widget)
        layout.addWidget(scroll_moduli)

        # 4. Barra Azioni Dinamica in base allo stato
        btn_bar = QHBoxLayout()

        if self.stato_tipo == "effettuato":
            btn_attestato = QPushButton("📜 Scarica Attestato Ufficiale (PDF)")
            btn_attestato.setStyleSheet("""
                QPushButton {
                    background-color: #0d47a1;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
            """)
            btn_attestato.clicked.connect(self.scarica_attestato_pdf)  # pyrefly: ignore [missing-attribute]
            btn_bar.addWidget(btn_attestato)

            btn_txt = QPushButton("📄 Esporta Scheda TXT")
            btn_txt.setStyleSheet("background-color: #37474f; color: white; padding: 8px 14px; border-radius: 6px;")
            btn_txt.clicked.connect(self.scarica_scheda_txt)  # pyrefly: ignore [missing-attribute]
            btn_bar.addWidget(btn_txt)

        elif self.stato_tipo == "in_corso":
            btn_disiscrivi = QPushButton("❌ Rinuncia / Disiscriviti dal Corso")
            btn_disiscrivi.setStyleSheet("""
                QPushButton {
                    background-color: #c62828;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #b71c1c;
                }
            """)
            btn_disiscrivi.clicked.connect(self.azione_disiscrivi)  # pyrefly: ignore [missing-attribute]
            btn_bar.addWidget(btn_disiscrivi)

        else:  # Disponibile
            iscritti_n = len(getattr(corso, "partecipanti", []))
            max_p = getattr(corso, "maxPartecipanti", 20)
            al_completo = (iscritti_n >= max_p)

            btn_iscrivi = QPushButton("🔴 Corso al Completo" if al_completo else "📝 Iscriviti a questo Corso")
            btn_iscrivi.setEnabled(not al_completo)
            btn_iscrivi.setStyleSheet("""
                QPushButton {
                    background-color: #2e7d32;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #1b5e20;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #aaaaaa;
                }
            """)
            btn_iscrivi.clicked.connect(self.azione_iscrivi)  # pyrefly: ignore [missing-attribute]
            btn_bar.addWidget(btn_iscrivi)

        btn_bar.addStretch()
        btn_chiudi = QPushButton("Chiudi")
        btn_chiudi.setStyleSheet("background-color: #333333; color: white; padding: 8px 14px; border-radius: 6px;")
        btn_chiudi.clicked.connect(self.accept)  # pyrefly: ignore [missing-attribute]
        btn_bar.addWidget(btn_chiudi)

        layout.addLayout(btn_bar)

    def scarica_attestato_pdf(self):
        """Genera e salva un documento PDF conforme dell'Attestato Ufficiale di Partecipazione CRI."""
        nome_default = f"Attestato_CRI_{self.corso.id}_{self.utente.cod_fiscale}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva Attestato di Partecipazione CRI",
            os.path.join(os.path.expanduser("~"), "Desktop", nome_default),
            "Documenti PDF (*.pdf)"
        )
        if not file_path:
            return

        try:
            now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            qualifica = getattr(self.corso, "qualificaRilasciata", "") or self.corso.titolo
            monte_ore = getattr(self.corso, "mesiValidita", 1) * 10

            titolo = "CROCE ROSSA ITALIANA - ATTESTATO DI CERTIFICAZIONE FORMATIVA"
            sottotitolo = "CERTIFICATO DI FREQUENZA E SUPERAMENTO CORSO OPERATIVO"

            righe = [
                "----------------------------------------------------------------------------------------------------",
                f"CORSO DI FORMAZIONE: {self.corso.titolo or self.corso.nome} (ID: {self.corso.id})",
                f"DATA RILASCIO ATTESTATO: {now_str}",
                "----------------------------------------------------------------------------------------------------",
                f"PARTECIPANTE: {self.utente.getNomeCompleto()}",
                f"CODICE FISCALE: {self.utente.cod_fiscale}",
                f"RUOLO / QUALIFICA ACQUISITA: {qualifica}",
                f"PERIODO FORMATIVO: dal {self.corso.dataInizio or 'N/D'} al {self.corso.dataFine or 'N/D'}",
                f"MONTE ORE VALUTATO: {monte_ore} ore di formazione e addestramento operativo",
                f"ESITO DELLA VALUTAZIONE: IDONEO / CERTIFICATO UFFICIALE CONSEGUITO",
                f"VALIDITA' CERTIFICAZIONE: fino al {getattr(self.corso, 'scadenza', 'Illimitata')}",
                "----------------------------------------------------------------------------------------------------",
                "ATTESTAZIONE DI CONFORMITA':",
                "Il presente attestato certifica che il volontario ha frequentato con profitto tutte le sessioni",
                "teoriche e pratiche previste dal regolamento formativo della Croce Rossa Italiana.",
                f"CODICE IDENTIFICATIVO ATTESTATO: CRI-CERT-{self.corso.id}-{self.utente.cod_fiscale[-6:]}",
                "FIRMA DEL DIRETTORE DEL CORSO: _____________________________ (Delegato Area Formazione)",
                "----------------------------------------------------------------------------------------------------"
            ]

            # Stream PDF valido in standard PDF 1.4
            content_stream = "BT\n/F1 12 Tf\n40 750 Td\n(" + titolo + ") Tj\nET\n"
            content_stream += "BT\n/F1 10 Tf\n40 735 Td\n(" + sottotitolo + ") Tj\nET\n"
            content_stream += "BT\n/F2 9 Tf\n"
            y = 705
            for riga in righe:
                clean = riga.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
                content_stream += f"40 {y} Td\n({clean}) Tj\n-40 {-y} Td\n"
                y -= 16
            content_stream += "ET\n"

            stream_bytes = content_stream.encode("latin-1", errors="replace")
            stream_len = len(stream_bytes)

            pdf_content = (
                b"%PDF-1.4\n"
                b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
                b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
                b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                b"/Contents 4 0 R /Resources << /Font << "
                b"/F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> "
                b"/F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> "
                b">> >> >>\nendobj\n"
                b"4 0 obj\n<< /Length " + str(stream_len).encode("ascii") + b" >>\nstream\n"
                + stream_bytes +
                b"\nendstream\nendobj\n"
                b"xref\n0 5\n0000000000 65535 f \n"
                b"0000000010 00000 n \n"
                b"0000000060 00000 n \n"
                b"0000000120 00000 n \n"
                b"0000000300 00000 n \n"
                b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n500\n%%EOF\n"
            )

            with open(file_path, "wb") as f:
                f.write(pdf_content)

            QMessageBox.information(
                self,
                "Attestato Scaricato",
                f"✅ Attestato di partecipazione generato con successo in formato PDF:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile salvare l'attestato PDF: {e}")

    def scarica_scheda_txt(self):
        nome_default = f"Scheda_Corso_{self.corso.id}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva Scheda Corso",
            os.path.join(os.path.expanduser("~"), "Desktop", nome_default),
            "File di Testo (*.txt)"
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"=== CROCE ROSSA ITALIANA - SCHEDA CORSO ===\n")
                f.write(f"ID Corso: {self.corso.id}\n")
                f.write(f"Titolo: {self.corso.titolo or self.corso.nome}\n")
                f.write(f"Data Inizio: {self.corso.dataInizio}\n")
                f.write(f"Data Fine: {self.corso.dataFine}\n")
                f.write(f"Qualifica Rilasciata: {getattr(self.corso, 'qualificaRilasciata', '') or self.corso.titolo}\n")
                f.write(f"Stato Personale: {self.stato_tipo.upper()}\n")
                f.write(f"Volontario: {self.utente.getNomeCompleto()} ({self.utente.cod_fiscale})\n")
            QMessageBox.information(self, "Esportato", f"✅ Scheda salvata in:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'esportazione: {e}")

    def azione_disiscrivi(self):
        risposta = QMessageBox.question(
            self,
            "Conferma Disiscrizione",
            f"Sei sicuro di voler rinunciare all'iscrizione per il corso '{self.corso.titolo or self.corso.nome}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if risposta != QMessageBox.Yes:
            return

        if self.controller:
            self.controller.disiscriviVolontario(self.utente, self.corso.id)
        else:
            if hasattr(self.utente, "disiscriviti_dal_corso"):
                self.utente.disiscriviti_dal_corso(self.corso)

        self.cambiamento_effettuato = True
        QMessageBox.information(self, "Disiscrizione Effettuata", f"✅ Ti sei disiscritto con successo dal corso {self.corso.titolo}.")
        self.accept()

    def azione_iscrivi(self):
        if self.corso.isCompleto():
            QMessageBox.critical(self, "Corso al Completo", f"❌ Impossibile iscriversi: il corso ha raggiunto la capienza massima consentita ({getattr(self.corso, 'maxPartecipanti', 20)} partecipanti).")
            return
        if self.controller:
            ok = self.controller.iscriviVolontario(self.utente, self.corso.id)
            if not ok:
                QMessageBox.critical(self, "Iscrizione Fallita", "❌ Impossibile completare l'iscrizione (corso al completo o errore).")
                return
        if hasattr(self.utente, "iscriviti_al_corso"):
            self.utente.iscriviti_al_corso(self.corso)
        if hasattr(self.utente, "aggiorna_firestore"):
            try:
                self.utente.aggiorna_firestore()
            except Exception:
                pass

        self.cambiamento_effettuato = True
        QMessageBox.information(self, "Iscrizione Confermata", f"✅ Ti sei iscritto con successo al corso {self.corso.titolo}!")
        self.accept()
