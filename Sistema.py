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
        self.volontari: list[Utente] = []
        self.corsi: list[Corso] = []
        self.turni: list[Turno] = []
        self.mezzi: list[Mezzo] = []
        self.checklist: list[Checklist] = []
        self.logged_user: Optional[Utente] = None

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
                    scadenza=str(dati.get("scadenza") or "")
                )
                
                # Associa i partecipanti
                partecipanti_ids = dati.get("partecipanti_ids", [])
                for p_id in partecipanti_ids:
                    v = self.get_volontario(p_id)
                    if v:
                        if v not in c.partecipanti:
                            c.partecipanti.append(v)
                        if c not in v.formazione:
                            v.formazione.append(c)
                        # Se il titolo del corso fa parte delle qualifiche attestate del volontario, aggiungilo ai completati
                        if c.titolo in v.qualifiche or c.nome in v.qualifiche:
                            if c not in v.corsi_frequentati:
                                v.corsi_frequentati.append(c)
                
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
                    personeRichieste=int(dati.get("personeRichieste", 1)),
                    stato=str(dati.get("stato") or "Proposto"),
                    tipoServizio=str(dati.get("tipoServizio") or "")
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
                        if t not in v.turni_assegnati:
                            v.turni_assegnati.append(t)
                        
                self.turni.append(t)
                
            print(f"🔄 Sincronizzazione Firebase completata: {len(self.volontari)} utenti, {len(self.turni)} turni.")
        except Exception as e:
            print(f"⚠️ Errore durante la sincronizzazione con Firebase: {e}")

    # --- Login / profilo ---
    def login(self, cod_fiscale: int) -> bool:
        volontario = self.get_volontario(cod_fiscale)
        if volontario:
            self.logged_user = volontario
            return True
        return False

    # pyrefly: ignore [bad-function-definition]
    def aggiorna_profilo(self, cod_fiscale: int, email: str = None, telefono: str = None, nome: str = None, cognome: str = None, nascita:str = None):
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
    def aggiungi_volontario(self, volontario: Utente):
        self.volontari.append(volontario)

    def rimuovi_volontario(self, cod_fiscale):
        self.volontari = [v for v in self.volontari if str(v.cod_fiscale) != str(cod_fiscale)]

    def get_volontario(self, cod_fiscale) -> Optional[Volontario]:
        for v in self.volontari:
            if str(v.cod_fiscale) == str(cod_fiscale):
                return v
        return None

    def assegna_referente(self, cod_fiscale_volontario: int, cod_fiscale_referente: int):
        volontario = self.get_volontario(cod_fiscale_volontario)
        referente = self.get_volontario(cod_fiscale_referente)
        if volontario and isinstance(referente, Referente):
            volontario.referente = referente

    def prenota_turno(self, cod_fiscale: int, id_turno: int):
        volontario = self.get_volontario(cod_fiscale)
        turno = next((t for t in self.turni if t.id_turno == id_turno), None)

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

    def carica_corso_al_volontario(self, cod_fiscale: int, corso: Corso):
        volontario = self.get_volontario(cod_fiscale)
        if volontario and corso not in volontario.formazione:
            volontario.formazione.append(corso)

    def notifica_corsi_in_scadenza(self):
        for corso in self.corsi:
            if corso.sta_per_scadere():
                print(f"⚠️ Corso '{corso.nome}' in scadenza!")

    # --- Gestione turni ---
    def aggiungi_turno(self, turno: Turno):
        self.turni.append(turno)

    def assegna_turno(self, cod_fiscale: int, turno: Turno):
        volontario = self.get_volontario(cod_fiscale)
        if volontario:
            volontario.prenota_turno(turno)
            turno.assegna_turno(volontario)

    def annulla_turno(self, cod_fiscale: int, turno: Turno):
        volontario = self.get_volontario(cod_fiscale)
        if volontario:
            # pyrefly: ignore [missing-attribute]
            volontario.rimuovi_turno(turno)
            turno.rimuovi_volontario(volontario)

    def notifica_turni_scoperti(self):
        for turno in self.turni:
            if not turno.volontari_assegnati:
                print(f"⚠️ Turno {turno} ancora scoperto!")

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
        return [turno for turno in self.turni if turno.stato == "Proposto"]

    def visualizza_turni_di_volontario(self, cod_fiscale: int):
        volontario = self.get_volontario(cod_fiscale)
        if volontario:
            return volontario.turni_assegnati

    def visualizza_rubrica(self):
        for v in self.volontari:
            print(f"{v.nome} {v.cognome} - {v.email} - {v.telefono}")

    def stampa_report_volontario(self, cod_fiscale: int) -> str:
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
