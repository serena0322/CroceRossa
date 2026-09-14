import os
import re
import sys
import subprocess
from datetime import datetime

SWIFT_OCR_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "pdf_ocr.swift")

def estrai_testo_da_pdf(file_path: str) -> str:
    """
    Estrae il testo da un file PDF di patente:
    1. Prova prima l'estrazione diretta del testo con pypdf (veloce ed efficiente).
    2. Se il PDF non contiene testo incorporato (es. scansione immagine/fotocopia),
       utilizza il motore OCR nativo Vision di macOS (Apple Neural Engine).
    """
    if not file_path or not os.path.exists(file_path):
        return ""

    testo = ""
    # 1. Tentativo con pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                testo += t + "\n"
    except Exception as e:
        print(f"⚠️ [PDFExtractor] Errore pypdf: {e}")

    # Se abbiamo già estratto testo significativo, ritornalo
    if len(testo.strip()) >= 35:
        return testo

    # 2. Se è una scansione o immagine senza testo, usa OCR nativo Vision di macOS
    if sys.platform == "darwin":
        try:
            swift_bin = "/usr/bin/swift"
            if os.path.exists(swift_bin):
                cmd = [swift_bin, "-e", '''
import Foundation
import PDFKit
import Vision

func ocrPDF(path: String) -> String {
    guard let doc = PDFDocument(url: URL(fileURLWithPath: path)) else { return "" }
    var fullText = ""
    for i in 0..<doc.pageCount {
        guard let page = doc.page(at: i) else { continue }
        let pageRect = page.bounds(for: .mediaBox)
        let scale: CGFloat = 2.0
        let width = Int(pageRect.width * scale)
        let height = Int(pageRect.height * scale)
        let cs = CGColorSpaceCreateDeviceRGB()
        if let ctx = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8, bytesPerRow: 0, space: cs, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) {
            ctx.scaleBy(x: scale, y: scale)
            page.draw(with: .mediaBox, to: ctx)
            if let cgImage = ctx.makeImage() {
                let req = VNRecognizeTextRequest()
                req.recognitionLevel = .accurate
                req.recognitionLanguages = ["it-IT", "en-US"]
                let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
                try? handler.perform([req])
                if let results = req.results {
                    let pageText = results.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\\n")
                    fullText += pageText + "\\n"
                }
            }
        }
    }
    return fullText
}

let args = CommandLine.arguments
if args.count > 1 {
    print(ocrPDF(path: args[1]))
}
''', os.path.abspath(file_path)]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
                if res.returncode == 0 and res.stdout.strip():
                    ocr_text = res.stdout.strip()
                    if len(ocr_text) > len(testo):
                        testo = ocr_text
        except Exception as e:
            print(f"⚠️ [PDFExtractor] Errore OCR macOS: {e}")

    return testo


def _normalizza_data(data_str: str) -> str:
    """Normalizza qualsiasi formato data (gg/mm/aaaa, aaaa-mm-gg, gg.mm.aaaa) in YYYY-MM-DD."""
    if not data_str:
        return ""
    clean = re.sub(r"[^\d/\-\.]", "", data_str.strip())
    clean = clean.replace(".", "/").replace("-", "/")
    parts = [p for p in clean.split("/") if p]
    if len(parts) == 3:
        if len(parts[0]) == 4:  # YYYY/MM/DD
            return f"{parts[0]}-{int(parts[1]):02d}-{int(parts[2]):02d}"
        elif len(parts[2]) == 4:  # DD/MM/YYYY
            return f"{parts[2]}-{int(parts[1]):02d}-{int(parts[0]):02d}"
    return ""


