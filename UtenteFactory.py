from __future__ import annotations

def costruisci_utente(data: dict):
    from Volontario import Volontario
    from Referente import Referente
    ruolo_raw = str(data.get("ruolo") or "volontario").strip().lower()
    ruolo = ruolo_raw.replace(" ", "_")

    if ruolo == "volontario" or ruolo in ["operatore_sanitario", "operatore", "sanitario"]:
        u = Volontario(
            cod_fiscale=data["cod_fiscale"],
            nome=data["nome"],
            cognome=data.get("cognome", ""),
            email=data["email"],
            nascita=data.get("data_nascita", data.get("nascita", "")),
            telefono=data.get("telefono", ""),
            curriculum=data.get("curriculum", ""),
            patenti=data.get("patenti", []),
            qualifiche=data.get("qualifiche", []),
            oreServizio=data.get("oreServizio", data.get("monteOreTotale", 0)),
            formazione=[],
            comitato_appartenenza=data.get("comitato_appartenenza", data.get("compagnia_appartenenza", "")),
            numero_patente=data.get("numero_patente", ""),
            data_rilascio_patente=data.get("data_rilascio_patente", data.get("data_rilascio", "")),
            scadenza_patente=data.get("scadenza_patente", "")
        )
        return u
    elif ruolo == "referente":
        r = Referente(
            cod_fiscale=data["cod_fiscale"],
            nome=data["nome"],
            cognome=data.get("cognome", ""),
            email=data["email"],
            nascita=data.get("data_nascita", data.get("nascita", "")),
            telefono=data.get("telefono", ""),
            curriculum=data.get("curriculum", ""),
            patenti=data.get("patenti", []),
            qualifiche=data.get("qualifiche", []),
            oreServizio=data.get("oreServizio", data.get("monteOreTotale", 0)),
            formazione=[],
            comitato_appartenenza=data.get("comitato_appartenenza", data.get("compagnia_appartenenza", "")),
            settoreGestito=data.get("settoreGestito", data.get("area_gestita", "")),
            codiceAutorizzazione=data.get("codiceAutorizzazione", data.get("codice_autorizzazione", "")),
            numero_patente=data.get("numero_patente", ""),
            data_rilascio_patente=data.get("data_rilascio_patente", data.get("data_rilascio", "")),
            scadenza_patente=data.get("scadenza_patente", "")
        )
        return r
    else:
        raise ValueError(f"Ruolo sconosciuto: {ruolo}")
