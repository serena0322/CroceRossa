# referente.py

from Volontario import Volontario

class Referente(Volontario):
    def __init__(
        self,
        id_volontario: int,
        nome: str,
        cognome: str,
        email: str,
        nascita: str,
        telefono: str,
        curriculum: str,
        patenti: list,
        formazione: list,
        compagnia_appartenenza: str,
        disponibilità: list,
        area_gestita: str
    ):
        super().__init__(id_volontario, nome, cognome, email, nascita, telefono,
                         curriculum, patenti, formazione, compagnia_appartenenza,
                         disponibilità, ruolo="referente")
        self.area_gestita = area_gestita

    def attesta_partecipazione(self, volontario: Volontario, corso: str):
        if corso not in volontario.corsi_frequentati:
            volontario.corsi_frequentati.append(corso)
            print(f"{self.nome} ha attestato la partecipazione di {volontario.nome} al corso '{corso}'.")
        else:
            print(f"{volontario.nome} ha già completato il corso '{corso}'.")
