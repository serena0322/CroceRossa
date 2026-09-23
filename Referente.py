from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from Corso import Corso
    from Volontario import Volontario

from Volontario import Volontario

from Utente import Utente

class Referente(Volontario):
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
        compagnia_appartenenza: str = "",
        disponibilita: list[str] | None = None,
        area_gestita: str = "",
        qualifiche: list[str] | None = None,
        monteOreTotale: int = 0,
        **kwargs
    ):
        super().__init__(
            cod_fiscale=str(cod_fiscale),
            nome=nome,
            cognome=cognome,
            email=email,
            data_nascita=nascita,
            telefono=telefono,
            ruolo="referente",
            curriculum=curriculum,
            patenti=patenti if patenti is not None else [],
            formazione=formazione if formazione is not None else [],
            compagnia_appartenenza=compagnia_appartenenza,
            disponibilita=disponibilita if disponibilita is not None else [],
            monteOreTotale=monteOreTotale,
            qualifiche=qualifiche if qualifiche is not None else []
        )
        self.area_gestita = area_gestita
        self.codice_autorizzazione = kwargs.get("codice_autorizzazione", "CRI2026")

    def getAreaGestita(self) -> str:
        return self.area_gestita

    def assegnaTurno(self, volontario: Volontario, turno: Turno) -> bool:
        """Assegna il turno al volontario (UML)."""
        return turno.aggiungiVolontario(volontario)

    def attestaPartecipazione(self, volontario: Volontario, corso: Corso):
        """Alias UML per attesta_partecipazione."""
        self.attesta_partecipazione(volontario, corso)

    def creaCorso(self, titolo: str, ore: int = 10) -> Corso:
        """Crea un nuovo corso formativo con titolo e monte ore (UML)."""
        return self.crea_corso(nome=titolo, titolo=titolo, durata_ore=ore, checklist=[])

    def crea_corso(
            self,
            nome: str,
            titolo: str,
            durata_ore: int,
            checklist: list[dict]
    ) -> Corso:
        oggi = datetime.today()
        data_inizio = oggi.strftime("%Y-%m-%d")
        data_fine = (oggi + timedelta(hours=durata_ore)).strftime("%Y-%m-%d")
        scadenza = (oggi + timedelta(days=365)).strftime("%Y-%m-%d")

        nuovo_corso = Corso(
            id=str(uuid4()),
            nome=nome,
            dataInizio=data_inizio,
            esito=False,
            dataFine=data_fine,
            checklist=checklist,
            titolo=titolo,
            scadenza=scadenza
        )
        nuovo_corso.imposta_referente(self)
        print(f"✅ Corso '{nome}' creato con successo.")
        return nuovo_corso

    def elimina_corso(self, corso: Corso, corsi: list[Corso]):
        if corso in corsi:
            # Rimuovi il corso dalla lista generale dei corsi
            corsi.remove(corso)
            print(f"🗑️ Corso '{corso.nome}' eliminato con successo.")

            # Rimuovi il corso dalla formazione e dai frequentati di ogni volontario
            for volontario in corso.partecipanti:
                if corso in volontario.formazione:
                    volontario.formazione.remove(corso)
                if corso in getattr(volontario, 'corsi_frequentati', []):
                    volontario.corsi_frequentati.remove(corso)
                print(f"ℹ️ Corso '{corso.nome}' rimosso anche da {volontario.get_nome_completo()}")
        else:
            print(f"❌ Corso '{corso.nome}' non trovato nella lista.")


    # pyrefly: ignore [bad-function-definition]
    def modifica_corso(self, corso: Corso, nome: str = None, descrizione: str = None, durata_ore: int = None):
        if nome is not None:
            corso.nome = nome
        if descrizione is not None:
            # pyrefly: ignore [missing-attribute]
            corso.descrizione = descrizione
        if durata_ore is not None:
            # pyrefly: ignore [missing-attribute]
            corso.durata_ore = durata_ore

    def assegna_corso_a_volontario(self, volontario: Volontario, corso: Corso):
        if corso.esito:
            if corso not in volontario.formazione:
                volontario.formazione.append(corso)
                print(f"{corso.nome} assegnato a {volontario.get_nome_completo()}")
            else:
                print(f"{volontario.get_nome_completo()} ha già il corso {corso.nome}.")
        else:
            print(f"❌ Il corso {corso.nome} non è stato superato da {volontario.get_nome_completo()}.")

    def attesta_partecipazione(self, volontario: Volontario, corso: Corso):
        if corso not in volontario.corsi_frequentati:
            volontario.corsi_frequentati.append(corso)
            print(f"{volontario.get_nome_completo()} ha completato il corso {corso.nome}")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "monteOreTotale": getattr(self, "monteOreTotale", 0),
            "patenti": self.patenti,
            "qualifiche": getattr(self, "qualifiche", []),
            "disponibilita": self.disponibilita,
            "curriculum": self.curriculum,
            "compagnia_appartenenza": self.compagnia_appartenenza,
            "area_gestita": self.area_gestita
        })
        return d
