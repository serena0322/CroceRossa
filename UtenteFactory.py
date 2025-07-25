

def costruisci_utente(data: dict):
    from Volontario import Volontario
    from Referente import Referente
    from OperatoreSanitario import OperatoreSanitario
    ruolo = data.get("ruolo")

    if ruolo == "volontario":
        return Volontario(
            cod_fiscale=data["cod_fiscale"],
            nome=data["nome"],
            cognome=data.get("cognome", ""),
            email=data["email"],
            nascita=data.get("nascita", ""),
            telefono=data.get("telefono", ""),
            curriculum=data.get("curriculum", ""),
            patenti=data.get("patenti", []),
            formazione=data.get("formazione", []),
            compagnia_appartenenza=data.get("compagnia_appartenenza", ""),
            disponibilita=data.get("disponibilita", [])
        )
    elif ruolo == "referente":
        return Referente(
            cod_fiscale=data["cod_fiscale"],
            nome=data["nome"],
            cognome=data.get("cognome", ""),
            email=data["email"],
            nascita=data.get("nascita", ""),
            telefono=data.get("telefono", ""),
            curriculum=data.get("curriculum", ""),
            patenti=data.get("patenti", []),
            formazione=data.get("formazione", []),
            compagnia_appartenenza=data.get("compagnia_appartenenza", ""),
            disponibilita=data.get("disponibilita", []),
            area_gestita=data.get("area_gestita", "")
        )
    elif ruolo == "operatore sanitario":
        return OperatoreSanitario(
            cod_fiscale=data["cod_fiscale"],
            nome=data["nome"],
            cognome=data.get("cognome", ""),
            email=data["email"],
            nascita=data.get("nascita", ""),
            telefono=data.get("telefono", ""),
            specializzazioni=data.get("specializzazioni", []),
            disponibilita=data.get("disponibilita", [])
        )
    else:
        raise ValueError(f"Ruolo sconosciuto: {ruolo}")
