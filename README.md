<div align="center">
  <img src="assets/logo.png" alt="ValidRx Logo" width="250"/>
   
  ### Sistema de Inteligência e Supervisão Clínica Automatizada

  **Transformando sistemas passivos em guardiões ativos da vida.

  ![Status](https://img.shields.io/badge/Status-Enterprise_MVP-green?style=for-the-badge)
  ![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
  ![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=for-the-badge)
  ![Database](https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge)
  ![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge)
</div>

---

# 📑 Índice

- [🏥 O Problema & A Missão](#-o-problema--a-missão)
- [🔄 Arquitetura de Integração](#-arquitetura-de-integração-tasymv--validrx)
- [🛡️ As 7 Camadas de Blindagem](#️-as-7-camadas-de-blindagem)
- [⚡ Como Rodar o Projeto](#-como-rodar-o-projeto)
- [📚 Guia de Uso da API](#-guia-de-uso-da-api-exemplos-práticos)
  - [1. Cadastro de Medicamento](#1-cadastrando-um-medicamento-e-regras-admin)
  - [2. Cadastro de Interação Medicamentosa](#2-cadastrando-uma-interação-medicamentosa-admin)
  - [3. Validação de Prescrição](#3-validando-uma-prescrição-integração-tasy)
- [🤝 Como Contribuir](#-como-contribuir)
- [⚖️ Disclaimer Legal](#️-disclaimer-aviso-legal)

---

# 🏥 O Problema & A Missão

Erros de **dosagem pediátrica**, administração por **via incorreta** ou **superdosagem** estão entre as principais causas de eventos adversos graves.

Os sistemas de prontuário eletrônico (Tasy, MV, Soul) são **passivos**: aceitam o que o usuário digita sem validação clínica profunda.

O **ValidRx** muda isso:  
Ele é um **motor de decisão clínica (CDSS)** que intercepta prescrições de risco via API **antes que a receita chegue à enfermagem**.

🎯 **Objetivo:** Criar um padrão nacional de segurança aberto para o SUS.

---

# 🔄 Arquitetura de Integração (Tasy/MV + ValidRx)

O ValidRx roda **no backend**, integrado ao fluxo do hospital, sem alterar a rotina do médico.

![Diagrama de Fluxo de Dados](assets/diagrama_integracao.png)

### Fluxo:

1. Médino clica em **Salvar** no prontuário.  
2. O ValidRx recebe dados criptografados e aplica todas as regras clínicas.  
3. Se houver risco fatal → retorna **BLOCKED** impedindo o procedimento.  
4. Caso contrário → **APPROVED**.

---

# 🛡️ As 7 Camadas de Blindagem

O sistema valida cada item da prescrição passando por 7 níveis:

1. **🧪 Dose Pediátrica (mg/kg)**  
2. **🛑 Teto Absoluto**  
3. **💉 Via de Administração**  
4. **⚠️ Interações Medicamentosas**  
5. **🤧 Alergias**  
6. **🚫 Contraindicações (CID)**  
7. **🔁 Duplicidade Terapêutica**

---

# ⚡ Como Rodar o Projeto

## Pré-requisitos
- Docker  
- Docker Compose  

## Passo a passo

### 1. Clonar repositório
```bash
git clone https://github.com/seu-usuario/validrx.git
cd validrx


### 2. Iniciar ambiente Docker

``` bash
docker-compose up --build
```

A API e o banco PostgreSQL serão iniciados automaticamente.

### 3. Abrir Swagger

Acesse:

    http://localhost:8000/docs

------------------------------------------------------------------------

# 📚 Guia de Uso da API (Exemplos Práticos)

A API segue o padrão REST.

------------------------------------------------------------------------

## 1. Cadastrando um Medicamento e Regras (Admin)

**Endpoint:**

    POST /api/v1/admin/drugs

**Header obrigatório:**

    x-admin-key: VALIDRX_OPEN_SOURCE

### 📌 Exemplo --- Cadastrando Adrenalina 1mg/mL

``` json
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
```

------------------------------------------------------------------------

## 2. Cadastrando uma Interação Medicamentosa (Admin)

### Exemplo --- Varfarina + Ibuprofeno

``` json
{
  "substancia_a": "varfarina",
  "substancia_b": "ibuprofeno",
  "nivel": "ALTO",
  "mensagem": "🔴 RISCO HEMORRÁGICO: AINEs aumentam o efeito da Varfarina."
}
```

------------------------------------------------------------------------

## 3. Validando uma Prescrição (Integração Tasy)

**Endpoint principal do sistema hospitalar:**

    POST /api/v1/clinical-check

### Cenário demonstrativo

📌 *Criança de 20kg, 3ml de Adrenalina IV (erro fatal)*

### Payload

``` json
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
```

### Resposta esperada (BLOQUEIO)

``` json
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
```

------------------------------------------------------------------------

# 🤝 Como Contribuir

O ValidRx é um projeto Open Source cuja missão é **proteger vidas**. Sua
colaboração é valiosa.

## 👩‍💻 Para Desenvolvedores (Tech)

-   Integração HL7 FHIR\
-   Performance\
-   Segurança avançada

📌 Como ajudar:\
**Fork → Branch → Pull Request**

------------------------------------------------------------------------

## 👨‍⚕️ Para Profissionais de Saúde (Curadoria)

-   Revisão de limites de dose\
-   Criação de protocolos regionais

📌 Abra uma Issue com:

    [PROTOCOLO] Sugestão de Regra

------------------------------------------------------------------------

# ⚖️ Disclaimer (Aviso Legal)

O ValidRx é um **CDSS**, não substitui julgamento clínico.\
Decisões são responsabilidade exclusiva do profissional de saúde.\
Software fornecido "como está", sob licença MIT.

------------------------------------------------------------------------

::: {align="center"}
```{=html}
<p>
```
Feito com ❤️ e Código para o SUS.
```{=html}
</p>
```
:::
