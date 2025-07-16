class Mezzo:
    def __init__(
        self,
        id_mezzo: int,
        targa: str,
        tipo: str,              # es. "Ambulanza", "Automedica", "Furgone"
        km_attuali: int,
        dispositivi_presenti: list,
        checklist: list,
        disponibile: bool = True
    ):
        self.id_mezzo = id_mezzo
        self.targa = targa
        self.tipo = tipo
        self.km_attuali = km_attuali
        self.dispositivi_presenti = dispositivi_presenti  # es. ["defibrillatore", "barella"]
        self.checklist = checklist                        # es. ["controllo olio", "presenza DPI"]
        self.disponibile = disponibile
        self.turni_assegnati = []

    def assegna_a_turno(self, turno):
        if not self.disponibile:
            print(f"Il mezzo {self.targa} non è attualmente disponibile.")
            return
        self.turni_assegnati.append(turno)
        self.disponibile = False
        print(f"Il mezzo {self.targa} è stato assegnato al turno del {turno.data}.")

    def aggiorna_km(self, nuovi_km: int):
        if nuovi_km >= self.km_attuali:
            self.km_attuali = nuovi_km
            print(f"Chilometraggio aggiornato a {self.km_attuali} km.")
        else:
            print("Errore: il chilometraggio inserito è inferiore a quello attuale.")

    def libera_mezzo(self):
        self.disponibile = True
        print(f"Il mezzo {self.targa} è ora disponibile.")
