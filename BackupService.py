from __future__ import annotations
import os
import json
from datetime import datetime
import threading
import time
from typing import TYPE_CHECKING, Tuple, Optional

if TYPE_CHECKING:
    from Sistema import Sistema

class BackupService:
    """
    Servizio di Backup Automatico e Periodico (RF23).
    Permette l'esportazione e la rotazione dei backup dell'intero stato del sistema CRI.
    """
    _thread_periodico: Optional[threading.Thread] = None
    _in_esecuzione: bool = False

    def __init__(self, backup_dir: str = "backups", max_backups: int = 15):
        self.backup_dir = backup_dir
        self.max_backups = max_backups

    def crea_backup(self, sistema: Sistema) -> Tuple[bool, str]:
        """Esegue il backup usando la directory configurata nell'istanza."""
        return self.esegui_backup(sistema, base_dir=self.backup_dir)

    @staticmethod
    def get_backup_dir(base_dir: str = "backups") -> str:
        """Restituisce il percorso assoluto della cartella dei backup."""
        if not os.path.isabs(base_dir):
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), base_dir)
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    @classmethod
    def esegui_backup(cls, sistema: Sistema, base_dir: str = "backups") -> Tuple[bool, str]:
        """
        Esegue un backup completo dei dati del sistema (Utenti, Turni, Mezzi, Corsi)
        salvandoli in un file JSON timestampato con rotazione automatica.
        """
        try:
            cartella = cls.get_backup_dir(base_dir)
            ora_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_file = f"backup_cri_{ora_str}.json"
            percorso_completo = os.path.join(cartella, nome_file)

            payload = {
                "versione": "1.0",
                "data_backup": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "conteggio": {
                    "utenti": len(sistema.volontari),
                    "turni": len(sistema.turni),
                    "mezzi": len(sistema.mezzi),
                    "corsi": len(sistema.corsi)
                },
                "utenti": [v.to_dict() for v in getattr(sistema, "volontari", []) if hasattr(v, "to_dict")],
                "mezzi": [
                    {
                        "targa": m.targa,
                        "tipo": m.tipo,
                        "chilometraggioTotale": m.chilometraggioTotale,
                        "stato": m.stato,
                        "dataScadenzaAssicurazione": getattr(m, "dataScadenzaAssicurazione", ""),
                        "disponibile": getattr(m, "disponibile", True)
                    }
                    for m in getattr(sistema, "mezzi", [])
                ],
                "corsi": [
                    {
                        "id": c.id,
                        "titolo": c.titolo,
                        "nome": c.nome,
                        "dataInizio": c.dataInizio,
                        "dataFine": c.dataFine,
                        "mesiValidita": c.mesiValidita,
                        "qualificaRilasciata": c.qualificaRilasciata,
                        "stato": c.stato,
                        "direttore": getattr(c, "direttore", ""),
                        "luogo": getattr(c, "luogo", ""),
                        "orari": getattr(c, "orari", ""),
                        "requisitiIscrizione": getattr(c, "requisitiIscrizione", ""),
                        "maxPartecipanti": getattr(c, "maxPartecipanti", 20),
                        "partecipanti_ids": [str(p.cod_fiscale) for p in getattr(c, "partecipanti", [])]
                    }
                    for c in getattr(sistema, "corsi", [])
                ],
                "turni": [
                    {
                        "id": getattr(t, "codice", getattr(t, "id", "")),
                        "codice": getattr(t, "codice", getattr(t, "id", "")),
                        "data": t.data,
                        "luogoPrelevamento": getattr(t, "luogoPrelevamento", ""),
                        "luogoDestinazione": getattr(t, "luogoDestinazione", ""),
                        "oraInizio": t.oraInizio,
                        "oraFine": t.oraFine,
                        "patenteRichiesta": t.patenteRichiesta,
                        "paziente": getattr(t, "paziente", ""),
                        "paziente_nome": getattr(t, "paziente_nome", ""),
                        "paziente_cognome": getattr(t, "paziente_cognome", ""),
                        "paziente_cf": getattr(t, "paziente_cf", ""),
                        "personeRichieste": t.personeRichieste,
                        "stato": t.stato,
                        "tipoServizio": t.tipoServizio,
                        "mezzo_targa": getattr(t, "mezzo_targa", ""),
                        "volontari_ids": [str(v.cod_fiscale) for v in getattr(t, "volontari_assegnati", [])]
                    }
                    for t in getattr(sistema, "turni", [])
                ]
            }

            with open(percorso_completo, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

            cls._ruota_backup(cartella, max_file=15)
            print(f"[BackupService] Backup completato con successo: {nome_file}")
            return True, percorso_completo

        except Exception as e:
            print(f"[BackupService/Errore] Durante l'esecuzione del backup: {e}")
            return False, str(e)

    @classmethod
    def _ruota_backup(cls, cartella: str, max_file: int = 15):
        """
        Politica di retention FIFO (First-In, First-Out):
        Mantiene un massimo di N file di backup (default 15).
        Ordina i file esistenti per timestamp di ultima modifica (os.path.getmtime)
        ed elimina progressivamente le snapshot più obsolete per prevenire l'esaurimento
        dello storage su disco.
        """
        try:
            files = [
                os.path.join(cartella, f)
                for f in os.listdir(cartella)
                if f.startswith("backup_cri_") and f.endswith(".json")
            ]
            if len(files) > max_file:
                files.sort(key=os.path.getmtime)
                for vecchio in files[:-max_file]:
                    try:
                        os.remove(vecchio)
                    except OSError:
                        pass
        except Exception:
            pass

    @classmethod
    def avvia_backup_automatico_daemon(cls, sistema: Sistema, intervallo_secondi: int = 3600):
        """
        Avvia un thread demone (daemon=True) in background (RF23) per il backup periodico.
        Operando su un thread separato dal Main GUI Thread di PyQt5, assicura che il dump
        dello stato del sistema e la scrittura su disco avvengano senza generare lag o
        freeze dell'interfaccia utente.
        """
        if cls._in_esecuzione:
            return

        cls._in_esecuzione = True

        def _loop():
            while cls._in_esecuzione:
                time.sleep(intervallo_secondi)
                if cls._in_esecuzione and sistema:
                    cls.esegui_backup(sistema)

        cls._thread_periodico = threading.Thread(target=_loop, daemon=True, name="BackupServiceThread")
        cls._thread_periodico.start()
        print(f"[BackupService] Backup automatico periodico avviato (intervallo: {intervallo_secondi}s).")

    @classmethod
    def ferma_backup_automatico(cls):
        """Arresta in modo pulito il ciclo di esecuzione del thread demone."""
        cls._in_esecuzione = False
