from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from database import DatabaseManager
from engine import ClinicalEngine

app = FastAPI(title="ValidRx API", version="3.5.0", description="Open Source Clinical Decision Support System")

# --- DEPENDÊNCIAS ---
db = DatabaseManager()

def get_engine():
    # Recarrega dados a cada chamada para pegar atualizações
    return ClinicalEngine(db.get_all_drugs_dict(), db.get_interactions())

async def verify_admin_key(x_admin_key: str = Header(None)):
    if x_admin_key != "VALIDRX_OPEN_SOURCE": # Em prod, use ENV vars
        raise HTTPException(status_code=403, detail="Chave de Admin Inválida")

# --- MODELOS ---
class PediatricRule(BaseModel):
    modo: str
    min: float
    max: float
    teto_dose: float

class DrugCreate(BaseModel):
    id: str
    nome: str
    principio_ativo: str
    classe_terapeutica: str
    familias_alergia: List[str] = []
    concentracao_mg_ml: float = 0
    min_idade_meses: int = 0
    dose_max_diaria_adulto_mg: float = 0
    contra_indicacoes: List[str] = []
    vias_permitidas: List[str]
    pediatria: Optional[PediatricRule] = None

class ClinicalCheckPayload(BaseModel):
    patient_weight_kg: float
    patient_age_months: int
    patient_conditions: List[str] = []
    patient_allergies: List[str] = []
    patient_current_meds: List[str] = []
    prescription_drug_id: str
    prescription_dose_input: float
    prescription_route: str
    prescription_freq_hours: int

# --- ENDPOINTS ---

@app.post("/api/admin/drugs", tags=["Admin"], dependencies=[Depends(verify_admin_key)])
def create_drug(drug: DrugCreate):
    """Cadastra nova regra de medicamento."""
    ped_dict = drug.pediatria.dict() if drug.pediatria else None
    db.add_drug(
        drug.id, drug.nome, drug.principio_ativo, drug.classe_terapeutica,
        drug.familias_alergia, drug.concentracao_mg_ml, drug.min_idade_meses,
        drug.dose_max_diaria_adulto_mg, drug.contra_indicacoes, drug.vias_permitidas, ped_dict
    )
    return {"msg": f"Medicamento {drug.nome} cadastrado."}

@app.post("/api/clinical-check", tags=["Clinical"])
def validate(payload: ClinicalCheckPayload):
    """Endpoint principal de validação (Usado por Tasy/MV)."""
    engine = get_engine()
    
    patient = {
        "weight_kg": payload.patient_weight_kg, "age_months": payload.patient_age_months,
        "conditions": payload.patient_conditions, "allergies": payload.patient_allergies,
        "current_meds": payload.patient_current_meds
    }
    presc = {
        "drug_id": payload.prescription_drug_id, "dose_input": payload.prescription_dose_input,
        "route": payload.prescription_route, "freq_hours": payload.prescription_freq_hours
    }
    
    alerts = engine.validate(patient, presc)
    status = "BLOCKED" if any(a['type'] == 'BLOCK' for a in alerts) else ("WARNING" if alerts else "APPROVED")
    
    return {"status": status, "alerts": alerts}