from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from Utente import Utente
    from Volontario import Volontario
    from Referente import Referente
    from Corso import Corso
    from Turno import Turno
    from Mezzo import Mezzo
    from Checklist import Checklist

class Sistema:
    def __init__(self):
        self.volontari: list[Volontario] = []
        self.corsi: list[Corso] = []
        self.turni: list[Turno] = []
        self.mezzi: list[Mezzo] = []
        self.checklist: list[Checklist] = []
        self.logged_user: Optional[Volontario] = None
        self.promemoria_inviati: set[str] = set()

    def sincronizza_con_firebase(self):
        try:
            from FirebaseConfig import db
            from UtenteFactory import costruisci_utente
            from Turno import Turno
            from Mezzo import Mezzo
            from Corso import Corso
            
            # 1. Sincronizza utenti
            self.volontari = []
            utenti_docs = db.collection("utenti").get()
            for doc in utenti_docs:
                dati = doc.to_dict() or {}
                dati["cod_fiscale"] = doc.id
                try:
                    user_obj = costruisci_utente(dati)
                    self.volontari.append(user_obj)
                except Exception as e:
                    print(f"Errore parsing utente {doc.id}: {e}")
                    
            # 2. Sincronizza mezzi
            self.mezzi = []
            mezzi_docs = db.collection("mezzi").get()
            for doc in mezzi_docs:
                dati = doc.to_dict() or {}
                m = Mezzo(
                    targa=doc.id,
                    tipo=dati.get("tipo", "Ambulanza"),
                    chilometraggioTotale=int(dati.get("chilometraggioTotale", 0) or dati.get("chilometraggio", 0)),
                    stato=dati.get("stato", "Disponibile"),
                    dataScadenzaAssicurazione=dati.get("dataScadenzaAssicurazione", "")
                )
                self.mezzi.append(m)
                
            # 3. Sincronizza corsi
            self.corsi = []
            corsi_docs = db.collection("corsi").get()
            for doc in corsi_docs:
                dati = doc.to_dict() or {}
                c = Corso(
                    id=doc.id,
                    titolo=str(dati.get("titolo") or dati.get("nome") or ""),
                    nome=str(dati.get("nome") or dati.get("titolo") or ""),
                    dataInizio=str(dati.get("dataInizio") or ""),
                    dataFine=str(dati.get("dataFine") or ""),
                    esito=bool(dati.get("esito", False)),
                    checklist=dati.get("checklist", []),
                    scadenza=str(dati.get("scadenza") or ""),
                    direttore=str(dati.get("direttore") or ""),
                    luogo=str(dati.get("luogo") or ""),
                    orari=str(dati.get("orari") or ""),
                    requisitiIscrizione=str(dati.get("requisitiIscrizione") or ""),
                    maxPartecipanti=int(dati.get("maxPartecipanti", 20) or 20)
                )
                
                # Associa partecipanti e certificati
                partecipanti_ids = dati.get("partecipanti_ids", []) or []
                certificati_ids = dati.get("certificati_ids", []) or dati.get("completati_ids", []) or []
                c.certificati_ids = certificati_ids

                for p_id in partecipanti_ids:
                    v = self.get_volontario(p_id)
                    if v:
                        if v not in c.partecipanti:
                            c.partecipanti.append(v)
                        if c not in v.formazione:
                            v.formazione.append(c)

                for cert_id in certificati_ids:
                    v = self.get_volontario(cert_id)
                    if v:
                        if c not in v.corsi_frequentati:
                            v.corsi_frequentati.append(c)
                        if c in v.formazione:
                            v.formazione.remove(c)

                # Associa a tutti i volontari se presente nelle loro qualifiche o corsi frequentati salvati
                for v in self.volontari:
                    v_qualifiche = [str(q).strip().upper() for q in getattr(v, "qualifiche", [])]
                    v_cf_ids = getattr(v, "corsi_frequentati_ids", [])
                    if (c.titolo.strip().upper() in v_qualifiche or 
                        c.nome.strip().upper() in v_qualifiche or
                        c.id in v_cf_ids):
                        if c not in v.corsi_frequentati:
                            v.corsi_frequentati.append(c)
                        if c in v.formazione:
                            v.formazione.remove(c)
                
                self.corsi.append(c)

            # 4. Sincronizza turni
            self.turni = []
            turni_docs = db.collection("turni").get()
            for doc in turni_docs:
                dati = doc.to_dict() or {}
                t = Turno(
                    id=doc.id,
                    data=str(dati.get("data") or ""),
                    luogoDestinazione=str(dati.get("luogoDestinazione") or dati.get("luogo") or ""),
                    luogoPrelevamento=str(dati.get("luogoPrelevamento") or dati.get("luogo") or ""),
                    oraInizio=str(dati.get("oraInizio") or ""),
                    oraFine=str(dati.get("oraFine") or ""),
                    patenteRichiesta=str(dati.get("patenteRichiesta") or dati.get("corso_richiesto") or ""),
                    paziente=str(dati.get("paziente") or ""),
                    paziente_nome=str(dati.get("paziente_nome") or ""),
                    paziente_cognome=str(dati.get("paziente_cognome") or ""),
                    paziente_cf=str(dati.get("paziente_cf") or ""),
                    personeRichieste=int(dati.get("personeRichieste", 1)),
                    stato=str(dati.get("stato") or "Proposto"),
                    tipoServizio=str(dati.get("tipoServizio") or ""),
                    mezzo_targa=str(dati.get("mezzo_targa") or ""),
                    checklist=bool(dati.get("checklist", False))
                )
                t.persone_richieste = dati.get("persone_richieste") or {"volontario": t.personeRichieste}
                
                # Associa i volontari iscritti
                volontari_ids = dati.get("volontari_ids", [])
                t.volontari_ruoli = dati.get("volontari_ruoli", {})
                for v_id in volontari_ids:
                    v = self.get_volontario(str(v_id))
                    if v:
                        if v not in t.volontari_assegnati:
                            t.volontari_assegnati.append(v)
                        if hasattr(v, "turni_assegnati") and t not in v.turni_assegnati:
                            v.turni_assegnati.append(t)
                
                # Associa mezzo se presente
                mezzo_targa = str(dati.get("mezzo_targa") or "").strip()
                if mezzo_targa:
                    mezzo_obj = next((m for m in self.mezzi if m.targa.strip().upper() == mezzo_targa.upper()), None)
                    if mezzo_obj:
                        t.mezzo = mezzo_obj
                        if t not in mezzo_obj.turni_assegnati:
                            mezzo_obj.turni_assegnati.append(t)
                        
                self.turni.append(t)
                
            print(f"🔄 Sincronizzazione Firebase completata: {len(self.volontari)} utenti, {len(self.turni)} turni.")
        except Exception as e:
            print(f"⚠️ Errore durante la sincronizzazione con Firebase: {e}")

    # --- Login / profilo ---
    def login(self, cod_fiscale: str) -> bool:
        volontario = self.get_volontario(cod_fiscale)
        if volontario:
            self.logged_user = volontario
            return True
        return False

    def aggiorna_profilo(self, cod_fiscale: str, email: str | None = None, telefono: str | None = None, nome: str | None = None, cognome: str | None = None, nascita: str | None = None):
        volontario = self.get_volontario(cod_fiscale)
        if volontario:
            if email:
                volontario.email = email
            if telefono:
                volontario.telefono = telefono
            if nome:
                volontario.nome = nome
            if cognome:
                volontario.cognome = cognome
            if nascita:
                volontario.nascita = nascita

    # --- Gestione volontari ---
    def aggiungi_volontario(self, volontario: Volontario):
        self.volontari.append(volontario)

    def rimuovi_volontario(self, cod_fiscale: str):
        self.volontari = [v for v in self.volontari if v.cod_fiscale != cod_fiscale]

    def get_volontario(self, cod_fiscale: str) -> Optional[Volontario]:
        cf_target = cod_fiscale.strip().upper()
        for v in self.volontari:
            if v.cod_fiscale.strip().upper() == cf_target:
                return v
        return None

    def assegna_referente(self, cod_fiscale_volontario: str, cod_fiscale_referente: str):
        volontario = self.get_volontario(cod_fiscale_volontario)
        referente = self.get_volontario(cod_fiscale_referente)
        if volontario and isinstance(referente, Referente):
            volontario.referente = referente

    def prenota_turno(self, cod_fiscale: str, id_turno: str | int):
        volontario = self.get_volontario(cod_fiscale)
        turno = next((t for t in self.turni if t.id == str(id_turno) or getattr(t, "id_turno", None) == id_turno), None)

        if not volontario:
            print("⚠️ Volontario non trovato.")
            return
        if not turno:
            print("⚠️ Turno non trovato.")
            return

        turno.assegna_turno(volontario)

    # --- Gestione corsi ---
    def aggiungi_corso(self, corso: Corso):
        self.corsi.append(corso)

    def carica_corso_al_volontario(self, cod_fiscale: str, corso: Corso):
        volontario = self.get_volontario(cod_fiscale)
        if volontario and corso not in volontario.formazione:
            volontario.formazione.append(corso)

    def notifica_corsi_in_scadenza(self) -> list[dict]:
        avvisi = []
        for corso in self.corsi:
            try:
                if hasattr(corso, "sta_per_scadere") and corso.sta_per_scadere():
                    avviso = {
                        "tipo": "corso",
                        "livello": "warning",
                        "titolo": f"Corso in scadenza: {corso.titolo or corso.nome}",
                        "dettaglio": f"Scadenza prevista: {getattr(corso, 'scadenza', 'N/D')}",
                        "oggetto": corso
                    }
                    avvisi.append(avviso)
                    print(f"⚠️ Corso '{corso.nome}' in scadenza!")
            except Exception:
                pass
        return avvisi

    # --- Gestione turni ---
    def aggiungi_turno(self, turno: Turno):
        self.turni.append(turno)

    def assegna_turno(self, cod_fiscale: str, turno: Turno):
        volontario = self.get_volontario(cod_fiscale)
        if volontario:
            volontario.prenota_turno(turno)
            turno.assegna_turno(volontario)

    def annulla_turno(self, cod_fiscale: str, turno: Turno):
        volontario = self.get_volontario(cod_fiscale)
        if volontario:
            volontario.annulla_prenotazione(turno)
            turno.rimuovi_volontario(volontario)

    def notifica_turni_scoperti(self) -> list[dict]:
        avvisi = []
        for turno in self.turni:
            persone_richieste = getattr(turno, "personeRichieste", 1)
            iscritti = len(getattr(turno, "volontari_assegnati", []))
            if iscritti == 0 or iscritti < persone_richieste:
                mancanti = max(0, persone_richieste - iscritti)
                avviso = {
                    "tipo": "turno",
                    "livello": "danger" if iscritti == 0 else "warning",
                    "titolo": f"Turno scoperto: {turno.tipoServizio or 'Servizio'} ({turno.data})",
                    "dettaglio": f"{turno.fascia_oraria} @ {turno.luogoDestinazione or turno.luogo} (Mancano {mancanti} volontari)",
                    "oggetto": turno
                }
                avvisi.append(avviso)
                print(f"⚠️ Turno {turno.id} ancora scoperto (iscritti: {iscritti}/{persone_richieste})")
        return avvisi

    def invia_promemoria_servizi_24h(self) -> list[dict]:
        """
        Requisito RNF4: Notifica promemoria servizio 24 ore prima dell'inizio del turno.
        
        Logica applicativa:
        1. Finestra temporale: individua i turni pianificati per la giornata odierna o per l'indomani (lookahead 24h).
        2. Idempotenza e deduplicazione: genera una chiave composita univoca ('idTurno_codFiscale_data')
           memorizzata nel set in-memory 'self.promemoria_inviati'. Questo impedisce l'invio duplicato di email
           al medesimo soccorritore in caso di sincronizzazioni o verifiche successive.
        3. Dispatch asincrono / simulato tramite EmailService con dettagli operativi (mezzo, orario, checklist).
        """
        from datetime import datetime, timedelta
        from EmailService import EmailService
        
        notifiche = []
        oggi = datetime.now()
        domani_str = (oggi + timedelta(days=1)).strftime("%Y-%m-%d")
        oggi_str = oggi.strftime("%Y-%m-%d")
        
        for turno in self.turni:
            data_t = str(getattr(turno, "data", "")).strip()
            # Valuta i servizi entro le 24 ore successive
            if data_t in [domani_str, oggi_str]:
                for v in getattr(turno, "volontari_assegnati", []):
                    email = getattr(v, "email", "")
                    # Chiave composita di deduplicazione per garantire l'idempotenza
                    chiave_notifica = f"{turno.id}_{v.cod_fiscale}_{data_t}"
                    if email and "@" in email and chiave_notifica not in self.promemoria_inviati:
                        nome_vol = v.get_nome_completo() if hasattr(v, "get_nome_completo") else v.nome
                        servizio = turno.tipoServizio or "Servizio Operativo"
                        orario = turno.fascia_oraria or f"{turno.oraInizio} - {turno.oraFine}"
                        luogo = turno.luogo
                        
                        testo = (
                            f"Gentile {nome_vol},\n\n"
                            f"ti ricordiamo che nelle prossime 24 ore hai in programma il seguente servizio CRI:\n\n"
                            f"📌 Tipologia: {servizio}\n"
                            f"📅 Data: {turno.data}\n"
                            f"⏰ Orario: {orario}\n"
                            f"📍 Tratta / Luogo: {luogo}\n"
                            f"🚑 Mezzo assegnato: {turno.mezzo_targa or 'Da definire'}\n\n"
                            f"Ricordati di verificare la checklist del mezzo e i presidi sanitari prima della partenza.\n\n"
                            f"Comitato Croce Rossa Italiana"
                        )
                        
                        EmailService.inviaMail(
                            destinatario=email,
                            messaggio=testo,
                            oggetto=f"⏰ Promemoria Servizio CRI: {servizio} del {turno.data}"
                        )
                        self.promemoria_inviati.add(chiave_notifica)
                        notifiche.append({
                            "volontario": v,
                            "volontario_cf": getattr(v, "cod_fiscale", ""),
                            "turno": turno,
                            "id_turno": getattr(turno, "id", ""),
                            "email": email,
                            "data": data_t
                        })
                        print(f"📧 [RNF4 Promemoria] Inviato promemoria turno a {email} per il {data_t}")
        return notifiche

    def esegui_backup(self, base_dir: str = "backups") -> tuple[bool, str]:
        """Esegue il backup periodico automatico di sistema (RF23)."""
        from BackupService import BackupService
        return BackupService.esegui_backup(self, base_dir=base_dir)

    def get_avvisi_sistema(self) -> list[dict]:
        avvisi = []
        avvisi.extend(self.notifica_turni_scoperti())
        avvisi.extend(self.notifica_corsi_in_scadenza())
        # Controllo scadenze mezzi
        from datetime import datetime, timedelta
        oggi = datetime.today()
        for mezzo in self.mezzi:
            scad = getattr(mezzo, "dataScadenzaAssicurazione", "")
            if scad:
                try:
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                        try:
                            dt = datetime.strptime(scad, fmt)
                            if dt < oggi:
                                avvisi.append({
                                    "tipo": "mezzo",
                                    "livello": "danger",
                                    "titolo": f"Assicurazione scaduta: {mezzo.targa}",
                                    "dettaglio": f"Scaduta il {scad} ({mezzo.tipo})",
                                    "oggetto": mezzo
                                })
                            elif dt <= oggi + timedelta(days=30):
                                avvisi.append({
                                    "tipo": "mezzo",
                                    "livello": "warning",
                                    "titolo": f"Assicurazione in scadenza: {mezzo.targa}",
                                    "dettaglio": f"Scade il {scad} ({mezzo.tipo})",
                                    "oggetto": mezzo
                                })
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass
        return avvisi

    # --- Gestione mezzi ---
    def aggiungi_mezzo(self, mezzo: Mezzo):
        self.mezzi.append(mezzo)

    def assegna_mezzo_a_turno(self, mezzo: Mezzo, turno: Turno):
        turno.assegna_mezzo(mezzo)

    def visualizza_stato_mezzi(self):
        for mezzo in self.mezzi:
            stato = "disponibile" if mezzo.disponibile else "non disponibile"
            print(f"🚐 Mezzo {mezzo.targa} - {stato}")

    # --- Checklist (opzionale) ---
    def aggiungi_checklist(self, item: Checklist):
        self.checklist.append(item)

    def visualizza_turni_disponibili(self):
        return [turno for turno in self.turni if turno.stato in ["Proposto", "Aperto"]]

    def visualizza_turni_di_volontario(self, cod_fiscale: str):
        volontario = self.get_volontario(cod_fiscale)
        if volontario:
            return volontario.turni_assegnati
        return []

    def visualizza_rubrica(self):
        for v in self.volontari:
            print(f"{v.nome} {v.cognome} - {v.email} - {v.telefono}")

    def stampa_report_volontario(self, cod_fiscale: str) -> str:
        volontario = self.get_volontario(cod_fiscale)
        if not volontario:
            return "⚠️ Volontario non trovato."

        report = []
        report.append(f"🧾 REPORT VOLONTARIO: {volontario.nome} {volontario.cognome}")
        report.append("-" * 40)
        report.append(f"Codice fiscale : {volontario.cod_fiscale}")
        report.append(f"Email : {volontario.email}")
        report.append(f"Totale ore : {volontario.calcola_ore_totali():.2f} h")

        if not volontario.turni_assegnati:
            report.append("\nNessun turno assegnato.")
            return "\n".join(report)

        report.append("\n🗓️ Turni assegnati:")
        for turno in volontario.turni_assegnati:
            ore = volontario.ore_lavorate.get(turno.id_turno, 0.0)
            report.append(f"- {turno.data} | {turno.fascia_oraria} | Servizio: {turno.tipoServizio} | Ore: {ore:.2f}")

        return "\n".join(report)

    def riepilogo_testuale(self) -> str:
        return (
            f"📋 Riepilogo Sistema:\n\n"
            f"👥 Volontari: {len(self.volontari)}\n"
            f"🎓 Corsi: {len(self.corsi)}\n"
            f"📅 Turni: {len(self.turni)}\n"
            f"🚐 Mezzi: {len(self.mezzi)}\n"
            f"✅ Checklist: {len(self.checklist)}"
        )
