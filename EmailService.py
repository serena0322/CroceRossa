import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class EmailService:
    # Registro in memoria delle email inviate (utile per verifica e audit)
    sent_emails = []

    @staticmethod
    def inviaMail(destinatario: str, messaggio: str, oggetto: str = "Comunicazione Croce Rossa Italiana") -> bool:
        """
        Invia un'email al destinatario specificato.
        Se le credenziali SMTP sono definite nelle variabili d'ambiente, effettua l'invio reale.
        Altrimenti registra l'invio nello storico controllato dell'applicazione.
        """
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "destinatario": destinatario,
            "oggetto": oggetto,
            "messaggio": messaggio,
            "inviata_realmente": False
        }

        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")

        if smtp_host and smtp_user and smtp_pass:
            try:
                msg = MIMEText(messaggio, "plain", "utf-8")
                msg["Subject"] = oggetto
                msg["From"] = smtp_user
                msg["To"] = destinatario

                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)

                record["inviata_realmente"] = True
                print(f"📧 [EmailService] Email inviata con successo a {destinatario}")
            except Exception as e:
                print(f"⚠️ [EmailService] Errore invio SMTP a {destinatario}: {e}")
                record["errore"] = str(e)
        else:
            # Modalità simulazione / test
            print(f"📧 [EmailService] (Simulazione) Inviata a {destinatario} | Oggetto: {oggetto} | Testo: {messaggio[:60]}...")

        EmailService.sent_emails.append(record)
        return True

    @staticmethod
    def get_sent_emails() -> list:
        return list(EmailService.sent_emails)

    @staticmethod
    def clear_history():
        EmailService.sent_emails.clear()
