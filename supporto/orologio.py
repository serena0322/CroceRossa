"""unico punto in cui il sistema legge l'ora corrente.Tutte le classi chiamano orologio.adesso()"""
from datetime import datetime

def adesso() -> datetime:
    return datetime.now()
