from typing import List
from Volontario import Volontario
from Mezzo import Mezzo  # Assumendo tu abbia una classe Mezzo

class Turno:
    def __init__(
        self,
        id_turno: int,
        data: str,
        fascia_oraria: str,   # es. "08:00 - 14:00"
        tipo: str,            # A o B
        compagnia: str,
        dispositivi_richiesti: List[str],
        corso_richiesto: str = None
    ):
        self.id_turno = id_turno
        self.data = data
        self.fascia_oraria = fascia_oraria
        self.tipo = tipo
        self.compania = compagnia

        self.dispositivi_richiesti = dispositivi_richiesti
        self.corso_richiesto = corso_richiesto

        self.volontari_assegnati: List[Volontario] = []
        self.mezzo: Mezzo = None
        self.checklist_completata = False
        self.stato = "Proposto"  # Proposto, Confermato, Annullato, Concluso

    def assegna_volontario(self, volontario: Volontario):
        if self.corso_richiesto and self.corso_richiesto not in volontario.corsi_frequentati:
            print(f"{volontario.nome} non ha i requisiti per partecipare al turno.")
            return
        self.volontari_assegnati.append(volontario)
        volontario.turni_assegnati.append(self)
        print(f"{volontario.nome} assegnato al turno del {self.data}.")

    def assegna_mezzo(self, mezzo: Mezzo):
        self.mezzo = mezzo
        print(f"Mezzo {mezzo.targa} assegnato al turno del {self.data}.")

    def completa_checklist(self):
        self.checklist_completata = True
        print(f"Checklist completata per il turno del {self.data}.")

    def cambia_stato(self, nuovo_stato: str):
        if nuovo_stato in ["Proposto", "Confermato", "Annullato", "Concluso"]:
            self.stato = nuovo_stato
            print(f"Stato del turno aggiornato a {self.stato}.")
        else:
            print("Stato non valido.")
