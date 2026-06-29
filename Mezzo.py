from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from Turno import Turno

class Mezzo:
    def __init__(
        self,
        targa: str,
        tipo: str,
        chilometraggioTotale: int = 0,
        stato: str = "Disponibile",
        dataScadenzaAssicurazione: str = "",
        # Compatibility arguments:
        chilometraggio: int = None,
        dispositivi_richiesti: List[str] = None,
        checklist: List[str] = None,
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
        return self.chilometraggioTotale
    
    @chilometraggio.setter
    def chilometraggio(self, val: int):
        self.chilometraggioTotale = val

    @property
    def disponibile(self) -> bool:
        # For compatibility:
        return self.stato == "Disponibile" or self.stato == "disponibile" or getattr(self, '_disponibile', True)
        
    @disponibile.setter
    def disponibile(self, val: bool):
        self._disponibile = val
        if val:
            self.stato = "Disponibile"

    def assegna_a_turno(self, turno: Turno):
        self.turni_assegnati.append(turno)
        self.stato = "Assegnato"
        self._disponibile = False
        print(f"✅ Il mezzo {self.targa} è stato assegnato al turno del {turno.data}.")

    def libera_mezzo(self):
        self.stato = "Disponibile"
        self._disponibile = True
        print(f"🟢 Il mezzo {self.targa} è ora disponibile.")

    def aggiornaKm(self, kmPercorsi: int) -> None:
        if kmPercorsi >= self.chilometraggioTotale:
            self.chilometraggioTotale = kmPercorsi
            print(f"📈 Chilometraggio aggiornato a {self.chilometraggioTotale} km.")
        else:
            print("⚠️ Errore: il chilometraggio inserito è inferiore a quello attuale.")

    def aggiorna_km(self, nuovi_km: int):
        self.aggiornaKm(nuovi_km)

    def cambiaStato(self, s: str) -> None:
        self.stato = s
        print(f"Stato del mezzo {self.targa} cambiato in {s}.")

    def fineRiparazione(self) -> None:
        self.stato = "Disponibile"
        self._disponibile = True
        print(f"🔧 Riparazione terminata per il mezzo {self.targa}. Ora disponibile.")

    def inviaInOfficina(self) -> None:
        self.stato = "In Manutenzione"
        self._disponibile = False
        print(f"🔧 Mezzo {self.targa} inviato in officina.")

    def isDismesso(self) -> bool:
        return self.stato == "Dismesso"

    def radiazioneVeicolo(self) -> None:
        self.stato = "Dismesso"
        self._disponibile = False
        print(f"🗑️ Veicolo {self.targa} radiato.")

    def aggiorna_firestore(self):
        from FirebaseConfig import db
        db.collection("mezzi").document(self.targa).set({
            "targa": self.targa,
            "tipo": self.tipo,
            "chilometraggioTotale": self.chilometraggioTotale,
            "stato": self.stato,
            "dataScadenzaAssicurazione": self.dataScadenzaAssicurazione,
            "disponibile": self.disponibile
        }, merge=True)
