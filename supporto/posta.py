"""Modulo di supporto per le e-mail (classe di supporto, non di dominio).
MODALITA = "simulata": le e-mail vengono scritte in dati/email_inviate.log
MODALITA = "smtp": le e-mail vengono inviate davvero con smtplib
(la scelta dipende dalla risposta del prof: e-mail simulate o reali?)
"""
import os
import smtplib
from email.message import EmailMessage
from supporto import orologio

MODALITA = "simulata"
PERCORSO_LOG = os.path.join("dati", "email_inviate.log")
SMTP_SERVER = "smtp.esempio.it"  
SMTP_PORTA = 587
SMTP_UTENTE = ""
SMTP_PASSWORD = ""

def invia(destinatario: str, oggetto: str, testo: str) -> None:
    if MODALITA == "smtp":
        messaggio = EmailMessage()
        messaggio["From"] = SMTP_UTENTE
        messaggio["To"] = destinatario
        messaggio["Subject"] = oggetto
        messaggio.set_content(testo)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORTA) as server:
            server.starttls()
            server.login(SMTP_UTENTE, SMTP_PASSWORD)
            server.send_message(messaggio)
    else:
        os.makedirs(os.path.dirname(PERCORSO_LOG), exist_ok=True)
        with open(PERCORSO_LOG, "a", encoding="utf-8") as log:
            log.write(f"[{orologio.adesso():%d/%m/%Y %H:%M}] A: {destinatario} | "
                      f"{oggetto} | {testo}\n")
