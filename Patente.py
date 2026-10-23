from __future__ import annotations


class Patente:
    """
    Rappresenta una patente di guida posseduta da un Volontario della Croce Rossa Italiana.
    Classe conforme al diagramma delle classi UML.

    Attributi UML:
        codice: str        — identificativo univoco della patente
        tipo: str          — categoria della patente (es. A, B, C, D, BE, CE...)
        dataScadenza: str  — data di scadenza nel formato YYYY-MM-DD
    """

    def __init__(
        self,
        codice: str = "",
        tipo: str = "",
        dataScadenza: str = "",
        # Compatibility arguments per il DB JSON esistente:
        numero_patente: str | None = None,
        scadenza_patente: str | None = None,
        **kwargs
    ):
        # Supporta i vecchi nomi per retrocompatibilità con il DB JSON
        self.codice = numero_patente if numero_patente is not None else codice
        self.tipo = tipo
        self.dataScadenza = scadenza_patente if scadenza_patente is not None else dataScadenza

    def __repr__(self) -> str:
        return f"<Patente {self.tipo} — Codice: {self.codice} — Scadenza: {self.dataScadenza}>"

    def to_dict(self) -> dict:
        """Serializza la patente in dizionario per il salvataggio nel database locale JSON."""
        return {
            "codice": self.codice,
            "tipo": self.tipo,
            "dataScadenza": self.dataScadenza,
        }

    def isScaduta(self) -> bool:
        """Verifica se la patente è scaduta rispetto alla data odierna (UML PrenotaTurno)."""
        from datetime import datetime
        try:
            return datetime.strptime(self.dataScadenza, "%Y-%m-%d").date() < datetime.today().date()
        except Exception:
            return False

    def rinnova(self, nuovaData: str) -> None:
        """Aggiorna la data di scadenza della patente (UML)."""
        self.dataScadenza = nuovaData

    @staticmethod
    def from_dict(d: dict) -> Patente:
        """Deserializza una Patente da un dizionario (DB JSON)."""
        return Patente(
            codice=d.get("codice", d.get("numero_patente", "")),
            tipo=d.get("tipo", ""),
            dataScadenza=d.get("dataScadenza", d.get("scadenza_patente", "")),
        )
