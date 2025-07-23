from __future__ import annotations
from typing import List

class Checklist:
    def __init__(self, controlli: List[str], km_inizio: str, km_fine: str):
        self.km_inizio = km_inizio
        self.km_fine = km_fine
        self.controlli = {elemento: False for elemento in controlli}

    def completa_elemento(self, elemento: str):
        if elemento in self.controlli:
            self.controlli[elemento] = True
            print(f"✅ Elemento '{elemento}' completato.")
        else:
            print(f"⚠️ L'elemento '{elemento}' non è presente nella checklist.")

    def annulla_elemento(self, elemento: str):
        if elemento in self.controlli:
            self.controlli[elemento] = False
            print(f"❌ Elemento '{elemento}' segnato come non completato.")
        else:
            print(f"⚠️ L'elemento '{elemento}' non è presente nella checklist.")

    def checklist_completata(self) -> bool:
        return all(self.controlli.values())

    def riepilogo(self):
        print(f"📋 Checklist (km iniziali: {self.km_inizio}, finali: {self.km_fine}):")
        for elem, stato in self.controlli.items():
            simbolo = "✓" if stato else "✗"
            print(f"  {simbolo} {elem}")
