"""Modulo di supporto: l'unico punto in cui il sistema legge l'ora corrente.
Tutte le classi chiamano orologio.adesso() invece di datetime.now():
nei test basta sostituire questa funzione per "spostare" il tempo.
"""
from datetime import datetime

def adesso() -> datetime:
    return datetime.now()
