from typing import List
from Volontario import Volontario
from Referente import Referente
from Corso import Corso
from Turno import Turno
from Mezzo import Mezzo

class Sistema:
    def __init__(self):
        self.volontari: List[Volontario] = []
        self.referenti: List[Referente] = []
        self.corsi: List[Corso] = []
        self.turni: List[Turno] = []
        self.mezzi: List[Mezzo] = []

    # --- GESTIONE VOLONTARI ---
    def aggiungi_volontario(self, volontario: Volontario):
        self.volontari.append(volontario)
        print(f"Volontario {volontario.nome} {volontario.cognome} aggiunto.")

    def get_volontario_by_email(self, email: str) -> Volontario:
        return next((v for v in self.volontari if v.email == email), None)

    # --- GESTIONE REFERENTI ---
    def aggiungi_referente(self, referente: Referente):
        self.referenti.append(referente)
        print(f"Referente {referente.nome} {referente.cognome} aggiunto.")

    # --- GESTIONE CORSI ---
    def crea_corso(self, nome: str, data: str, tipo: str, checklist: list, referente: Referente):
        corso = Corso(nome, data, tipo, checklist)
        self.corsi.append(corso)
        referente.crea_corso(nome, self.corsi)
        print(f"Corso '{nome}' creato e gestito da {referente.nome}.")
        return corso

    def iscrivi_volontario_a_corso(self, volontario: Volontario, corso: Corso):
        if volontario not in corso.partecipanti:
            corso.partecipanti.append(volontario)
            print(f"{volontario.nome} iscritto al corso '{corso.nome}'.")
        else:
            print(f"{volontario.nome} è già iscritto al corso '{corso.nome}'.")

    # --- GESTIONE TURNI ---
    def crea_turno(self, turno: Turno):
        self.turni.append(turno)
        print(f"Turno del {turno.data} creato.")

    def assegna_volontario_a_turno(self, turno: Turno, volontario: Volontario):
        turno.assegna_volontario(volontario)

    def assegna_mezzo_a_turno(self, turno: Turno, mezzo: Mezzo):
        turno.assegna_mezzo(mezzo)

    # --- GESTIONE MEZZI ---
    def aggiungi_mezzo(self, mezzo: Mezzo):
        self.mezzi.append(mezzo)
        print(f"Mezzo {mezzo.targa} aggiunto al sistema.")

    def get_mezzo_disponibile(self) -> Mezzo:
        for mezzo in self.mezzi:
            if mezzo.disponibile:
                return mezzo
        print("Nessun mezzo disponibile.")
        return None
