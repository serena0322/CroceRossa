"""Avvio del programma. Qui vive l'attore Tempo: un QTimer controlla ogni minuto
quali attivita' pianificate vanno eseguite (casi d'uso con attore Tempo)."""
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from attivita.corso import Corso
from attivita.turno import Turno
from dati.gestore_backup import GestoreBackup
from dati.gestore_dati import GestoreDati
from supporto import orologio
from viste.gestione_account.vista_login import VistaLogin

QUINDICI_MINUTI = 15 * 60 * 1000
UN_MINUTO = 60 * 1000

# attivita' giornaliere: nome -> (ora minima, azione)
ATTIVITA_GIORNALIERE = {
    "AggiornaStatoCorso": ((0, 0), lambda: Corso().aggiornaStatoCorsi()),
    "InviaPromemoriaTurno": ((18, 0), lambda: Turno().inviaPromemoriaTurni()),
    "Backup": ((23, 30), lambda: GestoreBackup().effettuaBackup()),
}


def esegui_attivita_giornaliere() -> None:
    """Esegue ogni attivita' giornaliera una sola volta al giorno, appena passata la sua ora.
    Se il programma era chiuso all'ora prevista, l'attivita' parte alla prima occasione."""
    ora = orologio.adesso()
    dati = GestoreDati().carica()
    ultime = dati["ultima_esecuzione"]
    for nome, ((h, m), azione) in ATTIVITA_GIORNALIERE.items():
        if (ora.hour, ora.minute) >= (h, m) and ultime.get(nome) != ora.date():
            azione()
            ultime[nome] = ora.date()
            GestoreDati().salva(dati)


def main() -> None:
    app = QApplication(sys.argv)
    from supporto.stile import applica_tema
    applica_tema(app)

    # all'avvio lo stato di turni e corsi deve corrispondere a data e ora correnti
    Turno().aggiornaStatoTurni()
    Corso().aggiornaStatoCorsi()
    esegui_attivita_giornaliere()

    timer_turni = QTimer()  # AggiornaStatoTurno: ogni 15 minuti
    timer_turni.timeout.connect(lambda: Turno().aggiornaStatoTurni())
    timer_turni.start(QUINDICI_MINUTI)

    timer_giornaliero = QTimer()  # controlla ogni minuto le attivita' giornaliere
    timer_giornaliero.timeout.connect(esegui_attivita_giornaliere)
    timer_giornaliero.start(UN_MINUTO)

    vista = VistaLogin()
    vista.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
