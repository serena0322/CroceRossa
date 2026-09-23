from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from Turno import Turno

class Mezzo:
    """
    Rappresenta un automezzo appartenente al parco veicoli della Croce Rossa Italiana (Ambulanze, furgoni, automediche).
    Incapsula lo stato operativo, la cronologia dei chilometri percorsi e le scadenze legali/assicurative.
    """
    def __init__(
        self,
        targa: str,
        tipo: str,
        chilometraggioTotale: int = 0,
        stato: str = "Disponibile",
        dataScadenzaAssicurazione: str = "",
        # Compatibility arguments:
        chilometraggio: int | None = None,
        dispositivi_richiesti: List[str] | None = None,
        checklist: List[str] | None = None,
        disponibile: bool = True
    ):
        self.targa = targa
        self.tipo = tipo
        self.chilometraggioTotale = chilometraggio if chilometraggio is not None else chilometraggioTotale
        
        if isinstance(stato, list):
            self.stato = ", ".join(stato)
        else:
            self.stato = stato
            
        self.dataScadenzaAssicurazione = dataScadenzaAssicurazione
        self.turni_assegnati: List[Turno] = []
        
        # Compatibility attributes:
        self.dispositivi_presenti = dispositivi_richiesti if dispositivi_richiesti is not None else []
        self.dispositivi_richiesti = self.dispositivi_presenti
        self.checklist = checklist if checklist is not None else []
        self._disponibile = disponibile

    @property
    def chilometraggio(self) -> int:
        """Alias compatibile per il chilometraggio totale del veicolo."""
        return self.chilometraggioTotale
    
    @chilometraggio.setter
    def chilometraggio(self, val: int):
        self.chilometraggioTotale = val

    @property
    def disponibile(self) -> bool:
        """Verifica se il mezzo è libero e pronto per essere assegnato a un servizio."""
        return self.stato == "Disponibile" or self.stato == "disponibile" or getattr(self, '_disponibile', True)
        
    @disponibile.setter
    def disponibile(self, val: bool):
        self._disponibile = val
        if val:
            self.stato = "Disponibile"

    def assegna_a_turno(self, turno: Turno):
        """Associa il mezzo al turno di servizio e ne imposta lo stato ad Assegnato."""
        self.turni_assegnati.append(turno)
        self.stato = "Assegnato"
        self._disponibile = False
        print(f"✅ Il mezzo {self.targa} è stato assegnato al turno del {turno.data}.")

    def libera_mezzo(self):
        """Ripristina la disponibilità del mezzo al termine del servizio."""
        self.stato = "Disponibile"
        self._disponibile = True
        print(f"🟢 Il mezzo {self.targa} è ora disponibile.")

    def aggiornaKm(self, kmPercorsi: int) -> None:
        """
        Aggiorna il contachilometri totale garantendo la monotonicità:
        il chilometraggio non può diminuire rispetto al valore precedentemente registrato.
        """
        if kmPercorsi >= self.chilometraggioTotale:
            self.chilometraggioTotale = kmPercorsi
            print(f"📈 Chilometraggio aggiornato a {self.chilometraggioTotale} km.")
        else:
            print("⚠️ Errore: il chilometraggio inserito è inferiore a quello attuale.")

    def aggiorna_km(self, nuovi_km: int):
        """Alias snake_case per aggiornaKm."""
        self.aggiornaKm(nuovi_km)

    def cambiaStato(self, s: str) -> None:
        """Modifica lo stato operativo del mezzo (Disponibile, Assegnato, In Manutenzione, Dismesso)."""
        self.stato = s
        print(f"Stato del mezzo {self.targa} cambiato in {s}.")

    def fineRiparazione(self) -> None:
        """Registra il rientro del mezzo dall'officina e lo rende nuovamente utilizzabile."""
        self.stato = "Disponibile"
        self._disponibile = True
        print(f"🔧 Riparazione terminata per il mezzo {self.targa}. Ora disponibile.")

    def inviaInOfficina(self) -> None:
        """Imposta lo stato del mezzo 'In Manutenzione' escludendolo dai servizi prenotabili."""
        self.stato = "In Manutenzione"
        self._disponibile = False
        print(f"🔧 Mezzo {self.targa} inviato in officina.")

    def isDismesso(self, limite_km: int = 400000) -> bool:
        """
        Verifica se il veicolo ha concluso il proprio ciclo di vita operativo:
        per standard di sicurezza dei mezzi di soccorso CRI, si prevede una soglia indicativa
        di 400.000 km oppure lo stato esplicito 'Dismesso'.
        """
        return self.stato == "Dismesso" or self.chilometraggioTotale >= limite_km

    def radiazioneVeicolo(self) -> None:
        """Dismette permanentemente il mezzo dal parco flotta CRI."""
        self.stato = "Dismesso"
        self._disponibile = False
        print(f"🗑️ Veicolo {self.targa} radiato.")

    def aggiorna_firestore(self):
        """Salva lo stato corrente del mezzo su Cloud Firestore."""
        from FirebaseConfig import db
        db.collection("mezzi").document(self.targa).set({
            "targa": self.targa,
            "tipo": self.tipo,
            "chilometraggioTotale": self.chilometraggioTotale,
            "stato": self.stato,
            "dataScadenzaAssicurazione": self.dataScadenzaAssicurazione,
            "disponibile": self.disponibile
        }, merge=True)
