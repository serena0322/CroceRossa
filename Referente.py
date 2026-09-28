from __future__ import annotations

from typing import List, Optional
from Volontario import Volontario

class Referente(Volontario):
    """
    Rappresenta la figura del Referente / Coordinatore di settore della Croce Rossa Italiana.
    Estende formalmente la classe Volontario secondo la gerarchia:
        Utente <-- Volontario <-- Referente
    Eredita tutte le caratteristiche anagrafiche e operative del Volontario
    (monte ore, patenti, qualifiche) e aggiunge l'area di competenza gestita
    e il codice di autorizzazione.
    
    Come da requisiti architetturali UML, i metodi operativi di creazione/modifica turni e corsi
    risiedono nei rispettivi Controller (GestioneTurniController e GestioneFormazioneController).
    """
    def __init__(
        self,
        cod_fiscale: str = "",
        nome: str = "",
        cognome: str = "",
        email: str = "",
        nascita: str = "",
        telefono: str = "",
        curriculum: str = "",
        patenti: list[str] | None = None,
        formazione: list | None = None,
        comitato_appartenenza: str = "",
        area_gestita: str = "",
        qualifiche: list[str] | None = None,
        monteOreTotale: int = 0,
        **kwargs
    ):
        comitato = comitato_appartenenza or kwargs.get("compagnia_appartenenza", "")
        super().__init__(
            cod_fiscale=cod_fiscale,
            nome=nome,
            cognome=cognome,
            email=email,
            data_nascita=nascita,
            telefono=telefono,
            ruolo="referente",
            curriculum=curriculum,
            patenti=patenti if patenti is not None else [],
            formazione=formazione if formazione is not None else [],
            comitato_appartenenza=comitato,
            monteOreTotale=monteOreTotale,
            qualifiche=qualifiche if qualifiche is not None else [],
            **kwargs
        )
        self.area_gestita = area_gestita
        self.codice_autorizzazione = kwargs.get("codice_autorizzazione", "CRI2026")

    def getAreaGestita(self) -> str:
        """Restituisce l'area o settore operativo di competenza del referente (UML)."""
        return self.area_gestita

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "monteOreTotale": getattr(self, "monteOreTotale", 0),
            "patenti": self.patenti,
            "qualifiche": getattr(self, "qualifiche", []),
            "curriculum": self.curriculum,
            "comitato_appartenenza": self.comitato_appartenenza,
            "area_gestita": self.area_gestita,
            "codice_autorizzazione": self.codice_autorizzazione
        })
        return d

    def __repr__(self) -> str:
        return f"<Referente {self.get_nome_completo()} - Area: {self.area_gestita}>"
