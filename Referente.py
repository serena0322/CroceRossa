from __future__ import annotations

from typing import List, Optional
from Volontario import Volontario

class Referente(Volontario):
    """
    Rappresenta la figura del Referente / Coordinatore di settore della Croce Rossa Italiana.
    Estende formalmente la classe Volontario secondo la gerarchia:
        Utente <-- Volontario <-- Referente
    Eredita tutte le caratteristiche anagrafiche e operative del Volontario
    (oreServizio, patenti, qualifiche) e aggiunge il settore di competenza gestita.

    Attributi UML aggiuntivi: settoreGestito.
    Metodi UML aggiuntivi: getSettoreGestito().
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
        settoreGestito: str = "",
        codiceAutorizzazione: str = "",
        qualifiche: list[str] | None = None,
        oreServizio: int = 0,
        # old name compatibility:
        area_gestita: str | None = None,
        monteOreTotale: int | None = None,
        **kwargs
    ):
        comitato = comitato_appartenenza or kwargs.get("compagnia_appartenenza", "")
        ore = monteOreTotale if monteOreTotale is not None else oreServizio
        kwargs.pop("ruolo", None)
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
            oreServizio=ore,
            qualifiche=qualifiche if qualifiche is not None else [],
            **kwargs
        )
        self.settoreGestito = area_gestita if area_gestita is not None else settoreGestito
        self.codiceAutorizzazione = str(codiceAutorizzazione or kwargs.get("codice_autorizzazione", "1234")).strip()

    def getSettoreGestito(self) -> str:
        """Restituisce il settore operativo di competenza del referente (UML)."""
        return self.settoreGestito

    def verificaCodiceAutorizzazione(self, codice: str) -> bool:
        """Verifica la validità del codice autorizzazione per la registrazione referente (UML CreaAccountReferente)."""
        return self.codiceAutorizzazione == str(codice).strip()

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "monteOreTotale": getattr(self, "oreServizio", 0),
            "patenti": self.patenti,
            "qualifiche": getattr(self, "qualifiche", []),
            "curriculum": self.curriculum,
            "comitato_appartenenza": self.comitato_appartenenza,
            "area_gestita": self.settoreGestito,
            "settoreGestito": self.settoreGestito,
            "codiceAutorizzazione": self.codiceAutorizzazione,
        })
        return d

    def __repr__(self) -> str:
        return f"<Referente {self.getNomeCompleto()} - Settore: {self.settoreGestito}>"
