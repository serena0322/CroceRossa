from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
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

    # --- Login / profilo ---
    def login(self, cod_fiscale: int) -> bool:
        volontario = self.get_volontario(cod_fiscale)
        if volontario:
            self.logged_user = volontario
            return True
        return False

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
    def aggiungi_volontario(self, volontario: Volontario):
        self.volontari.append(volontario)

    def rimuovi_volontario(self, cod_fiscale: int):
        self.volontari = [v for v in self.volontari if v.cod_fiscale != cod_fiscale]

    def get_volontario(self, cod_fiscale: int) -> Optional[Volontario]:
        for v in self.volontari:
            if v.cod_fiscale == cod_fiscale:
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
