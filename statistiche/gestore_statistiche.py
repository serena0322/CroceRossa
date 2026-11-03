"""Package Gestione: GestoreStatistiche 
Usa: GestoreDati (per avere gli elenchi), Volontario (getDati) e,
per turni e corsi, l'interfaccia Programmabile (getDati, getStato).
"""
from dati.gestore_dati import GestoreDati
from utenti.volontario import Volontario


class GestoreStatistiche:

    def __init__(self):  
        pass

    def gestisciStatistiche(self, categoria: str) -> dict:
        dati = GestoreDati().carica()
        if categoria == "volontari":
            volontari = [u for u in dati.get("utenti", {}).values() if isinstance(u, Volontario)]
            return self.__calcolaStatisticheVolontari(volontari)
        if categoria == "turni":
            return self.__calcolaStatisticheTurni(list(dati.get("turni", {}).values()))
        if categoria == "corsi":
            return self.__calcolaStatisticheCorsi(list(dati.get("corsi", {}).values()))
        return {}

    # Metodi di compatibilità con la vecchia interfaccia pubblica
    def calcolaStatisticheVolontari(self) -> dict:
        dati = GestoreDati().carica()
        volontari = [u for u in dati.get("utenti", {}).values() if isinstance(u, Volontario)]
        return self.__calcolaStatisticheVolontari(volontari)

    def calcolaStatisticheTurni(self) -> dict:
        dati = GestoreDati().carica()
        return self.__calcolaStatisticheTurni(list(dati.get("turni", {}).values()))

    def calcolaStatisticheCorsi(self) -> dict:
        dati = GestoreDati().carica()
        return self.__calcolaStatisticheCorsi(list(dati.get("corsi", {}).values()))

    def __calcolaStatisticheVolontari(self, volontari) -> dict:
        if not volontari:
            return {}  # la vista mostra il messaggio di errore
        elenco = [v.getDati() for v in volontari]
        oreTotali = sum(d["oreServizio"] for d in elenco)
        elenco.sort(key=lambda d: d["oreServizio"], reverse=True)
        return {
            "numeroVolontari": len(elenco),
            "oreServizioTotali": oreTotali,
            "mediaOreServizio": oreTotali / len(elenco),
            "classifica": [(d["nome"], d["cognome"], d["oreServizio"]) for d in elenco],
            
        }

    def __calcolaStatisticheTurni(self, turni) -> dict:
        if not turni:
            return {}
        prenotazioniTotali = 0
        percentualiConclusi = []
        for turno in turni:  # turno visto come Programmabile
            d = turno.getDati()
            prenotazioniTotali += d.get("numeroPrenotati", d.get("numeroPrenotazioni", 0))
            if turno.getStato().name == "CONCLUSO" and d["postiTotali"] > 0:
                prenotati = d.get("numeroPrenotati", d.get("numeroPrenotazioni", 0))
                percentualiConclusi.append(100 * prenotati / d["postiTotali"])
        return {
            "turniPerStato": self.__contaPerStato(turni),
            "prenotazioniTotali": prenotazioniTotali,
            "percentualeMediaPostiOccupati": self.__media(percentualiConclusi),
            
        }

    def __calcolaStatisticheCorsi(self, corsi) -> dict:
        if not corsi:
            return {}
        iscrizioniTotali = 0
        percentualiConclusi = []
        superatiPerCorso = {}
        for corso in corsi:  # corso visto come Programmabile
            d = corso.getDati()
            iscritti = d.get("numeroIscritti", d.get("numeroIscrizioni", 0))
            iscrizioniTotali += iscritti
            if corso.getStato().name == "CONCLUSO":
                if d["postiTotali"] > 0:
                    percentualiConclusi.append(100 * iscritti / d["postiTotali"])
                if iscritti > 0:
                    superati = d.get("numeroSuperati", 0)
                    superatiPerCorso[d.get("nome",d["codice"])] = 100 * superati / iscritti
        return {
            "corsiPerStato": self.__contaPerStato(corsi),
            "iscrizioniTotali": iscrizioniTotali,
            "percentualeMediaPostiOccupati": self.__media(percentualiConclusi),
            "percentualeSuperatiPerCorso": superatiPerCorso,
            
        }

    def __contaPerStato(self, elementi) -> dict:
        conteggio = {}
        for e in elementi:
            stato = e.getStato().name
            conteggio[stato] = conteggio.get(stato, 0) + 1
        return conteggio

    def __media(self, valori) -> float:
        return sum(valori) / len(valori) if valori else 0.0