def estrai_dati_patente_da_pdf(file_path: str) -> dict:
    """
    Analizza il documento PDF (elettronico o scansionato) ed estrapola:
    - numero_patente: Codice alfanumerico della patente (es. U1984210T, RM1234567A, ecc.)
    - data_scadenza: Data di scadenza normalizzata (YYYY-MM-DD)
    - data_rilascio: Data di emissione (YYYY-MM-DD)
    - categorie: Lista di categorie abilitate rilevate (es. ['B'])
    - cognome: Cognome del titolare se presente
    - nome: Nome del titolare se presente
    - raw_text: Testo grezzo estratto
    """
    testo = estrai_testo_da_pdf(file_path)
    
    risultato = {
        "esito": False,
        "numero_patente": "",
        "data_scadenza": "",
        "data_rilascio": "",
        "categorie": ["B"],
        "cognome": "",
        "nome": "",
        "raw_text": testo
    }

    if not testo:
        return risultato

    # --- 1. ESTRAZIONE NUMERO PATENTE ---
    # A) Standard Card UE campo 5: "5. U1234567X" o "5 U1234567X"
    m_num = re.search(r'(?:^|\n|\s)5[\.\s]+([A-Z0-9]{7,12})\b', testo, re.IGNORECASE)
    if m_num:
        risultato["numero_patente"] = m_num.group(1).upper()
    else:
        # B) Etichette esplicite: "NUMERO PATENTE: U1234567X", "PATENTE N.: U1234567X"
        m_num2 = re.search(r'(?:NUMERO\s+PATENTE|N\.\s*PATENTE|PATENTE\s*N\.?)\s*[:\-\s]+([A-Z0-9]{6,12})\b', testo, re.IGNORECASE)
        if m_num2:
            risultato["numero_patente"] = m_num2.group(1).upper()
        else:
            # C) Pattern tipici patente italiana: es. U1 + 7-8 alfanumerici, o 2 lettere + 7 cifre + 1 lettera
            m_num3 = re.search(r'\b(U1[0-9A-Z]{7,8}|[A-Z]{2}[0-9]{7}[A-Z])\b', testo)
            if m_num3:
                risultato["numero_patente"] = m_num3.group(1).upper()

    # --- 2. ESTRAZIONE DATA DI SCADENZA ---
    # A) Standard Card UE campo 4b: "4b. 22/01/2031" o "4b 22.01.2031"
    m_scad = re.search(r'(?:^|\n|\s)4b[\.\s]+(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})', testo, re.IGNORECASE)
    if m_scad:
        risultato["data_scadenza"] = _normalizza_data(m_scad.group(1))
    else:
        # B) Etichette esplicite: "SCADENZA: 2031-01-22" o "VALIDA FINO AL: 22/01/2031"
        m_scad2 = re.search(r'(?:SCADENZA|VALIDA\s+FINO\s+AL|SCAD\.?)\s*[:\-\s]+(\d{2,4}[\/\-\.]\d{2}[\/\-\.]\d{2,4})', testo, re.IGNORECASE)
        if m_scad2:
            risultato["data_scadenza"] = _normalizza_data(m_scad2.group(1))

    # --- 3. ESTRAZIONE DATA DI RILASCIO ---
    # Standard Card UE campo 4a: "4a. 25/01/2021"
    m_ril = re.search(r'(?:^|\n|\s)4a[\.\s]+(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})', testo, re.IGNORECASE)
    if m_ril:
        risultato["data_rilascio"] = _normalizza_data(m_ril.group(1))
    else:
        m_ril2 = re.search(r'(?:RILASCIO|RILASCIATA\s+IL|DATA\s+RILASCIO)\s*[:\-\s]+(\d{2,4}[\/\-\.]\d{2}[\/\-\.]\d{2,4})', testo, re.IGNORECASE)
        if m_ril2:
            risultato["data_rilascio"] = _normalizza_data(m_ril2.group(1))

    # --- 4. ESTRAZIONE CATEGORIE ABILITATE ---
    # Standard Card UE campo 9: "9. B" o "9 AM, B"
    cats = set()
    m_cat = re.search(r'(?:^|\n|\s)9[\.\s]+([A-Z0-9,\s]+)', testo)
    if m_cat:
        val_cat = m_cat.group(1).upper()
        for c in ["AM", "A1", "A2", "A", "B1", "B", "C1", "C", "D1", "D", "BE", "CE"]:
            if re.search(r'\b' + c + r'\b', val_cat):
                # Teniamo le categorie principali supportate da CRI: B, C, D, E
                if c in ["B", "C", "D", "E"]:
                    cats.add(c)
                elif "B" in c:
                    cats.add("B")
                elif "C" in c:
                    cats.add("C")

    # Ricerca generale di categorie nel testo se campo 9 non chiaro
    m_cat_gen = re.search(r'(?:CATEGORIA|CATEGORIE|ABILITAZIONI?)\s*[:\-\s]+([A-Z0-9,\s]+)', testo, re.IGNORECASE)
    if m_cat_gen:
        for c in ["B", "C", "D", "E"]:
            if re.search(r'\b' + c + r'\b', m_cat_gen.group(1).upper()):
                cats.add(c)

    # In Italia la patente autoveicoli standard è la B
    if not cats:
        cats.add("B")
    risultato["categorie"] = sorted(list(cats))

    # --- 5. ESTRAZIONE NOME E COGNOME (se presenti nei campi 1 e 2) ---
    m_cog = re.search(r'(?:^|\n)1[\.\s]+([A-ZÀ-ÿ\s]{2,25})', testo)
    if m_cog:
        risultato["cognome"] = m_cog.group(1).strip().title()

    m_nom = re.search(r'(?:^|\n)2[\.\s]+([A-ZÀ-ÿ\s]{2,25})', testo)
    if m_nom:
        risultato["nome"] = m_nom.group(1).strip().title()

    # Se abbiamo trovato almeno il numero o la scadenza o testo coerente
    if risultato["numero_patente"] or risultato["data_scadenza"] or len(testo) > 50:
        risultato["esito"] = True

    return risultato
