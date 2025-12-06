import os
from typing import List, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.engine import ClinicalEngine
from src.database import DatabaseManager

# ============================
# 🔷 NOVO: CAMADA DE NORMALIZAÇÃO (TRADUTOR)
# ============================

# Mapeamento de siglas de mercado (MV/Tasy) para o padrão ValidRx
ROUTE_MAPPING = {
    # Vias Venosas
    "EV": "Endovenosa (IV)",
    "IV": "Endovenosa (IV)",
    "INTRAVENOSA": "Endovenosa (IV)",
    
    # Vias Musculares
    "IM": "Intramuscular (IM)",
    "INTRAMUSCULAR": "Intramuscular (IM)",
    
    # Vias Orais
    "VO": "Oral",
    "ORAL": "Oral",
    "PO": "Oral", # Per Os (latim)
    
    # Subcutânea
    "SC": "Subcutânea",
    "SQ": "Subcutânea",
    "SUBCUTANEA": "Subcutânea"
}

def normalize_route(route_input: str) -> str:
    """
    Traduz siglas (EV, IM, VO) para o padrão do banco de dados.
    Ex: Recebe 'EV' -> Retorna 'Endovenosa (IV)'
    """
    if not route_input:
        return "Desconhecida"
    
    # Converte para maiúsculo e busca no mapa. Se não achar, devolve o original.
    return ROUTE_MAPPING.get(route_input.upper(), route_input)

# ============================
# 🔷 CONFIGURAÇÃO DA API
# ============================

# Carrega variável de ambiente
ADMIN_KEY = os.getenv("ADMIN_KEY", "DEFAULT_ADMIN_KEY")

app = FastAPI(
    title="ValidRx API",
    version="3.6.0",
    description="Open Source Clinical Decision Support System"
)

# CORS (opcional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# 🔷 SCHEMAS CLÍNICOS
# ============================

class Patient(BaseModel):
    cd_pessoa_fisica: str
    nm_paciente: str
    nr_atendimento: str
    weight_kg: float
    age_months: int
    conditions: List[str]
    allergies: List[str]
    current_meds: List[str]


class PrescriptionItem(BaseModel):
    cd_item_prescricao: str
    ean_codigo: str
    nm_medicamento: str

    # Campos que a engine usa
    dose_input: float
    dose_unidade: str
    route: str
    freq_hours: int

    # ID interno do banco (PRIMARY KEY)
    drug_id: str


class ClinicalRequest(BaseModel):
    cd_medico: str
    patient: Patient
    items: List[PrescriptionItem]


# ============================
# 🔷 SCHEMAS ADMIN
# ============================

class DrugCreate(BaseModel):
    id: str
    nome: str
    principio_ativo: str
    classe_terapeutica: str
    familias_alergia: List[str]
    concentracao_mg_ml: float
    min_idade_meses: int
    dose_max_diaria_adulto_mg: float
    contra_indicacoes: List[str]
    vias_permitidas: List[str]

    # bloco pediátrico
    pediatria: dict


class InteractionCreate(BaseModel):
    substancia_a: str
    substancia_b: str
    nivel: str
    mensagem: str


# ============================
# 🔷 BANCO DE DADOS
# ============================

db_manager = DatabaseManager()


def _check_admin(x_admin_key: Optional[str]):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Chave de Admin Inválida")


# ============================
# 🔷 ENDPOINTS ADMIN - DRUGS
# ============================

@app.post("/api/admin/drugs")
def create_drug(
    drug: DrugCreate,
    x_admin_key: Optional[str] = Header(None)
):
    """
    Cria ou sobrescreve um medicamento.
    Protegido por X-Admin-Key.
    """
    _check_admin(x_admin_key)

    d = drug
    db_manager.add_drug(
        id=d.id,
        nome=d.nome,
        principio=d.principio_ativo,
        classe=d.classe_terapeutica,
        alergias=d.familias_alergia,
        conc=d.concentracao_mg_ml,
        min_idade=d.min_idade_meses,
        max_adulto=d.dose_max_diaria_adulto_mg,
        contras=d.contra_indicacoes,
        vias=d.vias_permitidas,
        ped_rule=d.pediatria,
    )

    return {"msg": f"Medicamento {drug.nome} cadastrado/atualizado com sucesso."}


@app.get("/api/admin/drugs")
def admin_list_drugs(x_admin_key: Optional[str] = Header(None)):
    """
    Lista todos os medicamentos (admin).
    """
    _check_admin(x_admin_key)
    drugs = db_manager.get_all_drugs_dict()
    # retorna como lista
    return {"drugs": list(drugs.values())}


