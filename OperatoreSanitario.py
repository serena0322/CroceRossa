from __future__ import annotations
from Utente import Utente
from typing import List

class OperatoreSanitario(Utente):
    def __init__(
        self,
        cod_fiscale: int,
        nome: str,
        cognome: str,
        email: str,
        nascita: str,
        telefono: str,
        ruolo: str = "operatore_sanitario",
        specializzazioni: List[str] = [],
        disponibilita: List[str] = []
    ):
        super().__init__(
            cod_fiscale=cod_fiscale,
            nome=nome,
            cognome=cognome,
            email=email,
            nascita=nascita,
            telefono=telefono,
            ruolo=ruolo
        )
        self.specializzazioni = specializzazioni
        self.disponibilita = disponibilita

    def aggiungi_specializzazione(self, specializzazione: str):
        if specializzazione not in self.specializzazioni:
            self.specializzazioni.append(specializzazione)
            print(f"✅ Specializzazione '{specializzazione}' aggiunta a {self.nome}.")

    def è_disponibile(self, giorno: str) -> bool:
        return giorno in self.disponibilita

    def descrizione_professionale(self) -> str:
        return f"{self.get_nome_completo()} - Specializzazioni: {', '.join(self.specializzazioni)}"
