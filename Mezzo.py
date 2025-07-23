from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Turno import Turno

class Mezzo:
    def __init__(
        self,
        targa: str,
        tipo: str,  # es. "Ambulanza", "Automedica", "Furgone"
        chilometraggio: int,
        stato: list[str],
        dispositivi_richiesti: list[str],
        checklist: list[str],
        disponibile: bool = True
    ):
        self.targa = targa
        self.tipo = tipo
        self.chilometraggio = chilometraggio
        self.stato = stato
        self.dispositivi_presenti = dispositivi_richiesti
        self.checklist = checklist
        self.disponibile = disponibile
        self.turni_assegnati: list[Turno] = []

    def assegna_a_turno(self, turno: Turno):
        if not self.disponibile:
            print(f"🚫 Il mezzo {self.targa} non è attualmente disponibile.")
            return
        self.turni_assegnati.append(turno)
        self.disponibile = False
        print(f"✅ Il mezzo {self.targa} è stato assegnato al turno del {turno.data}.")

    def aggiorna_km(self, nuovi_km: int):
        if nuovi_km >= self.chilometraggio:
            self.chilometraggio = nuovi_km
            print(f"📈 Chilometraggio aggiornato a {self.chilometraggio} km.")
        else:
            print("⚠️ Errore: il chilometraggio inserito è inferiore a quello attuale.")

    def libera_mezzo(self):
        self.disponibile = True
        print(f"🟢 Il mezzo {self.targa} è ora disponibile.")
