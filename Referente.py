from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from Corso import Corso
    from Volontario import Volontario

from Volontario import Volontario

from Utente import Utente

class Referente(Utente):
    def __init__(
        self,
        cod_fiscale: int,
        nome: str,
        cognome: str,
        email: str,
        nascita: str,
        telefono: str,
        curriculum: str,
        patenti: list[str],
        formazione: list,
        compagnia_appartenenza: str,
        disponibilita: list[str],
        area_gestita: str
    ):
        super().__init__(cod_fiscale, nome, cognome, email, nascita, telefono, ruolo="referente")
        self.curriculum = curriculum
        self.patenti = patenti
        self.formazione = formazione
        self.compagnia_appartenenza = compagnia_appartenenza
        self.disponibilita = disponibilita
        self.area_gestita = area_gestita

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


    def modifica_corso(self, corso: Corso, nome: str = None, descrizione: str = None, durata_ore: int = None):
        if nome is not None:
            corso.nome = nome
        if descrizione is not None:
            corso.descrizione = descrizione
        if durata_ore is not None:
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
