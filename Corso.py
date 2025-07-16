# corso.py
class Corso:
    def __init__(self, nome: str, data: str, tipo: str, checklist: list):
        self.nome = nome
        self.data = data
        self.tipo = tipo  # A/B
        self.checklist = checklist
        self.partecipanti = []  # lista di Volontari
        self.stato = "Proposto"  # o "InCorso", "Concluso"
