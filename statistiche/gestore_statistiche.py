"""Package Statistiche: GestoreStatistiche (GestisciStatistiche).
Turni e corsi vengono contati attraverso l'interfaccia Programmabile (getStato, getDati):
lo stesso codice funziona per entrambi.
"""
from attivita.programmabile import Programmabile
from attivita.stato_attivita import StatoAttivita
from dati.gestore_dati import GestoreDati
from utenti.volontario import Volontario

class GestoreStatistiche:
    def __init__(self):  # create(): void
        pass

    def gestisciStatistiche(self, categoria: str) -> dict:
        """categoria: "volontari", "turni", "corsi". {} = nessun dato (messaggio di errore)."""
        if categoria == "volontari":
            return self.calcolaStatisticheVolontari()
        if categoria == "turni":
            return self.calcolaStatisticheTurni()
        if categoria == "corsi":
            return self.calcolaStatisticheCorsi()
        return {}

    def calcolaStatisticheVolontari(self) -> dict:
        volontari = [u for u in GestoreDati().carica()["utenti"].values()
                     if isinstance(u, Volontario)]
        if not volontari:
            return {}
        ore = [v.getDati()["oreServizio"] for v in volontari]
        classifica = sorted(volontari, key=lambda v: v.getDati()["oreServizio"], reverse=True)
        return {
            "numeroVolontari": len(volontari),
            "oreTotali": sum(ore),
            "mediaOre": sum(ore) / len(volontari),
            "classifica": [(v.getDati()["nome"], v.getDati()["cognome"],
                            v.getDati()["oreServizio"]) for v in classifica]
        }

    def calcolaStatisticheTurni(self) -> dict:
        dati = GestoreDati().carica()
        turni = list(dati["turni"].values())
        if not turni:
            return {}
        risultato = self.__contaPerStatoETipo(turni, "tipoServizio")
        risultato["prenotazioniTotali"] = sum(t.getDati().get("numeroPrenotazioni", 0) for t in turni)
        risultato["occupazioneMediaConclusi"] = self.__occupazioneMedia(turni)
        return risultato

    def calcolaStatisticheCorsi(self) -> dict:
        dati = GestoreDati().carica()
        corsi = list(dati["corsi"].values())
        if not corsi:
            return {}
        risultato = self.__contaPerStatoETipo(corsi, "tipoCorso")
        risultato["iscrizioniTotali"] = sum(c.getDati().get("numeroIscrizioni", 0) for c in corsi)
        risultato["occupazioneMediaConclusi"] = self.__occupazioneMedia(corsi)
        risultato["percentualeSuperati"] = {
            c.getDati()["nome"]: (100.0 * c.getDati()["numeroSuperati"] / c.getDati()["numeroIscrizioni"])
            for c in corsi if c.getStato() == StatoAttivita.CONCLUSO and c.getDati().get("numeroIscrizioni", 0) > 0
        }
        return risultato

    # ---------- polimorfismo tramite l'interfaccia Programmabile ----------
    def __contaPerStatoETipo(self, attivita: list[Programmabile], chiaveTipo: str) -> dict:
        perStato = {stato.value: 0 for stato in StatoAttivita}
        perTipo: dict[str, int] = {}
        for a in attivita:
            perStato[a.getStato().value] += 1
            tipo = a.getDati()[chiaveTipo]
            perTipo[tipo] = perTipo.get(tipo, 0) + 1
        return {"perStato": perStato, "perTipo": perTipo}

    def __occupazioneMedia(self, attivita: list[Programmabile]) -> float:
        concluse = [a.getDati() for a in attivita if a.getStato() == StatoAttivita.CONCLUSO]
        if not concluse:
            return 0.0
        return sum(100 * (d["postiTotali"] - d["postiLiberi"]) / d["postiTotali"]
                   for d in concluse) / len(concluse)
