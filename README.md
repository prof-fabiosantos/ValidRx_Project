<div align="center">
  <img src="assets/logo.png" alt="ValidRx Logo" width="250"/>
  <h1>ValidRx</h1>
  <h3>Sistema de Inteligência e Supervisão Clínica Automatizada</h3>
  
  <p>
    Do Luto ao Legado: Transformando sistemas passivos em guardiões ativos da vida.
  </p>

  ![Status](https://img.shields.io/badge/Status-Enterprise_MVP-green?style=for-the-badge)
  ![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
  ![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=for-the-badge)
  ![Database](https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge)
  ![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge)
</div>

<br />

## 🏥 O Problema & A Missão
Erros de dosagem pediátrica e administração de medicamentos por vias incorretas são causas frequentes de eventos adversos graves e fatais. Sistemas hospitalares tradicionais (EMRs) são frequentemente passivos, aceitando qualquer dado inserido pelo médico sem crítica clínica.

O **ValidRx** atua como uma **Barreira de Segurança Ativa**. Ele é um motor lógico (CDSS) que intercepta prescrições perigosas via API, validando matematicamente cada item antes que ele chegue à enfermagem ou ao paciente.

**Nosso objetivo:** Criar um padrão de segurança acessível para a saúde pública brasileira (SUS).

---

## 🔄 Arquitetura de Integração (Tasy/MV + ValidRx)
O ValidRx não é um "software extra" que o médico precisa abrir. Ele roda integrado ao fluxo de trabalho do hospital via API REST.

![Diagrama de Fluxo de Dados](assets/diagrama_integracao.png)

1.  **Ação no Prontuário:** O médico clica em "Salvar" no Tasy/MV.
2.  **Validação na Nuvem:** O ValidRx recebe os dados criptografados e processa as regras em milissegundos.
3.  **Resposta:** Se houver risco fatal, o ValidRx retorna um **BLOQUEIO** que impede a impressão da receita.

---

## 🚀 As 7 Camadas de Blindagem
Nosso motor audita cada linha da prescrição baseando-se em protocolos rígidos:

1.  **🧪 Dose Pediátrica (mg/kg):** Cálculo automático e detecção de sobredose/subdose baseada no peso.
2.  **🛑 Teto Absoluto:** Limite máximo de segurança independente do peso (Freio de Emergência para erros de diluição).
3.  **💉 Via de Administração:** Bloqueio de vias incompatíveis (Ex: *Adrenalina IV* em paciente sem Parada Cardíaca).
4.  **⚠️ Interações:** Checagem cruzada com medicamentos de uso contínuo.
5.  **🤧 Alergias:** Detecção de sensibilidade a princípios ativos e famílias químicas.
6.  **🚫 Contraindicações:** Validação baseada em Condições Clínicas/CID.
7.  **🔄 Duplicidade:** Alerta de redundância terapêutica desnecessária.

---

## ⚡ Como Rodar o Projeto

A maneira recomendada é utilizando **Docker**, que sobe a API (FastAPI) e o Banco de Dados (PostgreSQL) automaticamente.

### Pré-requisitos
*   Docker e Docker Compose instalados.

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/validrx.git
    cd validrx
    ```

2.  **Inicie o ambiente:**
    ```bash
    docker-compose up --build
    ```
    *O sistema iniciará automaticamente a API e criará as tabelas no banco de dados.*

3.  **Acesse a Documentação (Swagger UI):**
    Abra seu navegador em: `http://localhost:8000/docs`

---

## 📚 Guia de Uso da API (Exemplos Práticos)

O ValidRx segue o padrão REST. Abaixo estão os payloads exatos para cadastrar regras e validar prescrições.

### 1. Cadastrando um Medicamento e Regras (Admin)
Utilizado pela equipe de farmácia clínica para ensinar ao sistema os parâmetros de segurança de uma droga.

*   **Endpoint:** `POST /api/v1/admin/drugs`
*   **Header:** `x-admin-key: VALIDRX_OPEN_SOURCE` *(Configurável no .env)*

**Exemplo: Cadastrando a Adrenalina (Regras Rígidas)**
```json
{
  "id": "MED_ADRE",
  "nome": "Adrenalina 1mg/mL",
  "principio_ativo": "epinefrina",
  "classe_terapeutica": "vasopressor",
  "familias_alergia": [],
  "concentracao_mg_ml": 1.0,
  "min_idade_meses": 0,
  "dose_max_diaria_adulto_mg": 1.0,
  "contra_indicacoes": [],
  "vias_permitidas": [
    "Intramuscular (IM)",
    "Endovenosa (IV)",
    "Subcutânea"
  ],
  "pediatria": {
    "modo": "mg_kg_dose",
    "min": 0.01,
    "max": 0.01,
    "teto_dose": 0.5
  }
}

### 2. Cadastrando uma Interação Medicamentosa (Admin)

{
  "substancia_a": "varfarina",
  "substancia_b": "ibuprofeno",
  "nivel": "ALTO",
  "mensagem": "🔴 RISCO HEMORRÁGICO: AINEs aumentam o efeito da Varfarina."
}

### 3. Validando uma Prescrição (Integração Tasy)

Este é o endpoint principal chamado pelo sistema hospitalar. Ele aceita dados do paciente e uma lista de medicamentos.
Endpoint: POST /api/v1/clinical-check
Exemplo de Payload (Simulando Erro Fatal):
Cenário: Criança de 20kg, prescrição de 3ml de Adrenalina IV.

{
  "cd_medico": "CRM-12345",
  "patient": {
    "cd_pessoa_fisica": "PAC-9988",
    "nm_paciente": "João da Silva",
    "nr_atendimento": "AT-100",
    "weight_kg": 20.0,
    "age_months": 72,
    "conditions": ["tosse seca"],
    "allergies": [],
    "current_meds_eans": []
  },
  "items": [
    {
      "cd_item_prescricao": "1",
      "ean_codigo": "789123456001",
      "nm_medicamento": "Adrenalina 1mg/mL",
      "dose_valor": 3.0,
      "dose_unidade": "ml",
      "via_administracao": "Endovenosa (IV)",
      "frequencia_horas": 24
    }
  ]
}

Exemplo de Resposta (Bloqueio):

{
  "status": "BLOCKED",
  "message": "⛔ A prescrição contém erros bloqueantes de segurança.",
  "alerts": [
    {
      "type": "BLOCK",
      "msg": "[Adrenalina 1mg/mL]: ⛔ ERRO FATAL: Adrenalina IV só em PCR."
    },
    {
      "type": "BLOCK",
      "msg": "[Adrenalina 1mg/mL]: ⛔ TETO ABSOLUTO EXCEDIDO: 3.0mg > 0.5mg."
    }
  ]
}

---

## 🤝 Como Contribuir
O ValidRx é um projeto Open Source nascido da necessidade de proteger vidas. Sua ajuda é fundamental.
👩‍💻 Para Desenvolvedores (Tech)
Integração: Implementar suporte nativo a HL7 FHIR.
Performance: Otimizar o tempo de resposta da API para grandes volumes.
Segurança: Melhorar a autenticação e criptografia de dados sensíveis.
Como ajudar: Faça um Fork, crie uma Branch (feature/nova-funcionalidade) e envie um Pull Request.
👨‍⚕️ Para Profissionais de Saúde (Curadoria)
Precisamos da sua expertise clínica para validar o "cérebro" do sistema:
Validação de Regras: Revisar os limites de dose pediátrica.
Protocolos Regionais: Ajudar a cadastrar regras para endemias (Dengue, Malária, etc).
Como ajudar: Abra uma Issue no GitHub com o título [PROTOCOLO] Sugestão de Regra descrevendo o medicamento e os limites de segurança.
---
⚖️ Disclaimer (Aviso Legal)
O ValidRx é uma ferramenta de Apoio à Decisão Clínica (CDSS).
Suporte, não Substituição: Este software foi projetado para auxiliar profissionais de saúde na detecção de erros matemáticos e procedimentais, mas não substitui o julgamento clínico profissional.
Responsabilidade: A decisão final sobre qualquer prescrição, dispensação ou administração de tratamento é de responsabilidade exclusiva do médico ou profissional de saúde licenciado.
Garantias: O software é fornecido "como está", sob a licença MIT, sem garantias de qualquer tipo quanto à sua precisão para casos clínicos específicos. Recomenda-se a validação constante das regras cadastradas pela equipe de farmácia clínica da instituição.
