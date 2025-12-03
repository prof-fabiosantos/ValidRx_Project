import json
from typing import List, Dict, Any

import requests
import streamlit as st

# ==============================
# Helpers
# ==============================

def get_headers(admin_key: str | None = None) -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if admin_key:
        headers["X-Admin-Key"] = admin_key
    return headers


def str_to_list(value: str) -> List[str]:
    """
    Converte texto em lista de strings.
    Aceita itens separados por vírgula ou quebra de linha.
    """
    if not value:
        return []
    # quebra em linhas, depois em vírgulas
    raw = []
    for line in value.splitlines():
        raw.extend(line.split(","))
    return [x.strip() for x in raw if x.strip()]


def list_to_str(values: List[str] | None) -> str:
    if not values:
        return ""
    return ", ".join(values)


def call_api(
    method: str,
    url: str,
    admin_key: str | None = None,
    payload: Dict[str, Any] | None = None,
):
    try:
        resp = requests.request(
            method=method,
            url=url,
            headers=get_headers(admin_key),
            data=json.dumps(payload) if payload is not None else None,
            timeout=10,
        )
        if resp.status_code >= 400:
            st.error(f"Erro {resp.status_code}: {resp.text}")
            return None
        return resp.json()
    except Exception as e:
        st.error(f"Erro ao chamar API: {e}")
        return None


# ==============================
# Layout geral
# ==============================

st.set_page_config(
    page_title="ValidRx Admin",
    layout="wide",
)

st.title("💊 Painel Admin - ValidRx")

with st.sidebar:
    st.header("⚙️ Configuração")
    base_url = st.text_input(
        "URL base da API",
        value="http://localhost:8000",
        help="Ex: http://localhost:8000",
    )
    admin_key = st.text_input(
        "X-Admin-Key",
        type="password",
        help="Mesma chave configurada na variável ADMIN_KEY da API.",
    )

    st.markdown("---")
    st.caption("Use as abas acima para gerenciar medicamentos, interações e testar a engine clínica.")

tab_meds, tab_interactions, tab_clinical = st.tabs(
    ["💉 Medicamentos", "🔗 Interações", "🧪 Teste Clínico"]
)

# ==============================
# ABA: MEDICAMENTOS
# ==============================

