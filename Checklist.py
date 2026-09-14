from __future__ import annotations
from typing import List, TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from Turno import Turno

class Checklist:
    """
    Rappresenta la checklist operativa (pre-partenza o fine turno) della Croce Rossa Italiana.
    I dati e le voci sono estratti direttamente dalla documentazione ufficiale di progetto
    (Goodnotes / Ingegneria Del Software / CHECKLIST):
    - Autista tipo A (Soccorso Avanzato / Emergenza 118)
    - Autista tipo B (Trasporto Ordinario)
    - Soccorritore tipo A (Vano Sanitario / Soccorso Avanzato AALS)
    - Soccorritore tipo B (Vano Sanitario / Ordinario e Sportivo)
    """

    CONTROLLI_CONFIG: Dict[str, List[Dict[str, Any]]] = {
        "Autista A": [
            {
                "categoria": "000-Quick look",
                "nome": "Avviamento Motore e Quadro Strumenti",
                "tipo": "ok_ko",
                "istruzioni": "Verifica accensione rapida, nessuna spia anomala sul cruscotto."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Dispositivi di Emergenza (Sirena primaria, secondaria, lampeggianti, strobo e faro brandeggiabile)",
                "tipo": "ok_ko",
                "istruzioni": "Test acustico e visivo dei lampeggianti blu, strobo griglia e sirene."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Controllo generale - Mezzo e Allestimento",
                "tipo": "ok_ko",
                "istruzioni": "Integrità carrozzeria, chiusura porte, gradino laterale e pedana."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Pneumatici (Controllo visivo ed efficienza) + presenza catene da neve",
                "tipo": "ok_ko",
                "istruzioni": "Pressione, usura battistrada e presenza catene a bordo."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Impianto distribuzione O2 e Manometri di linea",
                "tipo": "ok_ko",
                "istruzioni": "Verifica pressione impianto e tenuta raccordi rapidi."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Bombola Fissa O2 - UNO (7lt)",
                "tipo": "ok_ko",
                "istruzioni": "Pressione bombola principale >= 150 bar."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Bombola Fissa O2 - DUE (7lt)",
                "tipo": "ok_ko",
                "istruzioni": "Pressione bombola secondaria >= 150 bar."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Monitor Defibrillatore (Presenza e Fissaggio su supporto)",
                "tipo": "ok_ko",
                "istruzioni": "Presenza nel vano e collegamento al caricatore a parete."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Sedia Cingolata per trasporto scale",
                "tipo": "ok_ko",
                "istruzioni": "Meccanismo di sblocco e cingoli integri."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Barella autocaricante + cinture (set completo)",
                "tipo": "ok_ko",
                "istruzioni": "Carrello, gambe ripiegabili e set cinture a 5 punti."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Telo portaferiti con maniglie",
                "tipo": "ok_ko",
                "istruzioni": "Integrità tessuto e maniglie di sollevamento."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Barella Cucchiaio + cinture a moschettone (n°4)",
                "tipo": "ok_ko",
                "istruzioni": "Ganci a scatto e 4 cinture presenti."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Barella Spinale + Ragno e fermacapi",
                "tipo": "ok_ko",
                "istruzioni": "Spinale rigida, cinghie a ragno e coppia cuscini fermacapo."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Bombolino O2 Portatile - UNO (2/3 lt)",
                "tipo": "ok_ko",
                "istruzioni": "Pressione bombolino portatile 1."
            },
            {
                "categoria": "000-Quick look",
                "nome": "Bombolino O2 Portatile - DUE (2/3 lt)",
                "tipo": "ok_ko",
                "istruzioni": "Pressione bombolino portatile 2."
            },
            {
                "categoria": "100-Mezzo",
                "nome": "Controllo livelli (Liquido Radiatore, tergicristalli, servosterzo)",
                "tipo": "ok_ko",
                "istruzioni": "Vaschetta radiatore, liquido lavavetri e olio sterzo."
            },
            {
                "categoria": "100-Mezzo",
                "nome": "Documentazione Veicolo (Assicurazione, Libretto di circolazione, Revisione e Tessera carburante)",
                "tipo": "ok_ko",
                "istruzioni": "Documenti in regola nel cruscotto."
            },
            {
                "categoria": "100-Mezzo",
                "nome": "(3) Caschi di Protezione",
                "tipo": "ok_ko",
                "istruzioni": "Caschi protettivi omologati per equipaggio."
            },
            {
                "categoria": "100-Mezzo",
                "nome": "Dispositivi di Sicurezza (Cicalino retromarcia, sensore prossimità, telecamera)",
                "tipo": "ok_ko",
                "istruzioni": "Funzionamento cicalino e retrocamera su retromarcia."
            },
            {
                "categoria": "100-Mezzo",
                "nome": "(2) Estintori (V. guida e V. sanitario)",
                "tipo": "ok_ko",
                "istruzioni": "Manometro sul verde e cartellino revisione valido."
            },
            {
                "categoria": "100-Mezzo",
                "nome": "Torcia Elettrica (+cono giallo)",
                "tipo": "ok_ko",
                "istruzioni": "Carica e cono per segnalazione stradale."
            },
            {
                "categoria": "100-Mezzo",
                "nome": "Livello Carburante",
                "tipo": "scelta",
                "opzioni": ["PIENO", "3/4", "1/2", "RISERVA"],
                "istruzioni": "Verifica livello serbatoio gasolio."
            },
            {
                "categoria": "100-Mezzo",
                "nome": "Livello Olio motore",
                "tipo": "scelta",
                "opzioni": ["Pieno", "1/2", "Vuoto"],
                "istruzioni": "Astina di controllo tra min e max."
            },
            {
                "categoria": "100-Mezzo",
                "nome": "Impianto di climatizzazione (intero sistema cabina e vano)",
                "tipo": "ok_ko",
                "istruzioni": "Aria calda/fredda e ricircolo."
            },
            {
                "categoria": "100-Mezzo",
                "nome": "Radio Veicolare CRI / 118 + Telefono (dispositivi) di servizio",
                "tipo": "ok_ko",
                "istruzioni": "Canale regionale 118 impostato e telefono carico."
            },
            {
                "categoria": "100-Mezzo",
                "nome": "Kit da scasso + Kit cambio Ruota (Ruota di scorta)",
                "tipo": "ok_ko",
                "istruzioni": "Piede di porco, cric e chiave bulloni."
            },
            {
                "categoria": "200-Monossido",
                "nome": "Rilevatore CO (Monossido)",
                "tipo": "ok_ko",
                "istruzioni": "Acceso e test batteria OK."
            },
            {
                "categoria": "400-Attrezzature",
                "nome": "Materassino a depressione (+pompa)",
                "tipo": "ok_ko",
                "istruzioni": "Assenza fori, valvola a tenuta e pompa aspirazione."
            },
            {
                "categoria": "400-Attrezzature",
                "nome": "(1 Set) Steccobende a depressione/rigide",
                "tipo": "ok_ko",
                "istruzioni": "Steccobende per arti superiori e inferiori."
            },
            {
                "categoria": "400-Attrezzature",
                "nome": "(2 set) Set Collari cervicali Adulto e Pediatrico",
                "tipo": "ok_ko",
                "istruzioni": "Collari regolabili monopezzo."
            },
            {
                "categoria": "400-Attrezzature",
                "nome": "KED (Kendrick Extrication Device)",
                "tipo": "ok_ko",
                "istruzioni": "Corpetto estricatore e cinte colorate."
            },
            {
                "categoria": "400-Attrezzature",
                "nome": "(2) T-POD (Cintura di immobilizzazione pelvica)",
                "tipo": "ok_ko",
                "istruzioni": "Presidi pelvici di emostasi."
            },
            {
                "categoria": "400-Attrezzature",
                "nome": "Adattatore Pediatrico per Spinale (Pedi-Sleeve)",
                "tipo": "ok_ko",
                "istruzioni": "Guaina pediatrica per tavola spinale."
            },
            {
                "categoria": "400-Attrezzature",
                "nome": "Adattatore Pediatrico per Barella Autocaricante (Pedi-Mate)",
                "tipo": "ok_ko",
                "istruzioni": "Sistema ritenuta pediatrica per barella."
            },
            {
                "categoria": "800-Materiale Vario",
                "nome": "Biancheria e Pulizia",
                "tipo": "ok_ko",
                "istruzioni": "Lenzuolini monouso, coperte e disinfezione superfici."
            }
        ],
        "Autista B": [
            {
                "categoria": "100-Veicolo",
                "nome": "Pneumatici (Controllo visivo ed efficienza)",
                "tipo": "ok_ko",
                "istruzioni": "Pressione e assenza tagli."
            },
            {
                "categoria": "100-Veicolo",
                "nome": "Dispositivi di Sicurezza (Cicalino retromarcia, Sensore, Telecamera)",
                "tipo": "ok_ko",
                "istruzioni": "Segnalatore acustico e retrocamera."
            },
            {
                "categoria": "100-Veicolo",
                "nome": "Dispositivi di Emergenza (Sirena primaria/secondaria/lampeggianti/strobo)",
                "tipo": "ok_ko",
                "istruzioni": "Lampeggianti e sirena ordinaria."
            },
            {
                "categoria": "100-Veicolo",
                "nome": "(2) Estintori (vano guida + vano sanitario)",
                "tipo": "ok_ko",
                "istruzioni": "Manometro sul verde e cartellino revisione."
            },
            {
                "categoria": "100-Veicolo",
                "nome": "Livello Carburante",
                "tipo": "scelta",
                "opzioni": ["PIENO", "3/4", "1/2", "RISERVA"],
                "istruzioni": "Verifica livello carburante."
            },
            {
                "categoria": "100-Veicolo",
                "nome": "Livello Olio Motore",
                "tipo": "ok_ko",
                "istruzioni": "Controllo astina livello olio."
            },
            {
                "categoria": "100-Veicolo",
                "nome": "Controllo Altri Livelli (Liquido Radiatore, tergicristalli)",
                "tipo": "ok_ko",
                "istruzioni": "Vaschetta lavavetri e antigelo."
            },
            {
                "categoria": "100-Veicolo",
                "nome": "Impianto di Climatizzazione",
                "tipo": "ok_ko",
                "istruzioni": "Aria condizionata e riscaldamento."
            },
            {
                "categoria": "100-Veicolo",
                "nome": "Documentazione Veicolo (Assicurazione, Libretto circolazione e Revisione)",
                "tipo": "ok_ko",
                "istruzioni": "Documenti di bordo validi."
            },
            {
                "categoria": "100-Veicolo",
                "nome": "Radio Veicolare CRI + Telefono di Servizio",
                "tipo": "ok_ko",
                "istruzioni": "Apparati accesi e funzionanti."
            },
            {
                "categoria": "100-Veicolo",
                "nome": "n°2 fiaccole di segnalazione + Guanti di protezione",
                "tipo": "ok_ko",
                "istruzioni": "Dispositivi per segnalazione incidenti."
            },
            {
                "categoria": "100-Veicolo",
                "nome": "Catene da neve",
                "tipo": "ok_ko",
                "istruzioni": "Presenza a bordo della misura corretta."
            },
            {
                "categoria": "200-Presidi Sanitari",
                "nome": "Barella Autocaricante + set completo di cinte",
                "tipo": "ok_ko",
                "istruzioni": "Verifica aggancio carrello e cinte."
            },
            {
                "categoria": "200-Presidi Sanitari",
                "nome": "Telo con Maniglie (sotto barella)",
                "tipo": "ok_ko",
                "istruzioni": "Telo pulito e ripiegato."
            },
            {
                "categoria": "200-Presidi Sanitari",
                "nome": "Barella Cucchiaio + Set Cinte",
                "tipo": "ok_ko",
                "istruzioni": "Lame e agganci di blocco."
            },
            {
                "categoria": "200-Presidi Sanitari",
                "nome": "Sedia Cardiopatica / Portantina",
                "tipo": "ok_ko",
                "istruzioni": "Ruote e maniglie di trasporto."
            },
            {
                "categoria": "200-Presidi Sanitari (SPORTIVI)",
                "nome": "(SPORTIVO) Barella Spinale + Ragno e Fermacapi",
                "tipo": "ok_ko",
                "istruzioni": "Presenza presidi per servizio sportivo."
            },
            {
                "categoria": "200-Presidi Sanitari (SPORTIVI)",
                "nome": "(SPORTIVO) Set Steccobende",
                "tipo": "ok_ko",
                "istruzioni": "Stecche immobilizzatrici a bordo."
            },
            {
                "categoria": "300-Materiale Vario",
                "nome": "Biancheria (Lenzuola, Coperte)",
                "tipo": "ok_ko",
                "istruzioni": "Lenzuolini monouso e coperte pulite."
            },
            {
                "categoria": "400-DPI",
                "nome": "Guanti Monouso",
                "tipo": "ok_ko",
                "istruzioni": "Scatole di guanti M/L a bordo."
            }
        ],
        "Soccorritore A": [
            {
                "categoria": "100-Mezzo",
                "nome": "Impianto di Ventilazione (immissione ed estrazione)",
                "tipo": "ok_ko",
                "istruzioni": "Ventole vano sanitario accese e funzionanti."
            },
            {
                "categoria": "300-Ossigenoterapia",
                "nome": "Funzione Respiratoria Adulto (Maschere Reservoir, Occhialini O2, Venturi, Aerosol)",
                "tipo": "ok_ko",
                "istruzioni": "• (2) Maschere Reservoir\n• (2) Occhialini O2\n• (1) Maschera Venturi\n• (1) Maschera Aerosol"
            },
            {
                "categoria": "300-Ossigenoterapia",
                "nome": "Funzione Respiratoria Adulto (2) (Ambu + Reservoir + Raccordo Mount + Cannule Guedel)",
                "tipo": "ok_ko",
                "istruzioni": "• Ambu + Reservoir + Filtro antibatterico + Prolunga\n• Maschere Ambu 3/4/5\n• Guedel 2/3/4/5\n• Cannule rinofaringee 26/28"
            },
            {
                "categoria": "300-Ossigenoterapia",
                "nome": "Funzione Respiratoria Bambino (Ambu Pediatrico e Neonatale + Maschere)",
                "tipo": "ok_ko",
                "istruzioni": "• Ambu Pediatrico + Ambu Neonatale con reservoir\n• Maschere 0/1/2\n• Guedel pediatriche 000/00/0/1"
            },
            {
                "categoria": "450-Dispositivi Medici",
                "nome": "Ventilatore Polmonare + Circuito O2 + Tubo Corrugato + Bombola O2",
                "tipo": "ok_ko",
                "istruzioni": "Test autodiagnosi, carica batteria e circuito O2 collegato."
            },
            {
                "categoria": "450-Dispositivi Medici",
                "nome": "Aspiratore Fisso (Serbatoio / Tubo a bolle)",
                "tipo": "ok_ko",
                "istruzioni": "Verifica livello vuoto e vaso raccolta."
            },
            {
                "categoria": "450-Dispositivi Medici",
                "nome": "Aspiratore Portatile (Serres, tubo a bolle, sonde Yankauer)",
                "tipo": "ok_ko",
                "istruzioni": "1) Funzionamento a batteria\n2) Sacca Serres e sonde 8-18\n3) Ancoraggio e messa in carica"
            },
            {
                "categoria": "450-Dispositivi Medici",
                "nome": "Vani Condizionati (Caldo e Freddo)",
                "tipo": "ok_ko",
                "istruzioni": "Temperatura corretta per liquidi di infusione."
            },
            {
                "categoria": "450-Dispositivi Medici",
                "nome": "Pompa Infusione a siringa",
                "tipo": "ok_ko",
                "istruzioni": "Presenza pompa, cavo e set siringhe dedicate."
            },
            {
                "categoria": "450-Dispositivi Medici (Materiale)",
                "nome": "CASSETTO 1 - Monitor (Elettrodi ECG, piastre DAE, rasoi, gel)",
                "tipo": "ok_ko",
                "istruzioni": "• Elettrodi ECG\n• Piastra Adulto e Pediatrico\n• Rasoi e Gel ECG\n• Carta millimetrata di riserva"
            },
            {
                "categoria": "450-Dispositivi Medici (Materiale)",
                "nome": "CASSETTO 2 - Aspiratore (Sondini 6-18, Yankauer, Serres)",
                "tipo": "ok_ko",
                "istruzioni": "• Sondini aspirazione 6/8/10/12/14/18\n• Sonda Yankauer\n• Vaso Serres e tubo di ricambio"
            },
            {
                "categoria": "450-Dispositivi Medici (Materiale)",
                "nome": "CASSETTO 3 - Vario (Termometro, Glicemia, Pile, Sfigmomanometro)",
                "tipo": "ok_ko",
                "istruzioni": "• Termometro infrarossi\n• Kit Glicemia (Stick + aghi + salviette)\n• Pile di riserva per saturimetro\n• Sfigmomanometro manuale"
            },
            {
                "categoria": "500-Infusione",
                "nome": "Set Infusione (1 di 2) (Lacci, Agocannule 14-24, Deflussori, Rubinetto 3 vie)",
                "tipo": "ok_ko",
                "istruzioni": "• Laccio FAST e tourniquet\n• Agocannule 14/16/18/20/22/24\n• Deflussori e raccordi a 3 vie"
            },
            {
                "categoria": "500-Infusione",
                "nome": "Set Infusione (2 di 2) (Tegaderm, Siringhe, MAD nasale, Agobox)",
                "tipo": "ok_ko",
                "istruzioni": "• Medicazioni tegaderm e fixomull\n• Siringhe varie misure\n• Dispositivo MAD somministrazione nasale\n• Contenitore taglienti Agobox"
            },
            {
                "categoria": "500-Infusione",
                "nome": "Vano: Infusione (Fisiologica 0.9%, Ringer Lattato, Glucosata 5%)",
                "tipo": "ok_ko",
                "istruzioni": "• (2) Fisiologica 500/250/100 ml\n• (2) Ringer Lattato 500 ml\n• (2) Glucosata 5%"
            },
            {
                "categoria": "600-Medicazione",
                "nome": "Medicazione (1 di 2) (Disinfettanti, Cerotti, Ghiaccio istantaneo, Telini)",
                "tipo": "ok_ko",
                "istruzioni": "• Acqua ossigenata, Amuchina, Braunol\n• Cerotti medicati e cerotto seta\n• (5) Confezioni ghiaccio istantaneo\n• Bende e telini sterili"
            },
            {
                "categoria": "600-Medicazione",
                "nome": "Medicazione (2 di 2) (Tourniquet, Teli termici, Guanti sterili, Kit medicazione)",
                "tipo": "ok_ko",
                "istruzioni": "• (2) Tourniquet emostatici\n• (2) Teli termici isotermici oro/argento\n• Guanti sterili S/M/L/XL"
            },
            {
                "categoria": "700-DPI",
                "nome": "DPI Vano Sanitario (Guanti, mascherine FFP2/chirurgiche, camici)",
                "tipo": "ok_ko",
                "istruzioni": "Dispositivi di protezione individuale per equipaggio sanitario."
            },
            {
                "categoria": "750-KIT",
                "nome": "Kit C-PAP (Manometro, Valvola Boussignac, Maschere 3/4/5)",
                "tipo": "ok_ko",
                "istruzioni": "• Manometro e valvola Boussignac\n• Nucale e maschere facciali\n(Necessario per emergenza avanzata)"
            },
            {
                "categoria": "750-KIT",
                "nome": "Kit Vari (Cateterismo Vescicale, Sondino Nasogastrico)",
                "tipo": "ok_ko",
                "istruzioni": "• Cateteri vescicali 14/16/18/20 e sacca raccolta\n• Sondini nasogastrici e lubrificante"
            },
            {
                "categoria": "750-KIT",
                "nome": "Kit Intubazione (Laringoscopio Adulto/Pediatrico, Tubi 2-8.5, Mandrini)",
                "tipo": "ok_ko",
                "istruzioni": "• Laringoscopio lame Macintosh e Miller\n• Tubi endotracheali da 2 a 8.5\n• Mandrini e raccordi Mount"
            },
            {
                "categoria": "800-Materiale Vario",
                "nome": "Materiale Vario (Sacchetti raccolta, Padella, Pappagallo, Rilevatore CO)",
                "tipo": "ok_ko",
                "istruzioni": "• Sacchetti graduati\n• Padella e pappagallo igienizzati\n• Forbici tagliaabiti Robin di parete\n• Rilevatore CO acceso"
            },
            {
                "categoria": "900-Zaino",
                "nome": "Zaino di Soccorso Emergenza 118",
                "tipo": "ok_ko",
                "istruzioni": "Zaino completo, sigillato e pronto all'uso con presidi primari."
            }
        ],
        "Soccorritore B": [
            {
                "categoria": "500-Controllo Generale",
                "nome": "Aria Condizionata e Sistema ricambio vano sanitario (Immissione, Espulsione)",
                "tipo": "ok_ko",
                "istruzioni": "Funzionamento bocchette aerazione vano paziente."
            },
            {
                "categoria": "500-Controllo Generale",
                "nome": "Illuminazione vano sanitario (Luce bianca, luce notturna blu, spot)",
                "tipo": "ok_ko",
                "istruzioni": "Tutti i punti luce a soffitto funzionanti."
            },
            {
                "categoria": "600-Supporto Vitale",
                "nome": "DAE (+2 Piastre Adulto)",
                "tipo": "ok_ko",
                "istruzioni": "Defibrillatore con spia verde lampeggiante e piastre sigillate non scadute."
            },
            {
                "categoria": "600-Supporto Vitale",
                "nome": "Parametri Vitali (Saturimetro, Sfigmomanometro, Fonendoscopio, Termometro)",
                "tipo": "ok_ko",
                "istruzioni": "Pulsossimetro con pile cariche, bracciale e fonendo a bordo."
            },
            {
                "categoria": "600-Supporto Vitale",
                "nome": "Bombola UNO - Pressione e Controllo fissaggio",
                "tipo": "ok_ko",
                "istruzioni": "Manometro bombola fissa >= 100 bar, ancoraggio a parete serrato."
            },
            {
                "categoria": "600-Supporto Vitale",
                "nome": "Impianto Ossigeno (Flussimetro e Umidificatore)",
                "tipo": "ok_ko",
                "istruzioni": "Regolazione flussimetro e tenuta gas."
            },
            {
                "categoria": "600-Supporto Vitale",
                "nome": "Bombolino PORTATILE - Pressione e Controllo fissaggio",
                "tipo": "ok_ko",
                "istruzioni": "Bombola portatile carica per trasporto paziente."
            },
            {
                "categoria": "600-Supporto Vitale",
                "nome": "Funzione Respiratoria (n°4 Reservoir / n°4 Occhialini)",
                "tipo": "ok_ko",
                "istruzioni": "Maschere monouso sigillate con sacchetto e cannule nasali."
            },
            {
                "categoria": "600-Supporto Vitale",
                "nome": "Aspiratore Fisso (Serbatoio / Tubo a bolle)",
                "tipo": "ok_ko",
                "istruzioni": "Test aspirazione e pulizia vaso."
            },
            {
                "categoria": "600-Supporto Vitale",
                "nome": "(SPORTIVO) Aspiratore Portatile a batteria",
                "tipo": "ok_ko",
                "istruzioni": "Batteria carica per impiego su campo sportivo."
            },
            {
                "categoria": "700-Medicazione",
                "nome": "Medicazione (Garze sterili, bende, cerotti, disinfettante)",
                "tipo": "ok_ko",
                "istruzioni": "Kit medicazione completo e non scaduto."
            },
            {
                "categoria": "750-DPI",
                "nome": "Guanti Monouso - Vano Sanitario",
                "tipo": "ok_ko",
                "istruzioni": "Scatole guanti lattice/nitrile taglie M e L."
            },
            {
                "categoria": "750-DPI",
                "nome": "Dispositivi di Protezione (Mascherine FFP2, camici, visiere)",
                "tipo": "ok_ko",
                "istruzioni": "DPI puliti a disposizione dell'equipaggio."
            },
            {
                "categoria": "800-Vario",
                "nome": "Materiale Vario (Bacinelle, sacchetti vomito, teli puliti)",
                "tipo": "ok_ko",
                "istruzioni": "Materiale igienico a bordo."
            },
            {
                "categoria": "800-Vario",
                "nome": "(SPORTIVO) Zaino di Intervento per MANIFESTAZIONI/SPORTIVI",
                "tipo": "ok_ko",
                "istruzioni": "Zaino pronto per assistenza a gare o manifestazioni."
            }
        ]
    }

    def __init__(
        self,
        id: str,
        controlliMeccanici: bool = False,
        dispositiviMediciRichiesti: List[str] = None,
        dispositiviPresenti: bool = False,
        turnoAssegnato: Optional[Turno] = None,
        controlliMeccaniciOk: bool = None,
        risposte: Optional[Dict[str, str]] = None,
        ruoloCompilatore: str = ""
    ):
        self.id = id
        self.turnoAssegnato = turnoAssegnato
        self.dispositiviMediciRichiesti = dispositiviMediciRichiesti if dispositiviMediciRichiesti is not None else []
        self.dispositiviPresenti = dispositiviPresenti
        self.controlliMeccaniciOk = controlliMeccaniciOk if controlliMeccaniciOk is not None else controlliMeccanici
        self.controlliMeccanici = self.controlliMeccaniciOk
        self.risposte: Dict[str, str] = risposte if risposte is not None else {}
        self.ruoloCompilatore: str = ruoloCompilatore

    @classmethod
    def normalizzaRuolo(cls, ruolo: str) -> str:
        """Normalizza la stringa del ruolo in una delle 4 categorie definite dal Model Report."""
        r = str(ruolo or "").strip()
        if "Autista A" in r or ("Emergenza" in r and "Autista" in r) or r == "Autista":
            return "Autista A"
        elif "Autista B" in r or ("Ordinario" in r and "Autista" in r):
            return "Autista B"
        elif "Soccorritore A" in r or "Avanzato" in r or "Sanitario" in r:
            return "Soccorritore A"
        elif "Soccorritore B" in r or "Ordinario" in r:
            return "Soccorritore B"
        else:
            return "Soccorritore A"

    @classmethod
    def getControlliPerRuolo(cls, ruolo: str) -> List[Dict[str, Any]]:
        chiave = cls.normalizzaRuolo(ruolo)
        return cls.CONTROLLI_CONFIG.get(chiave, cls.CONTROLLI_CONFIG["Autista A"])

    def getControlliMeccaniciBase(self) -> List[str]:
        return [c["nome"] for c in self.CONTROLLI_CONFIG["Autista B"]]

    def getControlliMeccaniciEmergenza(self) -> List[str]:
        return [c["nome"] for c in self.CONTROLLI_CONFIG["Autista A"]]

    def getDispositiviSanitariAvanzati(self) -> List[str]:
        return [c["nome"] for c in self.CONTROLLI_CONFIG["Soccorritore A"]]

    def getDispositiviSanitariBase(self) -> List[str]:
        return [c["nome"] for c in self.CONTROLLI_CONFIG["Soccorritore B"]]

    def verificaIdoneita(self) -> bool:
        """Verifica se la checklist non presenta anomalie bloccanti (tutti i controlli meccanici e sanitari OK)."""
        if self.risposte:
            ha_ko = any(v in ["KO", "RISERVA", "Vuoto"] for v in self.risposte.values())
            self.controlliMeccanici = not ha_ko
            self.dispositiviPresenti = not ha_ko
            self.controlliMeccaniciOk = self.controlliMeccanici
            return not ha_ko
        return bool(self.controlliMeccanici and self.dispositiviPresenti)

    def segnalaAnomalia(self) -> List[str]:
        """Restituisce l'elenco delle voci che hanno fallito il controllo per la notifica all'officina/referente."""
        anomalie = []
        for nome, esito in self.risposte.items():
            if esito in ["KO", "RISERVA", "Vuoto"]:
                anomalie.append(f"{nome} ({esito})")
        return anomalie
