<div align="center">
  <img src="assets/logo.png" alt="ValidRx Logo" width="250"/>
   
  ### Sistema de Inteligência e Supervisão Clínica Automatizada

  Transformando sistemas passivos em guardiões ativos da vida.

  ![Status](https://img.shields.io/badge/Status-Enterprise_MVP-green?style=for-the-badge)
  ![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
  ![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=for-the-badge)
  ![Database](https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge)
  ![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge)
</div>

---

# 📑 Índice

- [🏥 O Problema & A Missão](#-o-problema--a-missão)
- [🤖 O que é o ValidRX?](#-o-que-e-o-ValidRX)
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

O **ValidRx** muda isso: Ele é uma **IA de decisão clínica** que intercepta prescrições de risco via API **antes que a receita chegue à enfermagem**.

🎯 **Objetivo:** Criar um padrão nacional de segurança aberto para o SUS.

---

# 🤖 O que é o ValidRX?

O **ValidRx** é uma IA de validação em tempo real que se conecta ao Prontuário Eletrônico. Ele audita a prescrição médica antes que ela seja liberada para a farmácia ou  enfermagem. É um tipo de sistema de IA denominado de Sistema Especialista. Ele não "aprende sozinho" (**Machine Learning**) e nem "chuta" respostas baseadas em estatística (como o **ChatGPT**).  

Ele opera baseado em uma **Árvore de Decisão Lógica e Determinística**. Ele codifica o conhecimento de especialistas humanos (médicos/farmacêuticos) em regras computacionais rigorosas (**SE peso < 10kg E dose > 50mg ENTÃO Bloquear**).

O ValidRx oferece integração nativa com sistemas hospitalares, como o **Philips Tasy** (https://www.philips.com.br/healthcare/resources/landing/solucao-tasy), através de uma API REST robusta e pronta para uso.
Para garantir uma implementação ágil e sem fricção, nossos endpoints consomem payloads JSON estruturados rigorosamente conforme o padrão de dados do Tasy. Isso permite uma conexão plug-and-play, onde o ValidRx valida prescrições em tempo real aproveitando a estrutura de dados que o seu prontuário já gera.

---



# 🔄 Arquitetura de Integração (Tasy + ValidRx)

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
- Docker Desktop 
- Docker Compose  

## Passo a passo

### 1. Clonar repositório
```bash
https://github.com/prof-fabiosantos/ValidRx_Project.git
cd ValidRx_Project
```
### 2. Iniciar ambiente Docker

Na primeira vez ou quando houver alguma alteração no código use:
``` bash
docker-compose up --build
```
Se não houver nenhuma alteração no código use:
```bash
docker compose up
```

A API e o banco PostgreSQL serão iniciados automaticamente.

### 3. Abrir Swagger

Acesse:

    http://localhost:8000/docs

------------------------------------------------------------------------

# 📚 Guia de Uso da API (Exemplos Práticos)

A API segue o padrão REST.

------------------------------------------------------------------------

🔐 Autenticação Admin

Todos os endpoints administrativos exigem:
x-admin-key: ADMIN_SECRET_KEY

A chave é configurada no .env:
ADMIN_SECRET_KEY=MEUSEGREDO123

------------------------------------------------------------------------

## 1. Cadastrando um Medicamento e Regras (Admin)

**Endpoint:**

    POST /api/admin/drugs

**Header obrigatório:**

    x-admin-key: MEUSEGREDO123

### 📌 Exemplo --- Cadastrando Adrenalina 1mg/mL

``` json
{
  "id": "ADRE_1MG",
  "nome": "Adrenalina 1mg/mL",
  "principio_ativo": "Epinefrina",
  "classe_terapeutica": "Vasopressor",
  "familias_alergia": [],
  "concentracao_mg_ml": 1,
  "min_idade_meses": 0,
  "dose_max_diaria_adulto_mg": 1,
  "contra_indicacoes": [],
  "vias_permitidas": ["Endovenosa (IV)", "Intramuscular (IM)"],
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

**Endpoint:**

    POST /api/admin/interactions

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

    POST /api/clinical-check

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
    "current_meds": []
  },
  "items": [
    {
      "cd_item_prescricao": "1",
      "ean_codigo": "789123456001",
      "nm_medicamento": "Adrenalina 1mg/mL",
      "dose_input": 3.0,
      "dose_unidade": "ml",
      "route": "Endovenosa (IV)",
      "freq_hours": 24,
      "drug_id": "ADRE_1MG"
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

🖥️ Painel Administrativo (App em Streamlit)

O ValidRx agora inclui um Painel Administrativo desenvolvido em Streamlit, projetado para facilitar a gestão completa do sistema sem necessidade de acessar o banco de dados manualmente ou manipular arquivos diretamente.

![Painel](assets/painel.png)

Esse painel fornece uma interface simples, visual e organizada para administradores atualizarem informações críticas de forma segura.

✨ Principais Funcionalidades:

- Gerenciamento de Medicamentos
  - Listar todos os medicamentos cadastrados
  - Adicionar novos medicamentos
  - Editar informações existentes
  - Excluir entradas incorretas ou desatualizadas

- Visualização das Regras de Validação
- Acessar as regras armazenadas no motor de validação

🔐 Acesso Restrito ao Administrador

Todas as operações do painel são protegidas por autenticação básica.
Somente usuários autorizados (admin) podem visualizar e modificar os dados.


🚀 Como Executar o Painel

1. No mesmo projeto (ou em outro diretório com acesso à API):
```bash
python -m venv venv
.\venv\Scripts\activate   
pip install streamlit requests
 ```
Garante que streamlit e requests estejam instalados (ou adicionados ao seu requirements.txt).

2. Com a API rodando (Docker validrx-api + validrx-db funcionando), execute:
```bash
  .\venv\Scripts\activate
  streamlit run validrx_admin_app
```

📌 Observação

O painel funciona integrado com a API FastAPI e depende do PostgreSQL configurado no Docker Compose.
Ele é a maneira recomendada de manter o ValidRx sempre atualizado, seguro e alinhado à prática clínica.

------------------------------------------------------------------------

# 🤝 Como Contribuir

O **ValidRx** é um projeto Open Source cuja missão é **proteger vidas**. Sua
colaboração é valiosa.

## 👩‍💻 Para Desenvolvedores (Tech)

O **ValidRx** é um projeto vivo e precisamos de ajuda em diversas frentes para torná-lo o padrão de segurança do SUS. Escolha sua área de expertise e junte-se a nós:

- 🔌 Interoperabilidade & Padrões: Criação de adaptadores para HL7 FHIR e TISS/TUSS, permitindo que o **ValidRx** "converse" nativamente com grandes prontuários (Epic, Tasy, MV).
- 🗄️ Engenharia de Dados (ETL): Desenvolvimento de scrapers e scripts para atualizar automaticamente a base de medicamentos com dados da ANVISA/CMED e mapeamento de códigos EAN/GTIN.
- ⚡ Performance & DevOps: Implementação de cache (Redis) para validações de alta frequência, testes de carga e anonimização de logs para conformidade total com a LGPD.
- 🎨 Frontend (Backoffice): Evolução do painel administrativo (atualmente em Streamlit) para interfaces mais robustas (React/Vue.js), facilitando a gestão de regras por farmacêuticos.
- 🧪 QA & Testes Clínicos: Criação de testes unitários e cenários de "pacientes virtuais" (CI/CD) para garantir que novas regras não quebrem a lógica de segurança crítica.

📌 Como ajudar:
**Fork → Branch → Pull Request**

------------------------------------------------------------------------

## 👨‍⚕️ Para Profissionais de Saúde (Curadoria)

Os médicos desempenham um papel essencial no aprimoramento do **ValidRx**. Eles ajudam a garantir que o sistema seja seguro, confiável e alinhado à prática clínica real. Entre as principais formas de contribuição:

- Revisão clínica das regras
  Atualizam contraindicações, doses, interações e diretrizes conforme a prática médica.

- Curadoria da base de medicamentos
  Adicionam, corrigem e validam informações essenciais sobre tratamentos.

- Validação de respostas (human-in-the-loop)
  Avaliam as classificações de risco e justificativas geradas pela IA.

- Testes em cenários clínicos simulados
  Identificam falsos positivos/negativos e possíveis riscos não previstos.

- Criação de casos para treinamento
  Fornecem prescrições corretas/incorretas e explicações clínicas estruturadas.

- Auditoria de segurança e ética
  Ajudam a detectar recomendações inseguras ou inconsistências do motor de validação.

- Feedback contínuo
  Reportam melhorias necessárias diretamente baseadas na prática.

A colaboração médica garante que o ValidRx evolua de forma responsável, com alto rigor clínico e foco em segurança ao paciente.

------------------------------------------------------------------------

# 💬  Discord

https://discord.gg/HkFJFCt2

------------------------------------------------------------------------

# ⚖️ Disclaimer (Aviso Legal)
O ValidRx é um CDSS — ferramenta de apoio à decisão clínica.

Não substitui julgamento clínico.
Responsabilidade final da prescrição é do médico.
Recomenda-se revisão contínua das regras pela farmácia clínica.



