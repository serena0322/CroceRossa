"""Inizializzazione dei dati iniziali (codici di autorizzazione NF4, ecc.). Si lancia una volta."""
from dati.gestore_dati import GestoreDati


def main():
    dati = GestoreDati().carica()
    # NF4: codici autorizzazione per referente
    codici = {"CRI2026", "REF_ANCONA", "REF_ROMA", "REF_MILANO"}
    dati["codici_autorizzazione"].update(codici)

    from utenti.volontario import Volontario
    from utenti.referente import Referente
    from utenti.patente import Patente
    from attivita.turno import Turno
    from attivita.corso import Corso
    from attivita.prenotazione import Prenotazione
    from attivita.iscrizione import Iscrizione
    from attivita.stato_attivita import StatoAttivita
    from supporto import orologio
    from datetime import timedelta, time, date

    oggi = orologio.adesso().date()
    domani = oggi + timedelta(days=1)
    ieri = oggi - timedelta(days=1)

    # 1. Volontario demo 1 (Mario Rossi)
    if "mario.rossi@cri.it" not in dati["utenti"]:
        v1 = Volontario()
        v1.inserisciInformazioni(
            nome="Mario", cognome="Rossi", codiceFiscale="RSSMRA80A01H501U",
            email="mario.rossi@cri.it", telefono="3331234567",
            comitato="Comitato di Ancona", password="password123"
        )
        # Patente valida per Mario
        Patente().inserisciDatiPatente("PAT_MR_01", "CRI 5", oggi + timedelta(days=365*3), v1)

    # Volontario demo 2 (Anna Bianchi)
    if "anna.bianchi@cri.it" not in dati["utenti"]:
        v2 = Volontario()
        v2.inserisciInformazioni(
            nome="Anna", cognome="Bianchi", codiceFiscale="BNCNNA85B41H501K",
            email="anna.bianchi@cri.it", telefono="3479876543",
            comitato="Comitato di Ancona", password="password123"
        )
        Patente().inserisciDatiPatente("PAT_AB_01", "B", oggi + timedelta(days=365*2), v2)

    # 2. Referente demo
    if "referente@cri.it" not in dati["utenti"]:
        r = Referente()
        r.inserisciInformazioni(
            settoreGestito="Emergenza", email="referente@cri.it",
            telefono="3339876543", comitato="Comitato di Ancona",
            password="password123", codiceAutorizzazione="CRI2026"
        )

    # 3. Turni di prova (oggi futuro e domani)
    if "T_OGGI_1" not in dati["turni"]:
        t_oggi = Turno()
        t_oggi.inserisciDatiTurno(
            codice="T_OGGI_1", datiPaziente="", data=oggi,
            oraInizio=time(22, 0), oraFine=time(23, 59), luogo="Ospedale Regionale",
            tipoServizio="Emergenza 118", postiTotali=3, patenteRichiesta="CRI 5",
            corsiRichiesti="BLSD", mezzo="Ambulanza CRI-01", materialeNecessario="Defibrillatore, barella"
        )

    if "T_DOMANI_1" not in dati["turni"]:
        t_domani = Turno()
        t_domani.inserisciDatiTurno(
            codice="T_DOMANI_1", datiPaziente="", data=domani,
            oraInizio=time(14, 0), oraFine=time(20, 0), luogo="Sede CRI Ancona",
            tipoServizio="Trasporto infermi", postiTotali=2, patenteRichiesta="",
            corsiRichiesti="", mezzo="Pulmino CRI-04", materialeNecessario="Sedia a rotelle"
        )

    # 4. Corsi: uno programmato e uno concluso da attestare
    if "C_PROGRAMMATO_1" not in dati["corsi"]:
        c_prog = Corso()
        c_prog.inserisciDatiCorso(
            codice="C_PROGRAMMATO_1", nome="Primo Soccorso Base",
            descrizione="Nozioni fondamentali di primo soccorso e manovre salvavita",
            direttoreCorso="Dott. G. Verdi", tipoCorso="Base",
            dataInizio=oggi + timedelta(days=5), dataFine=oggi + timedelta(days=12),
            orario="20:30 - 22:30", luogo="Aula Magna CRI", postiTotali=25
        )

    if "C_CONCLUSO_1" not in dati["corsi"]:
        c_conc = Corso()
        setattr(c_conc, "_Corso__codice", "C_CONCLUSO_1")
        c_conc.setDati(
            nome="BLSD ed uso Defibrillatore",
            descrizione="Basic Life Support and Defibrillation",
            direttoreCorso="Dott.ssa M. Neri", tipoCorso="Sanitario",
            dataInizio=ieri - timedelta(days=7), dataFine=ieri,
            orario="09:00 - 13:00", luogo="Polo Didattico CRI", postiTotali=15
        )
        c_conc.setStato(StatoAttivita.CONCLUSO)
        dati["corsi"]["C_CONCLUSO_1"] = c_conc
        # Iscrivi volontario demo per poter attestare la partecipazione
        v_mario = dati["utenti"].get("mario.rossi@cri.it")
        v_anna = dati["utenti"].get("anna.bianchi@cri.it")
        if v_mario:
            i1 = Iscrizione()
            setattr(i1, "_Iscrizione__codice", "ISCR_DEMO_1")
            setattr(i1, "_Iscrizione__corso", c_conc)
            setattr(i1, "_Iscrizione__volontario", v_mario)
            c_conc.aggiungiIscrizione(i1)
            v_mario.aggiungiPartecipazione(i1)
            dati["iscrizioni"]["ISCR_DEMO_1"] = i1
        if v_anna:
            i2 = Iscrizione()
            setattr(i2, "_Iscrizione__codice", "ISCR_DEMO_2")
            setattr(i2, "_Iscrizione__corso", c_conc)
            setattr(i2, "_Iscrizione__volontario", v_anna)
            c_conc.aggiungiIscrizione(i2)
            v_anna.aggiungiPartecipazione(i2)
            dati["iscrizioni"]["ISCR_DEMO_2"] = i2

    GestoreDati().salva(dati)
    print("Dati inizializzati con successo in dati/dati.pickle.")
    print(f"Codici di autorizzazione attivi: {dati['codici_autorizzazione']}")
    print("Dataset demo pronto:")
    print("  • Volontario 1: mario.rossi@cri.it   / password123 (con Patente CRI 5)")
    print("  • Volontario 2: anna.bianchi@cri.it  / password123 (con Patente B)")
    print("  • Referente:    referente@cri.it     / password123 (Settore Emergenza)")
    print("  • Turni: T_OGGI_1 (oggi), T_DOMANI_1 (domani)")
    print("  • Corsi: C_PROGRAMMATO_1 (aperto), C_CONCLUSO_1 (concluso, pronto per attestazione)")


if __name__ == "__main__":
    main()
