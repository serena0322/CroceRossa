"""
Modulo per l'esportazione dei turni di servizio in formato iCalendar (.ics - RFC 5545).
Permette ai volontari di importare i turni con un clic su Apple Calendar, Google Calendar e Outlook.
"""

from datetime import datetime
import uuid


def format_ics_datetime(date_str: str, time_str: str) -> str:
    """Converte 'YYYY-MM-DD' e 'HH:MM' in formato UTC iCal 'YYYYMMDDTHHMMSSZ'."""
    clean_date = date_str.strip()
    clean_time = time_str.strip()
    
    dt = None
    for d_fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            dt_base = datetime.strptime(clean_date, d_fmt)
            break
        except ValueError:
            continue
    else:
        dt_base = datetime.now()

    try:
        t_parts = clean_time.split(":")
        h = int(t_parts[0])
        m = int(t_parts[1]) if len(t_parts) > 1 else 0
        dt = dt_base.replace(hour=h, minute=m, second=0)
    except Exception:
        dt = dt_base.replace(hour=8, minute=0, second=0)

    return dt.strftime("%Y%m%dT%H%M%SZ")


def genera_file_ics(turni: list, volontario, dest_path: str) -> str:
    """
    Genera un file standard .ics contenente i turni assegnati al volontario.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Croce Rossa Italiana//Gestione Turni Volontari//IT",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Turni CRI - {volontario.get_nome_completo()}",
        "X-WR-TIMEZONE:Europe/Rome"
    ]

    now_stamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")

    for t in turni:
        # Estrazione orari da fascia_oraria (es. "08:00 - 14:00") o campi diretti
        data_turno = getattr(t, "data", "") or datetime.now().strftime("%Y-%m-%d")
        fascia = getattr(t, "fascia_oraria", "")
        ora_in = getattr(t, "oraInizio", "08:00")
        ora_out = getattr(t, "oraFine", "14:00")

        if fascia and "-" in fascia:
            parts = fascia.split("-")
            ora_in = parts[0].strip()
            ora_out = parts[1].strip()

        dt_start = format_ics_datetime(data_turno, ora_in)
        dt_end = format_ics_datetime(data_turno, ora_out)

        id_val = getattr(t, "id", None)
        if not id_val or str(id_val) == "0":
            id_val = getattr(t, "id_turno", None)
        id_t = str(id_val) if id_val else str(uuid.uuid4())[:8]
        uid = f"TURNO-{id_t}@cri.it"

        tipo_servizio = getattr(t, "tipoServizio", "Servizio CRI")
        luogo = getattr(t, "luogo", "") or getattr(t, "luogoDestinazione", "Sede Croce Rossa")
        patente = getattr(t, "patenteRichiesta", "Nessuna")

        descrizione = f"Turno di servizio CRI: {tipo_servizio}\\nLuogo: {luogo}\\nPatente richiesta: {patente}\\nID Turno: {id_t}"

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_stamp}",
            f"DTSTART:{dt_start}",
            f"DTEND:{dt_end}",
            f"SUMMARY:🚑 Turno CRI: {tipo_servizio}",
            f"DESCRIPTION:{descrizione}",
            f"LOCATION:{luogo}",
            "STATUS:CONFIRMED",
            "TRANSP:OPAQUE",
            "END:VEVENT"
        ])

    lines.append("END:VCALENDAR")
    lines.append("")

    ics_content = "\r\n".join(lines)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(ics_content)

    return dest_path
