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

    def crea_corso(self, nome_corso: str, elenco_corsi: list):
        if nome_corso not in elenco_corsi:
            elenco_corsi.append(nome_corso)
            print(f"{self.nome} ha creato il corso '{nome_corso}'.")
        else:
            print(f"Il corso '{nome_corso}' esiste già.")

    def approva_corso(self, volontario: Volontario, corso: str):
        if corso in self.formazione:
            print(f"{self.nome} approva l'iscrizione di {volontario.nome} al corso '{corso}'.")
        else:
            print(f"{self.nome} non può approvare il corso '{corso}' perché non è nel suo ambito di formazione.")

    def attesta_partecipazione(self, volontario: Volontario, corso: str):
        if corso not in volontario.corsi_frequentati:
            volontario.corsi_frequentati.append(corso)
            print(f"{self.nome} ha attestato la partecipazione di {volontario.nome} al corso '{corso}'.")
        else:
            print(f"{volontario.nome} ha già completato il corso '{corso}'.")
