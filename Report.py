class Report:
    def __init__(self, id: str, kmPercorsi: int, noteIntervento: str, oreEffettive: int):
        self.id = id
        self.kmPercorsi = kmPercorsi
        self.noteIntervento = noteIntervento
        self.oreEffettive = oreEffettive

    def getKmPercorsi(self) -> int:
        return self.kmPercorsi

    def getOreEffettive(self) -> int:
        return self.oreEffettive