@app.get("/api/admin/drugs/{drug_id}")
def admin_get_drug(drug_id: str, x_admin_key: Optional[str] = Header(None)):
    """
    Busca um medicamento específico (admin).
    """
    _check_admin(x_admin_key)
    drugs = db_manager.get_all_drugs_dict()
    drug = drugs.get(drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    return drug


@app.put("/api/admin/drugs/{drug_id}")
def admin_update_drug(
    drug_id: str,
    drug: DrugCreate,
    x_admin_key: Optional[str] = Header(None),
):
    """
    Atualiza (na prática, sobrescreve) um medicamento.
    """
    _check_admin(x_admin_key)

    if drug_id != drug.id:
        raise HTTPException(
            status_code=400,
            detail="ID do path e do corpo precisam ser iguais."
        )

    d = drug
    db_manager.add_drug(
        id=d.id,
        nome=d.nome,
        principio=d.principio_ativo,
        classe=d.classe_terapeutica,
        alergias=d.familias_alergia,
        conc=d.concentracao_mg_ml,
        min_idade=d.min_idade_meses,
        max_adulto=d.dose_max_diaria_adulto_mg,
        contras=d.contra_indicacoes,
        vias=d.vias_permitidas,
        ped_rule=d.pediatria,
    )

    return {"msg": f"Medicamento {drug.nome} atualizado com sucesso."}


@app.delete("/api/admin/drugs/{drug_id}")
def admin_delete_drug(drug_id: str, x_admin_key: Optional[str] = Header(None)):
    """
    Remove um medicamento pelo ID (admin).
    """
    _check_admin(x_admin_key)
    deleted = db_manager.delete_drug(drug_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    return {"msg": f"Medicamento {drug_id} removido com sucesso."}


# ============================
# 🔷 ENDPOINTS ADMIN - INTERAÇÕES
# ============================

@app.get("/api/admin/interactions")
def admin_list_interactions(x_admin_key: Optional[str] = Header(None)):
    """
    Lista interações de substâncias (admin).
    """
    _check_admin(x_admin_key)
    return {"interactions": db_manager.get_interactions()}


@app.post("/api/admin/interactions")
def admin_create_interaction(
    interaction: InteractionCreate,
    x_admin_key: Optional[str] = Header(None),
):
    """
    Cria uma nova interação de substâncias (admin).
    """
    _check_admin(x_admin_key)

    db_manager.add_interaction(
        sub_a=interaction.substancia_a,
        sub_b=interaction.substancia_b,
        nivel=interaction.nivel,
        msg=interaction.mensagem,
    )
    return {"msg": "Interação criada com sucesso."}


# ============================
# 🔷 ENDPOINT PÚBLICO - LISTAR DRUGS
# ============================

@app.get("/api/drugs")
def list_drugs():
    """
    Lista todos os medicamentos cadastrados (uso geral).
    """
    drugs = db_manager.get_all_drugs_dict()
    return {"drugs": list(drugs.values())}


# ============================
# 🔷 ENDPOINT CLÍNICO PRINCIPAL
# ============================

@app.post("/api/clinical-check")
def clinical_check(req: ClinicalRequest):
    """
    Endpoint principal de checagem clínica.
    Usa ClinicalEngine com dados vindos do banco.
    Aceita siglas como EV, IM, VO e traduz para o padrão do ValidRx.
    """

    # Carrega engine com drogas e interações
    engine = ClinicalEngine(
        db_manager.get_all_drugs_dict(),
        db_manager.get_interactions()
    )

    results = []

    for item in req.items:
        # 1. Normaliza a rota (Ex: "EV" vira "Endovenosa (IV)")
        route_normalized = normalize_route(item.route)

        # 2. Cria um dicionário dos dados do item e injeta a rota traduzida
        # Isso garante que a engine receba a string exata que está no banco de dados
        prescription_data = item.dict()
        prescription_data['route'] = route_normalized

        # 3. Chama a validação
        alert = engine.validate(
            patient=req.patient.dict(),
            prescription=prescription_data
        )
        
        results.append({
            "item": item.cd_item_prescricao,
            "route_interpreted": route_normalized, # Retorna qual rota foi entendida (útil para debug)
            "alerts": alert
        })

    return {"results": results}

# ============================
# 🔷 HEALTHCHECK
# ============================

@app.get("/")
def root():
    return {"status": "ValidRx API online"}


