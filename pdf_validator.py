import os

def valida_pdf_patente(file_path: str) -> tuple[bool, str]:
    """
    Esegue una verifica di sicurezza approfondita su un file PDF di patente:
    1. Verifica dell'esistenza e leggibilità del file.
    2. Controllo dell'estensione (.pdf).
    3. Controllo della dimensione (non vuoto, min. 500 byte, max 15 MB).
    4. Controllo della firma binaria (Magic Number %PDF- nei primi byte).
    5. Controllo di integrità (presenza del marcatore %%EOF negli ultimi byte).
    6. Controllo della struttura (presenza di oggetti PDF).

    Ritorna:
        (True, "OK") se il documento è integro e conforme.
        (False, messaggio_errore) se il file non supera i requisiti di sicurezza.
    """
    if not file_path or not isinstance(file_path, str):
        return False, "Nessun percorso file specificato."

    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        return False, f"Il file specificato non esiste:\n{abs_path}"

    if not os.path.isfile(abs_path):
        return False, "Il percorso specificato non corrisponde a un file valido."

    # Controllo estensione
    _, ext = os.path.splitext(abs_path)
    if ext.lower() != ".pdf":
        return False, f"Formato non consentito: l'estensione deve essere '.pdf' (rilevato '{ext}')."

    # Controllo dimensione file
    try:
        size = os.path.getsize(abs_path)
    except Exception as e:
        return False, f"Impossibile leggere la dimensione del file: {e}"

    if size == 0:
        return False, "Il file è vuoto (0 byte). Allega un documento scansionato o digitale valido."

    if size < 500:
        return False, f"Il file è troppo piccolo ({size} byte) per essere un PDF valido. Minimo richiesto: 500 byte."

    max_size = 15 * 1024 * 1024  # 15 MB
    if size > max_size:
        return False, f"Il file supera la dimensione massima consentita di 15 MB (rilevati {size / (1024*1024):.1f} MB)."

    # Controllo contenuto binario
    try:
        with open(abs_path, "rb") as f:
            header = f.read(1024)

            # Il file deve iniziare con il magic number PDF (es. %PDF-1.x o %PDF-2.x)
            if b"%PDF-" not in header:
                return False, "File non valido: intestazione binaria '%PDF-' mancante o non riconosciuta. Non è un vero documento PDF."

            # Posizionati alla fine per verificare il marcatore di chiusura
            f.seek(max(0, size - 2048), os.SEEK_SET)
            tail = f.read(2048)

            # Verifica chiusura standard PDF (%%EOF)
            if b"%%EOF" not in tail:
                return False, "File corrotto o incompleto: marcatore di chiusura '%%EOF' non trovato. Il file potrebbe essere stato scaricato o salvato solo parzialmente."

            # Verifica presenza minima di oggetti PDF
            f.seek(0)
            full_chunk = f.read(min(size, 65536))
            if b"obj" not in full_chunk:
                return False, "Struttura PDF non conforme: nessun oggetto dati valido individuato nel documento."

    except PermissionError:
        return False, "Permessi insufficienti per leggere il file specificato."
    except Exception as e:
        return False, f"Errore durante la lettura e verifica del documento: {e}"

    return True, "Documento PDF integro e valido."