with tab_meds:
    st.subheader("Gerenciamento de Medicamentos")

    subtab_list, subtab_edit, subtab_delete = st.tabs(
        ["📋 Listar", "✏️ Criar / Atualizar", "🗑️ Deletar"]
    )

    # ------- Listar -------
    with subtab_list:
        st.markdown("### 📋 Lista de Medicamentos")
        if st.button("Carregar medicamentos", type="primary"):
            url = f"{base_url}/api/admin/drugs"
            data = call_api("GET", url, admin_key=admin_key)
            if data and "drugs" in data:
                st.success(f"{len(data['drugs'])} medicamentos encontrados.")
                st.json(data["drugs"])

        st.markdown("### 🔍 Buscar medicamento por ID")
        search_id = st.text_input("ID do medicamento para buscar", key="search_drug_id")
        if st.button("Buscar medicamento"):
            if not search_id:
                st.warning("Informe o ID do medicamento.")
            else:
                url = f"{base_url}/api/admin/drugs/{search_id}"
                data = call_api("GET", url, admin_key=admin_key)
                if data:
                    st.json(data)

    # ------- Criar / Atualizar -------
    with subtab_edit:
        st.markdown("### ✏️ Criar / Atualizar Medicamento (Upsert)")

        col_id_nome = st.columns(2)
        with col_id_nome[0]:
            drug_id = st.text_input("ID (ex: MED_AMOX)")
        with col_id_nome[1]:
            nome = st.text_input("Nome comercial")

        col_principio = st.columns(2)
        with col_principio[0]:
            principio_ativo = st.text_input("Princípio ativo")
        with col_principio[1]:
            classe_terapeutica = st.text_input("Classe terapêutica")

        col_num = st.columns(3)
        with col_num[0]:
            concentracao_mg_ml = st.number_input(
                "Concentração (mg/mL)",
                min_value=0.0,
                step=0.1,
            )
        with col_num[1]:
            min_idade_meses = st.number_input(
                "Idade mínima (meses)",
                min_value=0,
                step=1,
            )
        with col_num[2]:
            dose_max_diaria_adulto_mg = st.number_input(
                "Dose máx. diária adulto (mg)",
                min_value=0.0,
                step=10.0,
            )

        col_lists = st.columns(3)
        with col_lists[0]:
            familias_alergia_str = st.text_area(
                "Famílias de alergia (separar por vírgula ou linha)",
                placeholder="penicilina, cefalosporina",
            )
        with col_lists[1]:
            contras_str = st.text_area(
                "Contra-indicações",
                placeholder="insuficiência renal, mononucleose",
            )
        with col_lists[2]:
            vias_str = st.text_area(
                "Vias permitidas",
                placeholder="Oral, Intravenosa (IV), Intramuscular (IM)",
            )

        st.markdown("#### 👶 Regras Pediátricas")
        col_ped = st.columns(4)
        with col_ped[0]:
            modo = st.selectbox(
                "Modo",
                options=["", "mg_kg_dose", "mg_kg_dia"],
                help="mg_kg_dose = dose por kg, mg_kg_dia = total diário por kg",
            )
        with col_ped[1]:
            ped_min = st.number_input("Mín (mg/kg)", min_value=0.0, step=0.1)
        with col_ped[2]:
            ped_max = st.number_input("Máx (mg/kg)", min_value=0.0, step=0.1)
        with col_ped[3]:
            teto_dose = st.number_input(
                "Teto por dose (mg)", min_value=0.0, step=1.0,
                help="0 para sem teto específico."
            )

        if st.button("Salvar medicamento (Upsert)", type="primary"):
            if not drug_id or not nome:
                st.warning("ID e Nome são obrigatórios.")
            else:
                payload = {
                    "id": drug_id,
                    "nome": nome,
                    "principio_ativo": principio_ativo,
                    "classe_terapeutica": classe_terapeutica,
                    "familias_alergia": str_to_list(familias_alergia_str),
                    "concentracao_mg_ml": float(concentracao_mg_ml),
                    "min_idade_meses": int(min_idade_meses),
                    "dose_max_diaria_adulto_mg": float(dose_max_diaria_adulto_mg),
                    "contra_indicacoes": str_to_list(contras_str),
                    "vias_permitidas": str_to_list(vias_str),
                    "pediatria": None,
                }

                if modo:
                    payload["pediatria"] = {
                        "modo": modo,
                        "min": float(ped_min),
                        "max": float(ped_max),
                        "teto_dose": float(teto_dose),
                    }

                url = f"{base_url}/api/admin/drugs"
                data = call_api("POST", url, admin_key=admin_key, payload=payload)
                if data:
                    st.success("✅ Medicamento salvo com sucesso!")
                    st.json(data)

    # ------- Deletar -------
    with subtab_delete:
        st.markdown("### 🗑️ Deletar Medicamento")
        del_id = st.text_input("ID do medicamento para deletar")

        if st.button("Deletar", type="primary"):
            if not del_id:
                st.warning("Informe o ID do medicamento.")
            else:
                url = f"{base_url}/api/admin/drugs/{del_id}"
                data = call_api("DELETE", url, admin_key=admin_key)
                if data:
                    st.success("✅ Medicamento removido (se existia).")
                    st.json(data)

# ==============================
# ABA: INTERAÇÕES
# ==============================

with tab_interactions:
    st.subheader("Gerenciamento de Interações")

    subtab_int_list, subtab_int_add = st.tabs(["📋 Listar", "➕ Adicionar"])

    with subtab_int_list:
        st.markdown("### 📋 Lista de Interações")
        if st.button("Carregar interações", type="primary"):
            url = f"{base_url}/api/admin/interactions"
            data = call_api("GET", url, admin_key=admin_key)
            if data and "interactions" in data:
                st.success(f"{len(data['interactions'])} interações encontradas.")
                st.json(data["interactions"])

    with subtab_int_add:
        st.markdown("### ➕ Nova Interação")

        col_int = st.columns(2)
        with col_int[0]:
            substancia_a = st.text_input("Substância A", placeholder="varfarina")
        with col_int[1]:
            substancia_b = st.text_input("Substância B", placeholder="ibuprofeno")

        col_int2 = st.columns(2)
        with col_int2[0]:
            nivel = st.selectbox("Nível", options=["ALTO", "MEDIO", "BAIXO"])
        with col_int2[1]:
            mensagem = st.text_input(
                "Mensagem",
                placeholder="🔴 RISCO HEMORRÁGICO.",
            )

        if st.button("Salvar interação", type="primary"):
            if not substancia_a or not substancia_b:
                st.warning("Substância A e B são obrigatórias.")
            else:
                payload = {
                    "substancia_a": substancia_a,
                    "substancia_b": substancia_b,
                    "nivel": nivel,
                    "mensagem": mensagem,
                }
                url = f"{base_url}/api/admin/interactions"
                data = call_api("POST", url, admin_key=admin_key, payload=payload)
                if data:
                    st.success("✅ Interação criada com sucesso!")
                    st.json(data)

