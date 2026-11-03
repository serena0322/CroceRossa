"""Package Statistiche: GestoreStatistiche (GestisciStatistiche, diagramma 7.1.5).
Usa: GestoreDati (per avere gli elenchi), Volontario (getDati) e,
per turni e corsi, SOLO l'interfaccia Programmabile (getDati, getStato).
"""
from dati.gestore_dati import GestoreDati
from utenti.volontario import Volontario


class GestoreStatistiche:
    """Realizza il caso d'uso GestisciStatistiche (7.1.5).
    Usa: GestoreDati (per avere gli elenchi), Volontario (getDati) e,
    per turni e corsi, SOLO l'interfaccia Programmabile (getDati, getStato)."""

    def __init__(self):  # create(): void
        pass

    # + gestisciStatistiche(str): dict
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

  """  # Metodi di compatibilità con la vecchia interfaccia pubblica
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
"""

    # - calcolaStatisticheVolontari(): dict
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
            # retrocompatibilità
            "oreTotali": oreTotali,
            "mediaOre": oreTotali / len(elenco),
        }

    # - calcolaStatisticheTurni(): dict
    def __calcolaStatisticheTurni(self, turni) -> dict:
        if not turni:
            return {}
        perTipo = {}
        prenotazioniTotali = 0
        percentualiConclusi = []
        for turno in turni:  # turno visto come Programmabile
            d = turno.getDati()
            perTipo[d["tipoServizio"]] = perTipo.get(d["tipoServizio"], 0) + 1
            prenotazioniTotali += d.get("numeroPrenotati", d.get("numeroPrenotazioni", 0))
            if turno.getStato().name == "CONCLUSO" and d["postiTotali"] > 0:
                prenotati = d.get("numeroPrenotati", d.get("numeroPrenotazioni", 0))
                percentualiConclusi.append(100 * prenotati / d["postiTotali"])
        return {
            "turniPerStato": self.__contaPerStato(turni),
            "turniPerTipoServizio": perTipo,
            "prenotazioniTotali": prenotazioniTotali,
            "percentualeMediaPostiOccupati": self.__media(percentualiConclusi),
            # retrocompatibilità
            "perStato": self.__contaPerStato(turni),
            "perTipo": perTipo,
            "occupazioneMediaConclusi": self.__media(percentualiConclusi),
        }

    # - calcolaStatisticheCorsi(): dict
    def __calcolaStatisticheCorsi(self, corsi) -> dict:
        if not corsi:
            return {}
        perTipo = {}
        iscrizioniTotali = 0
        percentualiConclusi = []
        superatiPerCorso = {}
        for corso in corsi:  # corso visto come Programmabile
            d = corso.getDati()
            perTipo[d["tipoCorso"]] = perTipo.get(d["tipoCorso"], 0) + 1
            iscritti = d.get("numeroIscritti", d.get("numeroIscrizioni", 0))
            iscrizioniTotali += iscritti
            if corso.getStato().name == "CONCLUSO":
                if d["postiTotali"] > 0:
                    percentualiConclusi.append(100 * iscritti / d["postiTotali"])
                if iscritti > 0:
                    superati = d.get("numeroSuperati", 0)
                    superatiPerCorso[d["codice"]] = 100 * superati / iscritti
        return {
            "corsiPerStato": self.__contaPerStato(corsi),
            "corsiPerTipo": perTipo,
            "iscrizioniTotali": iscrizioniTotali,
            "percentualeMediaPostiOccupati": self.__media(percentualiConclusi),
            "percentualeSuperatiPerCorso": superatiPerCorso,
            # retrocompatibilità
            "perStato": self.__contaPerStato(corsi),
            "perTipo": perTipo,
            "occupazioneMediaConclusi": self.__media(percentualiConclusi),
            "percentualeSuperati": {
                c.getDati().get("nome", c.getDati().get("codice")): superatiPerCorso[c.getDati()["codice"]]
                for c in corsi if c.getDati()["codice"] in superatiPerCorso
            },
        }

    # - contaPerStato(list[Programmabile]): dict
    def __contaPerStato(self, elementi) -> dict:
        conteggio = {}
        for e in elementi:
            stato = e.getStato().name
            conteggio[stato] = conteggio.get(stato, 0) + 1
        return conteggio

    def __media(self, valori) -> float:
        return sum(valori) / len(valori) if valori else 0.0

