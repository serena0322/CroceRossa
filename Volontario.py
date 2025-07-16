# Volontario.py

class Volontario:
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
        ruolo: str
    ):
        self.id = id_volontario
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.nascita = nascita
        self.telefono = telefono
        self.curriculum = curriculum
        self.patenti = patenti
        self.formazione = formazione              # lista di corsi disponibili o richiesti
        self.compagnia_appartenenza = compagnia_appartenenza
        self.disponibilità = disponibilità        # lista di disponibilità settimanale
        self.ruolo = ruolo

        self.turni_assegnati = []                 # lista di oggetti Turno (o stringhe temporanee)
        self.corsi_frequentati = []              # lista di corsi completati

    def aggiungi_turno(self, turno):
        if turno not in self.turni_assegnati:
            self.turni_assegnati.append(turno)

    def rimuovi_turno(self, turno):
        if turno in self.turni_assegnati:
            self.turni_assegnati.remove(turno)

    def è_disponibile(self, giorno: str) -> bool:
        return giorno in self.disponibilità