# ==============================
# ABA: TESTE CLÍNICO
# ==============================

with tab_clinical:
    st.subheader("Teste Rápido - /api/clinical-check")

    st.markdown("Monte um cenário simples para testar a engine clínica.")

    st.markdown("#### Dados do médico")
    cd_medico = st.text_input("Código do médico", value="MED001")

    st.markdown("#### Paciente")
    col_p1 = st.columns(2)
    with col_p1[0]:
        cd_pessoa_fisica = st.text_input("cd_pessoa_fisica", value="123")
        nm_paciente = st.text_input("Nome do paciente", value="João da Silva")
    with col_p1[1]:
        nr_atendimento = st.text_input("nr_atendimento", value="ATD001")
        weight_kg = st.number_input("Peso (kg)", min_value=0.0, value=20.0, step=0.5)

    col_p2 = st.columns(2)
    with col_p2[0]:
        age_months = st.number_input("Idade (meses)", min_value=0, value=60, step=1)
    with col_p2[1]:
        conditions_str = st.text_area(
            "Condições clínicas (lista)",
            placeholder="asma, insuficiência renal",
        )

    allergies_str = st.text_area(
        "Alergias (lista)",
        placeholder="penicilina",
    )
    current_meds_str = st.text_area(
        "Medicamentos em uso (lista)",
        placeholder="varfarina",
    )

    st.markdown("#### Item de prescrição (único para teste)")
    col_i1 = st.columns(2)
    with col_i1[0]:
        cd_item_prescricao = st.text_input("cd_item_prescricao", value="ITEM001")
        ean_codigo = st.text_input("EAN", value="0000000000000")
    with col_i1[1]:
        nm_medicamento = st.text_input("Nome do medicamento", value="Amoxicilina")

    col_i2 = st.columns(4)
    with col_i2[0]:
        dose_input = st.number_input("Dose", min_value=0.0, value=500.0, step=50.0)
    with col_i2[1]:
        dose_unidade = st.text_input("Unidade da dose", value="mg")
    with col_i2[2]:
        route = st.text_input("Via", value="Oral")
    with col_i2[3]:
        freq_hours = st.number_input("Frequência (em horas)", min_value=1, value=8, step=1)

    drug_id_item = st.text_input(
        "ID do medicamento (deve existir na base)",
        value="MED_AMOX",
    )

    if st.button("Enviar para /api/clinical-check", type="primary"):
        payload = {
            "cd_medico": cd_medico,
            "patient": {
                "cd_pessoa_fisica": cd_pessoa_fisica,
                "nm_paciente": nm_paciente,
                "nr_atendimento": nr_atendimento,
                "weight_kg": float(weight_kg),
                "age_months": int(age_months),
                "conditions": str_to_list(conditions_str),
                "allergies": str_to_list(allergies_str),
                "current_meds": str_to_list(current_meds_str),
            },
            "items": [
                {
                    "cd_item_prescricao": cd_item_prescricao,
                    "ean_codigo": ean_codigo,
                    "nm_medicamento": nm_medicamento,
                    "dose_input": float(dose_input),
                    "dose_unidade": dose_unidade,
                    "route": route,
                    "freq_hours": int(freq_hours),
                    "drug_id": drug_id_item,
                }
            ],
        }

        url = f"{base_url}/api/clinical-check"
        data = call_api("POST", url, admin_key=None, payload=payload)
        if data:
            st.success("✅ Resposta da engine clínica:")
            st.json(data)
