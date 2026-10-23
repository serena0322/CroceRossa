from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from Turno import Turno
    from Volontario import Volontario


class Prenotazione:
    """
    Rappresenta la prenotazione di un volontario a un turno di servizio.
    Classe conforme al package Attivita del diagramma delle classi UML.

    Attributi UML:
        codice: str
        dataPrenotazione: str (Data)
        turno: Turno
        volontario: Volontario
    """
    def __init__(
        self,
        codice: str = "",
        dataPrenotazione: str = "",
        turno: Turno | None = None,
        volontario: Volontario | None = None,
        **kwargs
    ):
        self.codice = codice or kwargs.get("id", f"PREN_{getattr(turno, 'codice', '')}_{getattr(volontario, 'cod_fiscale', '')}")
        self.dataPrenotazione = dataPrenotazione or datetime.now().strftime("%Y-%m-%d")
        self.turno = turno
        self.volontario = volontario

    def notificaModifica(self) -> None:
        """Invia notifica di modifica del turno al volontario (UML CUDTurno)."""
        if self.volontario and hasattr(self.volontario, "email"):
            from EmailService import EmailService
            t_info = f"{self.turno.codice} del {self.turno.data}" if self.turno else ""
            EmailService.inviaMail(
                destinatario=self.volontario.email,
                messaggio=f"Gentile {self.volontario.getNomeCompleto()},\nil turno {t_info} a cui sei iscritto è stato modificato.",
                oggetto=f"Notifica Modifica Turno CRI {t_info}"
            )

    def notificaEliminazione(self) -> None:
        """Invia notifica di cancellazione del turno al volontario (UML CUDTurno)."""
        if self.volontario and hasattr(self.volontario, "email"):
            from EmailService import EmailService
            t_info = f"{self.turno.codice} del {self.turno.data}" if self.turno else ""
            EmailService.inviaMail(
                destinatario=self.volontario.email,
                messaggio=f"Gentile {self.volontario.getNomeCompleto()},\nil turno {t_info} a cui eri iscritto è stato cancellato.",
                oggetto=f"Notifica Cancellazione Turno CRI {t_info}"
            )

    def inviaPromemoria(self) -> None:
        """Invia il promemoria del turno al volontario (UML InviaPromemoriaTurno)."""
        if self.volontario and hasattr(self.volontario, "email"):
            from EmailService import EmailService
            t_info = f"{self.turno.codice} del {self.turno.data}" if self.turno else ""
            EmailService.inviaMail(
                destinatario=self.volontario.email,
                messaggio=f"Gentile {self.volontario.getNomeCompleto()},\nti ricordiamo il servizio CRI per il turno {t_info}.",
                oggetto=f"Promemoria Turno CRI {t_info}"
            )

    def to_dict(self) -> dict:
        return {
            "codice": self.codice,
            "dataPrenotazione": self.dataPrenotazione,
            "turno_codice": getattr(self.turno, "codice", ""),
            "volontario_cf": getattr(self.volontario, "cod_fiscale", "")
        }
