from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from Volontario import Volontario
    from Mezzo import Mezzo

class Turno:
    def __init__(
        self,
        id_turno: int,
        data: str,
        fascia_oraria: str,
        tipoServizio: str,
        personeRichieste: str,
        checklist: bool,
        luogo: str,
        paziente: str,
        tempoExtra: str,
        dispositivi_richiesti: List[str],
        corso_richiesto: str = None
    ):
        self.id_turno = id_turno
        self.data = data
        self.fascia_oraria = fascia_oraria
        self.tipoServizio = tipoServizio
        self.personeRichieste = personeRichieste
        self.checklist = checklist
        self.luogo = luogo
        self.paziente = paziente
        self.tempoExtra = tempoExtra
        self.dispositivi_richiesti = dispositivi_richiesti
        self.corso_richiesto = corso_richiesto

        self.volontari_assegnati: List[Volontario] = []
        self.mezzo: Mezzo | None = None
        self.stato = "Proposto"  # Proposto, Confermato, Annullato, Concluso

    def assegna_volontario(self, volontario: Volontario):
        if self.corso_richiesto and self.corso_richiesto not in [c.nome for c in volontario.corsi_frequentati]:
            print(f"{volontario.nome} non ha i requisiti per partecipare al turno.")
            return
        if volontario in self.volontari_assegnati:
            print(f"{volontario.nome} è già assegnato a questo turno.")
            return
        self.volontari_assegnati.append(volontario)
        volontario.turni_assegnati.append(self)
        print(f"{volontario.nome} assegnato al turno del {self.data}.")

    def rimuovi_volontario(self, volontario: Volontario):
        if volontario in self.volontari_assegnati:
            self.volontari_assegnati.remove(volontario)
            volontario.turni_assegnati.remove(self)
            print(f"{volontario.nome} è stato rimosso dal turno del {self.data}.")
        else:
            print(f"{volontario.nome} non era assegnato a questo turno.")

    def assegna_mezzo(self, mezzo: Mezzo):
        self.mezzo = mezzo
        mezzo.assegna_a_turno(self)
        print(f"Mezzo {mezzo.targa} assegnato al turno del {self.data}.")

    def completa_checklist(self):
        self.checklist = True
        print(f"Checklist completata per il turno del {self.data}.")

    def cambia_stato(self, nuovo_stato: str):
        if nuovo_stato in ["Proposto", "Confermato", "Annullato", "Concluso"]:
            self.stato = nuovo_stato
            print(f"Stato del turno aggiornato a {self.stato}.")
        else:
            print("Stato non valido.")

    def is_scoperto(self) -> bool:
        try:
            richieste = int(self.personeRichieste)
        except ValueError:
            print("Valore personeRichieste non valido.")
            return True
        return len(self.volontari_assegnati) < richieste

    def richiede_corso(self) -> bool:
        return self.corso_richiesto is not None

    def dispositivi_mancanti(self, disponibili: List[str]) -> List[str]:
        return [d for d in self.dispositivi_richiesti if d not in disponibili]
