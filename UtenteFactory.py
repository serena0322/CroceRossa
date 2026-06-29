

def costruisci_utente(data: dict):
    from Volontario import Volontario
    from Referente import Referente
    from OperatoreSanitario import OperatoreSanitario
    ruolo = data.get("ruolo")

    if ruolo == "volontario":
        u = Volontario(
            cod_fiscale=data["cod_fiscale"],
            nome=data["nome"],
            cognome=data.get("cognome", ""),
            email=data["email"],
            nascita=data.get("nascita", ""),
            telefono=data.get("telefono", ""),
            curriculum=data.get("curriculum", ""),
            patenti=data.get("patenti", []),
            qualifiche=data.get("qualifiche", []),
            monteOreTotale=data.get("monteOreTotale", 0),
            formazione=[],
            compagnia_appartenenza=data.get("compagnia_appartenenza", ""),
            disponibilita=data.get("disponibilita", [])
        )
        u.patente_pdf_path = data.get("patente_pdf_path", "")
        return u
    elif ruolo == "referente":
        r = Referente(
            cod_fiscale=data["cod_fiscale"],
            nome=data["nome"],
            cognome=data.get("cognome", ""),
            email=data["email"],
            nascita=data.get("nascita", ""),
            telefono=data.get("telefono", ""),
            curriculum=data.get("curriculum", ""),
            patenti=data.get("patenti", []),
            qualifiche=data.get("qualifiche", []),
            monteOreTotale=data.get("monteOreTotale", 0),
            formazione=[],
            compagnia_appartenenza=data.get("compagnia_appartenenza", ""),
            disponibilita=data.get("disponibilita", []),
            area_gestita=data.get("area_gestita", "")
        )
        r.patente_pdf_path = data.get("patente_pdf_path", "")
        return r
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
