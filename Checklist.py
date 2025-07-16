class Checklist:
    def __init__(self, elementi: list):
        # Ogni elemento è una stringa, inizialmente non completato
        self.elementi = {elemento: False for elemento in elementi}

    def completa_elemento(self, elemento: str):
        if elemento in self.elementi:
            self.elementi[elemento] = True
            print(f"Elemento '{elemento}' completato.")
        else:
            print(f"L'elemento '{elemento}' non è presente nella checklist.")

    def annulla_elemento(self, elemento: str):
        if elemento in self.elementi:
            self.elementi[elemento] = False
            print(f"Elemento '{elemento}' segnato come non completato.")
        else:
            print(f"L'elemento '{elemento}' non è presente nella checklist.")

    def checklist_completata(self):
        return all(self.elementi.values())

    def riepilogo(self):
        for elem, stato in self.elementi.items():
            stato_txt = "✓" if stato else "✗"
            print(f"{stato_txt} {elem}")
