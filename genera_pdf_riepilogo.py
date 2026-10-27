import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

def build_pdf(filename="Riepilogo_Revisione_CroceRossa.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_red = colors.HexColor("#C8102E")      # CRI Red
    dark_gray = colors.HexColor("#222222")
    light_bg = colors.HexColor("#F8F9FA")
    border_color = colors.HexColor("#E5E7EB")
    alt_bg = colors.HexColor("#F1F5F9")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_red,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#555555"),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=primary_red,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=dark_gray
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    tbl_header = ParagraphStyle(
        'TblHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    tbl_cell = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=dark_gray
    )

    tbl_cell_bold = ParagraphStyle(
        'TblCellBold',
        parent=tbl_cell,
        fontName='Helvetica-Bold'
    )

    story = []

    # Title & Header
    story.append(Paragraph("SISTEMA GESTIONALE CROCE ROSSA ITALIANA", title_style))
    story.append(Paragraph("Guida Rapida alla Struttura del Progetto & Checklist per la Revisione", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_red, spaceBefore=0, spaceAfter=10))

    # Section 1: Overview
    story.append(Paragraph("1. Panoramica del Progetto", h1_style))
    story.append(Paragraph(
        "Applicazione desktop completa per la gestione operativa di una sezione della Croce Rossa. "
        "Consente la gestione integrata di <b>turni</b>, <b>parco mezzi</b>, <b>formazione</b>, "
        "<b>checklist sanitarie/tecniche</b> e <b>anagrafica volontari/referenti</b>.<br/>"
        "• <b>Linguaggio & Framework</b>: Python 3 con GUI in PyQt5.<br/>"
        "• <b>Archiviazione & Persistenza</b>: File locale <code>database.json</code> con rotazione automatica copie di sicurezza in <code>backups/</code>.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Section 2: Architettura Software
    story.append(Paragraph("2. Architettura del Software (Pattern MVC-like)", h1_style))
    story.append(Paragraph(
        "L'applicazione adotta una netta separazione delle responsabilità per garantire modularità, manutenibilità ed estendibilità:",
        body_style
    ))
    story.append(Spacer(1, 4))

    arch_data = [
        [
            Paragraph("Livello", tbl_header),
            Paragraph("Componenti Chiave", tbl_header),
            Paragraph("Ruolo e Responsabilità", tbl_header)
        ],
        [
            Paragraph("<b>Presentation (UI)</b><br/>(Cartella <code>layout/</code>)", tbl_cell),
            Paragraph("• <code>MainWindow.py</code><br/>• <code>LoginWindow.py</code><br/>• Dialogs operativi", tbl_cell),
            Paragraph("Interfaccia utente grafica in PyQt5. Raccoglie gli input, valida i campi grafici e delega la logica al controller/facade.", tbl_cell)
        ],
        [
            Paragraph("<b>Controller (Business Logic)</b>", tbl_cell),
            Paragraph("• <code>GestioneTurniController</code><br/>• <code>GestioneFlottaController</code><br/>• <code>GestioneFormazioneController</code><br/>• <code>GestioneUtenteController</code>", tbl_cell),
            Paragraph("Incapsulano le regole di business settoriali. Separano i compiti evitando classi monolitiche (principio di singola responsabilità).", tbl_cell)
        ],
        [
            Paragraph("<b>Facade / Coordinator</b>", tbl_cell),
            Paragraph("• <code>Sistema.py</code>", tbl_cell),
            Paragraph("Punto d'accesso centrale unificato. Gestisce lo stato globale della sessione, il caricamento/salvataggio del database JSON e il routing.", tbl_cell)
        ],
        [
            Paragraph("<b>Domain Model</b>", tbl_cell),
            Paragraph("• <code>Utente</code>, <code>Volontario</code>, <code>Referente</code><br/>• <code>Turno</code>, <code>Mezzo</code>, <code>Corso</code><br/>• <code>Checklist</code>, <code>Patente</code>, <code>Report</code>", tbl_cell),
            Paragraph("Entità con stato e metodi di dominio (es. calcolo ore, validazione patenti per i mezzi, iscrizioni e certificazioni).", tbl_cell)
        ],
        [
            Paragraph("<b>Services & Utils</b>", tbl_cell),
            Paragraph("• <code>BackupService.py</code><br/>• <code>EmailService.py</code><br/>• <code>auth.py</code>, <code>session_manager.py</code>", tbl_cell),
            Paragraph("Servizi di supporto trasversali: gestione backup, notifiche email, hashing sicuro password e persistenza token di sessione.", tbl_cell)
        ]
    ]

    t_arch = Table(arch_data, colWidths=[3.2*cm, 5.2*cm, 8.8*cm])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_red),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, alt_bg])
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # Section 3: Design Pattern
    story.append(Paragraph("3. Design Pattern Implementati (Cosa dire all'Assistente)", h1_style))
    patterns = [
        "<b>Factory Method (<code>UtenteFactory.py</code>)</b>: Decoupling della creazione utenti. Data la configurazione dal JSON o dalla registrazione, restituisce l'istanza corretta (<code>Volontario</code> o <code>Referente</code>) senza vincolare il client alle classi concrete.",
        "<b>Facade Pattern (<code>Sistema.py</code>)</b>: Maschera la complessità dei 4 controller interni fornendo un'API univoca e centralizzata sia all'avvio sia all'interfaccia grafica.",
        "<b>Controller Pattern / Separation of Concerns</b>: La logica applicativa è compartimentata per ambito tematico (Flotta, Turni, Formazione, Utente) anziché gravare su un God Object.",
        "<b>Service Layer</b>: Servizi modulari a sé stanti (<code>EmailService</code> per notifiche e <code>BackupService</code> per sicurezza dati), facilmente sostituibili o estendibili."
    ]
    for p in patterns:
        story.append(Paragraph(f"• {p}", bullet_style))
    story.append(Spacer(1, 8))

    # Section 4: Domande e Risposte Chiave
    story.append(Paragraph("4. Q&A Rapido: Domande Tipiche in Sede di Revisione", h1_style))

    qa_data = [
        [
            Paragraph("Domanda Possibile", tbl_header),
            Paragraph("Risposta Consigliata", tbl_header)
        ],
        [
            Paragraph("<b>Da dove parte l'app e come gestisce il login?</b>", tbl_cell_bold),
            Paragraph("L'entry-point è <code>main.py</code> (classe <code>AppController</code>). All'avvio controlla con <code>session_manager</code> se esiste una sessione memorizzata valida. Se sì, ripristina l'utente e apre la <code>MainWindow</code>; altrimenti mostra la <code>LoginWindow</code>.", tbl_cell)
        ],
        [
            Paragraph("<b>Come sono gestite le password e la sicurezza?</b>", tbl_cell_bold),
            Paragraph("Non ci sono password in chiaro nel database. Si usano hash sicuri e salt gestiti in <code>auth.py</code> e <code>security_config.py</code>. L'applicazione adotta inoltre RBAC (Role-Based Access Control) per limitare le funzioni ai volontari rispetto ai referenti.", tbl_cell)
        ],
        [
            Paragraph("<b>Come viene garantita la persistenza dei dati?</b>", tbl_cell_bold),
            Paragraph("I dati sono persistiti in <code>database.json</code>. A supporto opera <code>BackupService.py</code> che esegue snapshot periodici e all'occorrenza di modifiche critiche nella cartella <code>backups/</code>, garantendo tolleranza a corruzioni.", tbl_cell)
        ],
        [
            Paragraph("<b>Che differenza c'è tra Utente, Volontario e Referente?</b>", tbl_cell_bold),
            Paragraph("<code>Utente</code> è la classe base astratta che contiene credenziali e dati anagrafici essenziali. <code>Volontario</code> estende con patenti CRI, storico ore, turni e idoneità; <code>Referente</code> eredita o estende con privilegi gestionali e di coordinamento.", tbl_cell)
        ],
        [
            Paragraph("<b>Come avete verificato il funzionamento del sistema?</b>", tbl_cell_bold),
            Paragraph("Abbiamo implementato una suite di test unitari e di integrazione in <code>tests/test_sistema.py</code> (basata su <code>unittest</code>) che testa flussi completi di login, assegnazione turni, gestione flotta e serializzazione.", tbl_cell)
        ]
    ]

    t_qa = Table(qa_data, colWidths=[5.5*cm, 11.7*cm])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_red),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, alt_bg])
    ]))
    story.append(t_qa)

    # Footer note
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<i>Documento generato per il ripasso pre-revisione • Progetto Gestione Croce Rossa</i>",
        ParagraphStyle('FooterNote', parent=styles['Italic'], fontSize=8, textColor=colors.HexColor("#777777"), alignment=1)
    ))

    doc.build(story)
    print("PDF creato con successo!")

if __name__ == "__main__":
    build_pdf()
