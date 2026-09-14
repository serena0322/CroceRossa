"""
Modulo per la gestione dei controlli di sicurezza e autorizzazione di ruolo (RBAC).
"""

PIN_SICUREZZA_REFERENTE = "CRI2026"

def verifica_pin_referente(pin: str) -> bool:
    """Verifica se il PIN fornito corrisponde al codice di autorizzazione Referente CRI."""
    if not pin or not isinstance(pin, str):
        return False
    return pin.strip() == PIN_SICUREZZA_REFERENTE
