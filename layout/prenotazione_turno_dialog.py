"""
Modulo per la finestra di dialogo interattiva di prenotazione turno.
Presenta in modo chiaro, trasparente e guidato tutte le regole operative per l'iscrizione a un turno CRI:
1. Controllo di sovrapposizione oraria rispetto agli altri turni assegnati.
2. Controllo dei requisiti di guida (patenti valide e verificate per il ruolo di Autista).
3. Rispetto rigoroso del fabbisogno posti per ciascun ruolo operativo.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QRadioButton, QButtonGroup, QMessageBox, QWidget, QScrollArea
)
from PyQt5.QtCore import Qt


class PrenotazioneTurnoDialog(QDialog):
    def __init__(self, turno, volontario, turni_controller, parent=None):
        super().__init__(parent)
        self.turno = turno
        self.volontario = volontario
        self.turni_controller = turni_controller
        self.ruolo_selezionato = None

        self.setWindowTitle(f"📋 Iscrizione Turno — {turno.id}")
        self.resize(560, 580)
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
            QFrame#RoleCard {
                background-color: #2a2a2a;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
            }
            QFrame#RoleCard:hover {
                border: 1px solid #d32f2f;
            }
            QRadioButton {
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
                spacing: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Riquadro Dettagli Turno
        card_turno = QFrame()
        card_turno.setObjectName("Card")
        card_lay = QVBoxLayout(card_turno)
        card_lay.setContentsMargins(14, 12, 14, 12)
        card_lay.setSpacing(6)

        titolo_box = QHBoxLayout()
        lbl_servizio = QLabel(f"<h2 style='color: white; margin: 0;'>🚑 {turno.tipoServizio or 'Servizio CRI'}</h2>")
        badge_id = QLabel(f"<span style='background-color: #37474f; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;'>ID: {turno.id}</span>")
        titolo_box.addWidget(lbl_servizio)
        titolo_box.addStretch()
        titolo_box.addWidget(badge_id)
        card_lay.addLayout(titolo_box)

        luogo_str = getattr(turno, "luogo", "") or getattr(turno, "luogoDestinazione", "Sede Croce Rossa")
        pat_richiesta = str(getattr(turno, "patenteRichiesta", "") or "Nessuna specifica").strip()

        lbl_info = QLabel(
            f"🗓️ <b>Data:</b> {turno.data} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"🕒 <b>Orario:</b> {turno.fascia_oraria}<br>"
            f"📍 <b>Luogo / Destinazione:</b> {luogo_str}<br>"
            f"🪪 <b>Patente richiesta dal mezzo:</b> <b style='color: #4fc3f7;'>{pat_richiesta}</b>"
        )
        card_lay.addWidget(lbl_info)
        layout.addWidget(card_turno)

        # 2. Verifica Regole Preliminari
        self.card_regole = QFrame()
        self.card_regole.setObjectName("Card")
        regole_lay = QVBoxLayout(self.card_regole)
        regole_lay.setContentsMargins(14, 10, 14, 10)
        regole_lay.setSpacing(6)

        lbl_reg_title = QLabel("🛡️ <b>Controllo Requisiti di Conformità:</b>")
        lbl_reg_title.setStyleSheet("color: #90caf9; font-weight: bold;")
        regole_lay.addWidget(lbl_reg_title)

        # Controllo Sovrapposizione
        self.ha_sovrapposizione = not self.turni_controller.verificaTempoLimite(self.volontario, self.turno)
        if self.ha_sovrapposizione:
            lbl_check_ora = QLabel("❌ <b>Sovrapposizione oraria:</b> Sei già iscritto a un altro turno con orario coincidente in questa data.")
            lbl_check_ora.setStyleSheet("color: #ff5252;")
        else:
            lbl_check_ora = QLabel("✅ <b>Disponibilità oraria:</b> Nessun conflitto di orario con altri tuoi turni.")
            lbl_check_ora.setStyleSheet("color: #00e676;")
        regole_lay.addWidget(lbl_check_ora)

        # Patenti Possedute
        user_patenti = [str(p).strip().upper() for p in getattr(self.volontario, "patenti", [])]
        pat_txt = ", ".join(user_patenti) if user_patenti else "Nessuna registrata"
        lbl_check_pat = QLabel(f"🪪 <b>Le tue patenti abilitate:</b> {pat_txt}")
        lbl_check_pat.setStyleSheet("color: #e0e0e0;")
        regole_lay.addWidget(lbl_check_pat)

        layout.addWidget(self.card_regole)

        # 3. Sezione Selezione Ruoli Operativi
        layout.addWidget(QLabel("<b>🎯 Seleziona il Ruolo Operativo da Ricoprire:</b>"))

        self.ruoli_list = self.analizza_ruoli_disponibili()
        self.button_group = QButtonGroup(self)
        self.radio_buttons = {}

        roles_scroll = QScrollArea()
        roles_scroll.setWidgetResizable(True)
        roles_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        roles_widget = QWidget()
        roles_lay = QVBoxLayout(roles_widget)
        roles_lay.setContentsMargins(0, 0, 0, 0)
        roles_lay.setSpacing(8)

        for r_info in self.ruoli_list:
            role_card = QFrame()
            role_card.setObjectName("RoleCard")
            r_box = QHBoxLayout(role_card)
            r_box.setContentsMargins(12, 10, 12, 10)

            rb = QRadioButton(r_info["nome"])
            self.button_group.addButton(rb)
            self.radio_buttons[r_info["nome"]] = (rb, r_info)
            r_box.addWidget(rb)
            r_box.addStretch()

            # Badge Posti
            liberi = r_info["posti_liberi"]
            tot = r_info["posti_totali"]
            occupati = r_info["posti_occupati"]

            if liberi > 0:
                badge_posti = QLabel(f"<span style='background-color: #2e7d32; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold;'>🟢 {liberi} posto/i libero/i ({occupati}/{tot})</span>")
            else:
                badge_posti = QLabel(f"<span style='background-color: #c62828; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold;'>🔴 Al completo ({occupati}/{tot})</span>")
            r_box.addWidget(badge_posti)

            # Badge Requisito Patente
            if r_info["richiede_patente"]:
                has_pat = r_info["ha_patente"]
                bg_col = "#0d47a1" if has_pat else "#d84315"
                icon_pat = "✅" if has_pat else "⚠️"
                badge_req = QLabel(f"<span style='background-color: {bg_col}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold;'>{icon_pat} Patente {r_info['richiede_patente']}</span>")
                r_box.addWidget(badge_req)

            roles_lay.addWidget(role_card)
            rb.toggled.connect(self.on_role_selected)

        roles_scroll.setWidget(roles_widget)
        layout.addWidget(roles_scroll)

        # 4. Box Informativo / Errori
        self.lbl_stato_iscrizione = QLabel()
        self.lbl_stato_iscrizione.setWordWrap(True)
        self.lbl_stato_iscrizione.setStyleSheet("padding: 8px; border-radius: 6px; font-weight: bold;")
        layout.addWidget(self.lbl_stato_iscrizione)

        # 5. Pulsanti di Azione
        btn_box = QHBoxLayout()
        self.btn_conferma = QPushButton("✅ Conferma Iscrizione al Turno")
        self.btn_conferma.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #444444;
                color: #888888;
            }
        """)
        self.btn_conferma.clicked.connect(self.conferma_iscrizione)
        btn_box.addWidget(self.btn_conferma)

        btn_annulla = QPushButton("Annulla")
        btn_annulla.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border: 1px solid #555;
                color: #eee;
                padding: 10px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        btn_annulla.clicked.connect(self.reject)
        btn_box.addWidget(btn_annulla)

        layout.addLayout(btn_box)

        # Seleziona automaticamente il primo ruolo valido disponibile
        self.seleziona_primo_valido()

    def analizza_ruoli_disponibili(self) -> list[dict]:
        """
        Determina con chiarezza e precisione i ruoli previsti dal turno,
        il numero di posti liberi e i requisiti di patente per ciascuno.
        Risolve alla radice il problema dei fabbisogni vuoti o non allineati.
        """
        raw_fabbisogno = getattr(self.turno, "persone_richieste", {}) or {}
        tot_persone = getattr(self.turno, "personeRichieste", 1) or 1
        patente_richiesta = str(getattr(self.turno, "patenteRichiesta", "")).strip().upper()
        if patente_richiesta in ["NESSUNA", "NON RICHIESTA", "TUTTI"]:
            patente_richiesta = ""

        # Controllo se esistono ruoli specificati con fabbisogno > 0
        ruoli_configurati = {
            k: v for k, v in raw_fabbisogno.items() 
            if k.lower() != "volontario" and v > 0
        }

        if not ruoli_configurati:
            # Fallback standard strutturato per turni operativi CRI
            if patente_richiesta:
                ruoli_configurati = {
                    "Autista Tipo A": 1,
                    "Soccorritore Tipo A": max(1, tot_persone - 1)
                }
            else:
                ruoli_configurati = {
                    "Soccorritore Tipo A": tot_persone
                }

        user_patenti = [str(p).strip().upper() for p in getattr(self.volontario, "patenti", [])]
        assegnati = getattr(self.turno, "volontari_assegnati", [])
        ruoli_assegnati = getattr(self.turno, "volontari_ruoli", {})

        elenco = []
        for nome_ruolo, posti_richiesti in ruoli_configurati.items():
            count_occupati = sum(
                1 for v in assegnati 
                if (ruoli_assegnati.get(str(v.cod_fiscale)) or "").strip().lower() == nome_ruolo.lower()
            )
            posti_liberi = max(0, posti_richiesti - count_occupati)

            # Requisito patente
            req_pat = ""
            ha_patente = True
            if "Autista" in nome_ruolo:
                req_pat = patente_richiesta if patente_richiesta else "B"
                ha_patente = (req_pat in user_patenti)

            elenco.append({
                "nome": nome_ruolo,
                "posti_totali": posti_richiesti,
                "posti_occupati": count_occupati,
                "posti_liberi": posti_liberi,
                "richiede_patente": req_pat,
                "ha_patente": ha_patente
            })

        return elenco

    def seleziona_primo_valido(self):
        """Seleziona automaticamente il primo ruolo per cui il volontario ha i requisiti ed esistono posti liberi."""
        if self.ha_sovrapposizione:
            self.btn_conferma.setEnabled(False)
            self.lbl_stato_iscrizione.setText("❌ Impossibile procedere: hai già un turno assegnato con orario sovrapposto.")
            self.lbl_stato_iscrizione.setStyleSheet("background-color: rgba(198, 40, 40, 0.2); color: #ff5252; padding: 8px; border-radius: 6px;")
            return

        for rb, r_info in self.radio_buttons.values():
            if r_info["posti_liberi"] > 0 and r_info["ha_patente"]:
                rb.setChecked(True)
                return

        # Se nessun ruolo è valido
        self.btn_conferma.setEnabled(False)
        self.lbl_stato_iscrizione.setText("⚠️ Nessun ruolo operativo disponibile o compatibile con le tue attuali abilitazioni.")
        self.lbl_stato_iscrizione.setStyleSheet("background-color: rgba(239, 108, 0, 0.2); color: #ffb74d; padding: 8px; border-radius: 6px;")

    def on_role_selected(self):
        """Valida in tempo reale il ruolo selezionato e aggiorna il feedback visivo."""
        for rb, r_info in self.radio_buttons.values():
            if rb.isChecked():
                self.ruolo_selezionato = r_info["nome"]

                if self.ha_sovrapposizione:
                    self.btn_conferma.setEnabled(False)
                    self.lbl_stato_iscrizione.setText("❌ Impossibile procedere a causa della sovrapposizione oraria.")
                    self.lbl_stato_iscrizione.setStyleSheet("background-color: rgba(198, 40, 40, 0.2); color: #ff5252; padding: 8px; border-radius: 6px;")
                    return

                if r_info["posti_liberi"] <= 0:
                    self.btn_conferma.setEnabled(False)
                    self.lbl_stato_iscrizione.setText(f"❌ Il ruolo '{r_info['nome']}' è al completo ({r_info['posti_occupati']}/{r_info['posti_totali']}). Scegli un altro ruolo.")
                    self.lbl_stato_iscrizione.setStyleSheet("background-color: rgba(198, 40, 40, 0.2); color: #ff5252; padding: 8px; border-radius: 6px;")
                    return

                if not r_info["ha_patente"]:
                    self.btn_conferma.setEnabled(False)
                    self.lbl_stato_iscrizione.setText(
                        f"⚠️ Requisito mancante: il ruolo '{r_info['nome']}' richiede la patente {r_info['richiede_patente']}, "
                        f"non ancora abilitata o verificata nel tuo profilo."
                    )
                    self.lbl_stato_iscrizione.setStyleSheet("background-color: rgba(239, 108, 0, 0.2); color: #ffb74d; padding: 8px; border-radius: 6px;")
                    return

                # Tutto ok!
                self.btn_conferma.setEnabled(True)
                self.lbl_stato_iscrizione.setText(f"✅ Requisiti conformi! Pronto per l'iscrizione come '{r_info['nome']}'.")
                self.lbl_stato_iscrizione.setStyleSheet("background-color: rgba(46, 125, 50, 0.2); color: #69f0ae; padding: 8px; border-radius: 6px;")
                return

    def conferma_iscrizione(self):
        if not self.ruolo_selezionato:
            QMessageBox.warning(self, "Selezione Richiesta", "Seleziona un ruolo operativo per confermare l'iscrizione.")
            return

        if self.ha_sovrapposizione:
            QMessageBox.critical(self, "Sovrapposizione Rilevata", "Impossibile iscriversi: conflitto di orario con un altro turno già assegnato.")
            return

        self.accept()
