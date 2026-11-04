"""Inizializzazione completa di un dataset ricco e realistico per simulazioni e test:
- 15 codici di autorizzazione standard (CRI-REF-001 ... CRI-REF-015)
- Diversi Referenti (Emergenza, Sanitario, Formazione, Sociale)
- Oltre 10 Volontari con account realistici, patenti CRI e ordinarie (CRI 1, 2, 3, 4, 5, B, C)
- Numerosi Turni (Passati/Conclusi, Oggi, Futuri/Programmati) con diversi tipi di servizio
- Numerosi Corsi (Conclusi con attestazioni e percentuali di successo, In corso, Programmati con posti liberi)
- Prenotazioni e Iscrizioni già assegnate tra volontari e attività, ore di servizio accumulate
"""
from datetime import date, time, timedelta
from dati.gestore_dati import GestoreDati
from utenti.volontario import Volontario
from utenti.referente import Referente
from utenti.patente import Patente
from attivita.turno import Turno
from attivita.corso import Corso
from attivita.prenotazione import Prenotazione
from attivita.iscrizione import Iscrizione
from attivita.stato_attivita import StatoAttivita
from supporto import orologio


def popola_dati():
    dati = GestoreDati().carica()

    # Reset pulito delle strutture
    dati["utenti"] = {}
    dati["turni"] = {}
    dati["corsi"] = {}
    dati["prenotazioni"] = {}
    dati["iscrizioni"] = {}
    dati["patenti"] = {}
    dati["backup"] = {}

    # 1. Codici autorizzazione per Referenti (15 standard + storici)
    codici = {f"CRI-REF-{i:03d}" for i in range(1, 16)} | {"CRI2026", "REF_ANCONA", "REF_ROMA", "REF_MILANO"}
    dati["codici_autorizzazione"] = codici

    # 2. Referenti
    referenti_info = [
        ("referente@cri.it", "password123", "Emergenza", "3339876543", "Ancona", "CRI-REF-001"),
        ("referente.sanitario@cri.it", "password123", "Sanitario", "3401122334", "Ancona", "CRI-REF-002"),
        ("referente.formazione@cri.it", "password123", "Formazione", "3495566778", "Ancona", "CRI-REF-003"),
        ("referente.sociale@cri.it", "password123", "Sociale", "3489988776", "Ancona", "CRI-REF-004"),
    ]
    for email, pwd, settore, tel, com, cod in referenti_info:
        r = Referente()
        r.inserisciInformazioni(settore, email, tel, com, pwd, cod)
        dati["utenti"][email] = r

    # 3. Volontari
    volontari_info = [
        ("Mario", "Rossi", "RSSMRA80A01H501U", "mario.rossi@cri.it", "3389654324", "Ancona", "password123", [("CRI-482910", "Patente 5", date(2028, 3, 14)), ("CRI-517733", "Patente 4", date(2027, 9, 2))]),
        ("Laura", "Bianchi", "BNCLRA85B41H501K", "laura.bianchi@cri.it", "3471122334", "Ancona", "password123", [("CRI-331245", "Patente 3", date(2028, 5, 20))]),
        ("Luca", "Verdi", "VRDLCU90C15H501Y", "luca.verdi@cri.it", "3205566778", "Ancona", "password123", [("CRI-601245", "Patente 5", date(2029, 6, 18))]),
        ("Giulia", "Neri", "NRIGLI92D45H501A", "giulia.neri@cri.it", "3394455667", "Ancona", "password123", [("CRI-112233", "B", date(2029, 1, 10))]),
        ("Marco", "Ferrari", "FRRMRC88E12H501B", "marco.ferrari@cri.it", "3318899001", "Ancona", "password123", [("CRI-778899", "Patente 4", date(2027, 11, 15))]),
        ("Sara", "Esposito", "SPSSRA95F55H501C", "sara.esposito@cri.it", "3452233445", "Ancona", "password123", [("CRI-990011", "Patente 2", date(2030, 4, 12))]),
        ("Andrea", "Romano", "RMNDRA82G08H501D", "andrea.romano@cri.it", "3407788990", "Ancona", "password123", [("CRI-223344", "Patente 5", date(2028, 8, 30))]),
        ("Elena", "Galli", "GLLLNE94H62H501E", "elena.galli@cri.it", "3286677889", "Ancona", "password123", []),
        ("Davide", "Conti", "CNTDVD87L22H501F", "davide.conti@cri.it", "3331122445", "Ancona", "password123", [("CRI-556677", "CRI 5", date(2029, 10, 5))]),
        ("Chiara", "Rizzo", "RZZCHR96M50H501G", "chiara.rizzo@cri.it", "3475566112", "Ancona", "password123", [("CRI-445566", "B", date(2028, 2, 28))]),
        ("Simone", "Marini", "MRNSMN89P18H501H", "simone.marini@cri.it", "3348877665", "Ancona", "password123", [("CRI-889900", "Patente 4", date(2027, 7, 19))]),
        ("Federica", "Greco", "GRCFRC93R48H501I", "federica.greco@cri.it", "3493344556", "Ancona", "password123", [])
    ]

    volontari_creati: dict[str, Volontario] = {}
    for nome, cognome, cf, email, tel, com, pwd, patenti in volontari_info:
        v = Volontario()
        v.inserisciInformazioni(nome, cognome, cf, email, tel, com, pwd)
        dati["utenti"][email] = v
        volontari_creati[email] = v
        for cod_p, tipo_p, scad_p in patenti:
            Patente().inserisciDatiPatente(cod_p, tipo_p, scad_p, v)

    oggi = orologio.adesso().date()
    ieri = oggi - timedelta(days=1)
    domani = oggi + timedelta(days=1)

    # 4. Corsi (Conclusi, In Corso, Programmati)
    corsi_def = [
        # Conclusi
        ("C-021", "Corso Base", "Formazione d'accesso CRI", "Dott. R. Fabbri", "Base",
         oggi - timedelta(days=60), oggi - timedelta(days=45), "20:30 - 22:30", "Sede Ancona", 30, StatoAttivita.CONCLUSO),
        ("C-024", "Corso Base Soccorritori", "Modulo di base per soccorritori", "Dott. G. Verdi", "Base",
         oggi - timedelta(days=40), oggi - timedelta(days=25), "20:00 - 23:00", "Polo Didattico", 25, StatoAttivita.CONCLUSO),
        ("C-028", "BLSD", "Basic Life Support and Defibrillation", "Dott.ssa M. Neri", "Sanitario",
         oggi - timedelta(days=20), oggi - timedelta(days=5), "09:00 - 13:00", "Sede Osimo", 15, StatoAttivita.CONCLUSO),
        # In corso
        ("C-030", "Protezione Civile Operativa", "Intervento in emergenza e maxiemergenza", "Ing. A. Moretti", "Protezione Civile",
         oggi - timedelta(days=3), oggi + timedelta(days=7), "18:00 - 21:00", "Sede Ancona", 20, StatoAttivita.IN_CORSO),
        # Programmati / Disponibili
        ("C-031", "TSSA", "Trasporto sanitario e soccorso in ambulanza", "Dott. Paolo Sarti", "Sanitario",
         oggi + timedelta(days=10), oggi + timedelta(days=28), "Giovedì 20:30 - 23:00", "Sede Ancona", 20, StatoAttivita.PROGRAMMATO),
        ("C-032", "Guida Sicura Mezzi di Soccorso", "Tecniche avanzate di guida operativa", "Istr. F. Barone", "Soccorso",
         oggi + timedelta(days=15), oggi + timedelta(days=22), "Sabato 08:30 - 13:30", "Autodromo Jesi", 12, StatoAttivita.PROGRAMMATO),
        ("C-033", "PBLSD Pediatrico", "Rianimazione cardiopolmonare in età pediatrica", "Dott.ssa C. Rinaldi", "Sanitario",
         oggi + timedelta(days=20), oggi + timedelta(days=27), "Lunedì 20:30 - 23:00", "Osimo", 15, StatoAttivita.PROGRAMMATO),
        ("C-034", "Operatore Sociale", "Supporto a fasce vulnerabili ed inclusione", "Dott. E. Mariani", "Base",
         oggi + timedelta(days=25), oggi + timedelta(days=35), "Mercoledì 18:30 - 20:30", "Sede Ancona", 25, StatoAttivita.PROGRAMMATO),
    ]

    corsi_creati: dict[str, Corso] = {}
    for cod, nome, desc, dir_c, tipo, d_in, d_fi, orario, luogo, posti, stato in corsi_def:
        c = Corso()
        setattr(c, "_Corso__codice", cod)
        c.setDati(nome, desc, dir_c, tipo, d_in, d_fi, orario, luogo, posti)
        c.setPostiLiberi(posti)
        c.setStato(stato)
        dati["corsi"][cod] = c
        corsi_creati[cod] = c

    # Assegna Iscrizioni ai corsi
    # C-021 (Corso Base concluso) -> superato da quasi tutti
    iscritti_c021 = ["mario.rossi@cri.it", "laura.bianchi@cri.it", "luca.verdi@cri.it", "giulia.neri@cri.it", "marco.ferrari@cri.it", "sara.esposito@cri.it", "andrea.romano@cri.it", "davide.conti@cri.it"]
    for idx, em in enumerate(iscritti_c021):
        v = volontari_creati[em]
        isc = Iscrizione()
        setattr(isc, "_Iscrizione__codice", f"ISC-021-{idx+1:02d}")
        setattr(isc, "_Iscrizione__corso", corsi_creati["C-021"])
        setattr(isc, "_Iscrizione__volontario", v)
        setattr(isc, "_Iscrizione__dataIscrizione", corsi_creati["C-021"].getDataInizio() - timedelta(days=10))
        isc.setSuperato()
        corsi_creati["C-021"].aggiungiIscrizione(isc)
        v.aggiungiPartecipazione(isc)
        dati["iscrizioni"][f"ISC-021-{idx+1:02d}"] = isc

    # C-028 (BLSD concluso) -> attestato superato per alcuni (come da mockup: Mario Rossi e Laura Bianchi superati, Luca Verdi no)
    iscritti_c028 = ["mario.rossi@cri.it", "laura.bianchi@cri.it", "luca.verdi@cri.it"]
    for idx, em in enumerate(iscritti_c028):
        v = volontari_creati[em]
        isc = Iscrizione()
        setattr(isc, "_Iscrizione__codice", f"ISC-028-{idx+1:02d}")
        setattr(isc, "_Iscrizione__corso", corsi_creati["C-028"])
        setattr(isc, "_Iscrizione__volontario", v)
        setattr(isc, "_Iscrizione__dataIscrizione", corsi_creati["C-028"].getDataInizio() - timedelta(days=5))
        if em in ["mario.rossi@cri.it", "laura.bianchi@cri.it"]:
            isc.setSuperato()
        else:
            isc.setNonSuperato()
        corsi_creati["C-028"].aggiungiIscrizione(isc)
        v.aggiungiPartecipazione(isc)
        dati["iscrizioni"][f"ISC-028-{idx+1:02d}"] = isc

    # C-031 (TSSA programmato) -> Mario Rossi e Davide Conti già iscritti
    for idx, em in enumerate(["mario.rossi@cri.it", "davide.conti@cri.it", "andrea.romano@cri.it"]):
        v = volontari_creati[em]
        isc = Iscrizione()
        setattr(isc, "_Iscrizione__codice", f"ISC-031-{idx+1:02d}")
        setattr(isc, "_Iscrizione__corso", corsi_creati["C-031"])
        setattr(isc, "_Iscrizione__volontario", v)
        setattr(isc, "_Iscrizione__dataIscrizione", oggi - timedelta(days=2))
        corsi_creati["C-031"].aggiungiIscrizione(isc)
        v.aggiungiPartecipazione(isc)
        dati["iscrizioni"][f"ISC-031-{idx+1:02d}"] = isc

    # C-033 (BLSD programmato) -> Mario Rossi iscritto
    v_mario = volontari_creati["mario.rossi@cri.it"]
    isc_m = Iscrizione()
    setattr(isc_m, "_Iscrizione__codice", "ISC-033-01")
    setattr(isc_m, "_Iscrizione__corso", corsi_creati["C-033"])
    setattr(isc_m, "_Iscrizione__volontario", v_mario)
    setattr(isc_m, "_Iscrizione__dataIscrizione", oggi - timedelta(days=1))
    corsi_creati["C-033"].aggiungiIscrizione(isc_m)
    v_mario.aggiungiPartecipazione(isc_m)
    dati["iscrizioni"]["ISC-033-01"] = isc_m

    # 5. Turni (Passati con ore accumulate, Oggi, Futuri)
    turni_def = [
        # Turni Svolti nel passato (per accumulare carriera e statistiche)
        ("T-118", "L. Neri", ieri - timedelta(days=20), time(8, 0), time(14, 0), "Sede Ancona", "Emergenza 118", 3, "Patente 5", "TSSA", "AMB-12", "Barella, DAE", StatoAttivita.CONCLUSO),
        ("T-124", "L. Galli", ieri - timedelta(days=15), time(14, 0), time(20, 0), "Ancona", "Trasporto sanitario", 2, "Patente 3", "", "AMB-12", "Sedia a rotelle", StatoAttivita.CONCLUSO),
        ("T-165", "-", ieri - timedelta(days=5), time(8, 0), time(14, 0), "Osimo", "Assistenza manifestazioni", 4, "", "", "AMB-07", "Zaino soccorso", StatoAttivita.CONCLUSO),
        ("T-168", "G. Viola", ieri - timedelta(days=2), time(20, 0), time(23, 59), "Ospedale Regionale", "Emergenza 118", 3, "Patente 5", "BLSD", "AMB-01", "Defibrillatore, barella", StatoAttivita.CONCLUSO),
        # Turno Oggi
        ("T-170", "M. Neri", oggi, time(8, 0), time(13, 0), "Ancona", "Trasporto sanitario", 3, "Patente 5", "TSSA", "AMB-12", "Barella", StatoAttivita.PROGRAMMATO),
        ("T-171", "M. Neri, dialisi ore 9:00", domani, time(8, 0), time(14, 0), "Ancona", "Trasporto sanitario", 3, "Patente 5", "TSSA", "AMB-12", "Barella, DAE", StatoAttivita.PROGRAMMATO),
        ("T-172", "-", domani, time(14, 0), time(20, 0), "Sede CRI Ancona", "Trasporto sanitario", 3, "Patente 4", "", "PUL-04", "Sedia portantina", StatoAttivita.PROGRAMMATO),
        ("T-175", "Famiglia Marchetti", oggi + timedelta(days=3), time(8, 0), time(14, 0), "Osimo", "Sociale e spesa", 2, "B", "", "PUL-02", "Borse termiche", StatoAttivita.PROGRAMMATO),
        ("T-180", "Centrale 118", oggi + timedelta(days=4), time(20, 0), time(23, 59), "Pronto Soccorso Torrette", "Emergenza 118", 3, "Patente 5", "BLSD, TSSA", "AMB-01", "Attrezzatura rianimazione", StatoAttivita.PROGRAMMATO),
        ("T-182", "-", oggi + timedelta(days=5), time(8, 0), time(13, 0), "Stadio del Conero", "Assistenza sanitaria evento", 6, "Patente 3", "BLSD", "AMB-04", "Zaini soccorso x3", StatoAttivita.PROGRAMMATO),
        ("T-185", "Trasferimento clinica", oggi + timedelta(days=6), time(14, 0), time(18, 0), "Jesi", "Trasporto sanitario", 2, "Patente 4", "", "AMB-03", "Barella auto-caricante", StatoAttivita.PROGRAMMATO),
    ]

    turni_creati: dict[str, Turno] = {}
    for cod, paz, dt, o_i, o_f, luogo, tipo, posti, pat, corsi, mezzo, mat, stato in turni_def:
        t = Turno()
        setattr(t, "_Turno__codice", cod)
        t.setDati(paz, dt, o_i, o_f, luogo, tipo, posti, pat, corsi, mezzo, mat)
        t.setPostiLiberi(posti)
        t.setStato(stato)
        dati["turni"][cod] = t
        turni_creati[cod] = t

    # 6. Prenotazioni
    # Mario Rossi turni svolti nel passato -> T-118 (6h), T-124 (6h), T-165 (6h) per accumulare ore nella carriera
    mario_turni_passati = ["T-118", "T-124", "T-165"]
    for idx, cod in enumerate(mario_turni_passati):
        t = turni_creati[cod]
        p = Prenotazione()
        setattr(p, "_Prenotazione__codice", f"PREN-M-P{idx+1:02d}")
        setattr(p, "_Prenotazione__turno", t)
        setattr(p, "_Prenotazione__volontario", v_mario)
        setattr(p, "_Prenotazione__dataPrenotazione", t.getDati()["data"] - timedelta(days=3))
        t.aggiungiPrenotazione(p)
        v_mario.aggiungiPartecipazione(p)
        dati["prenotazioni"][f"PREN-M-P{idx+1:02d}"] = p

    # Anche Laura Bianchi e Luca Verdi partecipano a turni passati
    for idx, (em, cod) in enumerate([("laura.bianchi@cri.it", "T-118"), ("laura.bianchi@cri.it", "T-124"), ("luca.verdi@cri.it", "T-165"), ("marco.ferrari@cri.it", "T-118"), ("andrea.romano@cri.it", "T-168")]):
        v = volontari_creati[em]
        t = turni_creati[cod]
        p = Prenotazione()
        setattr(p, "_Prenotazione__codice", f"PREN-OTH-{idx+1:02d}")
        setattr(p, "_Prenotazione__turno", t)
        setattr(p, "_Prenotazione__volontario", v)
        setattr(p, "_Prenotazione__dataPrenotazione", t.getDati()["data"] - timedelta(days=2))
        t.aggiungiPrenotazione(p)
        v.aggiungiPartecipazione(p)
        dati["prenotazioni"][f"PREN-OTH-{idx+1:02d}"] = p

    # Prenotazioni future di Mario Rossi: T-170 (oggi), T-171 (domani) come da mockup
    p_fut1 = Prenotazione()
    setattr(p_fut1, "_Prenotazione__codice", "PREN-M-170")
    setattr(p_fut1, "_Prenotazione__turno", turni_creati["T-170"])
    setattr(p_fut1, "_Prenotazione__volontario", v_mario)
    setattr(p_fut1, "_Prenotazione__dataPrenotazione", oggi - timedelta(days=1))
    turni_creati["T-170"].aggiungiPrenotazione(p_fut1)
    v_mario.aggiungiPartecipazione(p_fut1)
    dati["prenotazioni"]["PREN-M-170"] = p_fut1

    # Prenotazione futura di Laura Bianchi su T-170
    v_laura = volontari_creati["laura.bianchi@cri.it"]
    p_fut2 = Prenotazione()
    setattr(p_fut2, "_Prenotazione__codice", "PREN-L-170")
    setattr(p_fut2, "_Prenotazione__turno", turni_creati["T-170"])
    setattr(p_fut2, "_Prenotazione__volontario", v_laura)
    setattr(p_fut2, "_Prenotazione__dataPrenotazione", oggi - timedelta(days=1))
    turni_creati["T-170"].aggiungiPrenotazione(p_fut2)
    v_laura.aggiungiPartecipazione(p_fut2)
    dati["prenotazioni"]["PREN-L-170"] = p_fut2

    # Prenotazione su T-172 di Luca Verdi
    v_luca = volontari_creati["luca.verdi@cri.it"]
    p_fut3 = Prenotazione()
    setattr(p_fut3, "_Prenotazione__codice", "PREN-V-172")
    setattr(p_fut3, "_Prenotazione__turno", turni_creati["T-172"])
    setattr(p_fut3, "_Prenotazione__volontario", v_luca)
    setattr(p_fut3, "_Prenotazione__dataPrenotazione", oggi)
    turni_creati["T-172"].aggiungiPrenotazione(p_fut3)
    v_luca.aggiungiPartecipazione(p_fut3)
    dati["prenotazioni"]["PREN-V-172"] = p_fut3

    # Calcolo coerente delle ore di servizio svolte sui soli turni CONCLUSI per ciascun volontario
    for v in volontari_creati.values():
        totale_ore = 0.0
        for p in getattr(v, "_Volontario__prenotazioni", []):
            t = p.getTurno()
            if t.getStato() == StatoAttivita.CONCLUSO:
                durata = (t.getDataOraFine() - t.getDataOraInizio()).total_seconds() / 3600
                totale_ore += round(durata, 2)
        setattr(v, "_Volontario__oreServizio", totale_ore)

    # Salva il dataset complessivo
    GestoreDati().salva(dati)
    print("Popolamento dataset completato con successo!")
    print(f"• Referenti registrati: {len([u for u in dati['utenti'].values() if isinstance(u, Referente)])}")
    print(f"• Volontari registrati: {len([u for u in dati['utenti'].values() if isinstance(u, Volontario)])}")
    print(f"• Turni totali: {len(dati['turni'])}")
    print(f"• Corsi totali: {len(dati['corsi'])}")
    print(f"• Prenotazioni attive: {len(dati['prenotazioni'])}")
    print(f"• Iscrizioni corsi: {len(dati['iscrizioni'])}")


if __name__ == "__main__":
    popola_dati()
