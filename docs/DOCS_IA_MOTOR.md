# 🧠 Arquitetura do Motor de Decisão ValidRx

## 1. Visão Geral: Sistema Especialista Determinístico

O ValidRx não utiliza redes neurais ou modelos probabilísticos ("caixa preta" ou IA Generativa). Ele é arquitetado como um **Sistema Especialista Baseado em Regras (Rule-Based Expert System)**.

A filosofia central do sistema é a separação total entre **Lógica** e **Conhecimento**:

1.  **O Motor (Lógica Fixa):** O código Python (`src/engine.py`) que define *como* as verificações são feitas. É a estrutura da "Árvore de Decisão".
2.  **A Base de Conhecimento (Dados Dinâmicos):** O Banco de Dados (`PostgreSQL`) que define *quais* são os limites e parâmetros. É o "Combustível" do motor.

> **Conceito Chave:** Nós não alteramos o código para mudar uma dose máxima. Nós alteramos o dado no banco, e o código se adapta instantaneamente. Isso garante 100% de previsibilidade e auditabilidade.

---

## 2. Persistência de Regras (`src/database.py`)

O conhecimento médico é armazenado no PostgreSQL utilizando o ORM **SQLAlchemy**. As regras clínicas não são *hardcoded* (escritas no código); elas são propriedades de objetos no banco.

### Estrutura de Dados (Models)
No arquivo `src/database.py`, definimos como o conhecimento é estruturado e consumido pelo motor:

```python
class Medicamento(Base):
    __tablename__ = "medicamentos"
    
    # Identificação Única
    id = Column(String, primary_key=True)  # ex: "MED_ADRE"
    
    # Regras de Segurança Gerais (Parametrização)
    # O motor consulta essas listas para validar a entrada
    vias_permitidas = Column(JSON)         # ex: ["Intramuscular", "Subcutânea"]
    contra_indicacoes = Column(JSON)       # ex: ["dengue", "insuficiencia_renal"]
    familias_alergia = Column(JSON)        # ex: ["aines", "penicilina"]
    
    # Relacionamento com Regra Pediátrica (A Matemática)
    pediatria = relationship("Pediatria", uselist=False, ...)

class Pediatria(Base):
    # Parâmetros para o cálculo de dose
    modo = Column(String)     # 'mg_kg_dose' ou 'mg_kg_dia'
    min = Column(Float)       # ex: 0.01
    max = Column(Float)       # ex: 0.01
    teto_dose = Column(Float) # ex: 0.5 (O Freio de Emergência)
```

---

## 3. O Motor de Inferência (`src/engine.py`)

Este é o coração do sistema. Ele implementa a **Árvore de Decisão** através de uma sequência hierárquica de condicionais (`if/elif/else`).

O motor recebe o contexto (Paciente + Prescrição) e carrega as regras do banco para executar a validação.

### A Implementação da Árvore
Trecho simplificado do método `validate()` em `src/engine.py`:

```python
def validate(self, patient, prescription):
    # 1. Carregamento de Dados (Obtenção das Regras)
    # O motor busca no banco as regras específicas para O REMÉDIO solicitado.
    drug = self.drugs.get(prescription['drug_id'])
    
    # 2. Execução da Árvore de Decisão (Camada a Camada)
    
    # --- NÓ 1: Decisão de Via ---
    # Pergunta: A rota pedida está na lista permitida pelo banco?
    if route not in drug['vias_permitidas']:
        alerts.append(f"⛔ ERRO DE VIA: {drug['nome']} permite apenas {drug['vias_permitidas']}.") 

    # --- NÓ 2: Decisão de Contexto Clínico (Exceção de Alta Complexidade) ---
    # Pergunta: É Adrenalina IV sem PCR?
    if "Adrenalina" in drug['nome'] and route == "Endovenosa (IV)" and "parada_cardiaca" not in conditions:
         alerts.append("⛔ ERRO FATAL: Adrenalina IV só permitida em Parada Cardíaca (PCR).")

    # --- NÓ 3: Decisão Matemática (Posologia) ---
    if is_child and ped_rule:
        # O motor usa os parâmetros DO BANCO para fazer a conta
        val_calculado = dose_input * concentracao
        teto_banco = ped_rule['teto_dose']
        
        # O Teste Lógico Determinístico
        # Verifica primeiro o Teto Absoluto (Segurança Máxima)
        if val_calculado > teto_banco:
            alerts.append(f"⛔ TETO ABSOLUTO EXCEDIDO: {val_calculado}mg > {teto_banco}mg")
        
        # Verifica a faixa terapêutica (Peso)
        elif val_calculado > max_dose_peso:
            alerts.append(f"⛔ SOBREDOSE TÓXICA: {val_calculado}mg > {max_dose_peso}mg")
```

---

## 4. Exemplo de Execução (Trace)

Vamos rastrear o processamento do sistema no momento exato em que um médico tenta cometer o erro da **Adrenalina (3ml, IV)** em uma criança de 20kg.

### Cenário de Entrada
*   **Paciente:** 20kg, 6 anos. Condição: "Tosse".
*   **Prescrição:** Adrenalina, 3ml, Endovenosa (IV).

### Passo 1: A Chamada da API (`src/api.py`)
O sistema hospitalar envia o JSON. A API normaliza os dados (ex: converte a sigla "EV" do MV para "Endovenosa (IV)") e chama o motor.

### Passo 2: O Carregamento de Regras (Memory Fetch)
O Motor pega o ID `MED_ADRE` e carrega os parâmetros da memória/banco.
**O que ele encontra (Dados):**
*   `vias_permitidas`: `["Intramuscular", "Endovenosa (IV)", "Subcutânea"]`
*   `teto_dose`: `0.5`
*   `concentracao`: `1.0`

### Passo 3: A Travessia da Árvore (Processamento Lógico)

1.  **Nó de Via (Lista):**
    *   *Teste:* "Endovenosa (IV)" está em `["Intramuscular", "Endovenosa (IV)", ...]`?
    *   *Resultado:* **VERDADEIRO**. (A via existe tecnicamente, o código avança).

2.  **Nó de Contexto (Regra Específica):**
    *   *Teste:* É Adrenalina? (Sim) **E** É IV? (Sim) **E** NÃO tem PCR? (Sim, paciente só tem tosse).
    *   *Resultado:* **VERDADEIRO** para Erro.
    *   *Ação:* Adiciona alerta na lista: **"⛔ ERRO FATAL: Adrenalina IV só em PCR."**

3.  **Nó de Posologia (Matemática):**
    *   *Cálculo:* 3ml * 1mg/ml = **3.0 mg**.
    *   *Teste:* `3.0 mg` (Dose Solicitada) > `0.5 mg` (Teto do Banco)?
    *   *Resultado:* **VERDADEIRO**.
    *   *Ação:* Adiciona alerta na lista: **"⛔ TETO ABSOLUTO EXCEDIDO: 3.0mg > 0.5mg"**.

### Passo 4: O Retorno
O motor devolve a lista de alertas para a API, que responde ao hospital com **Status: BLOCKED**, impedindo a impressão da receita.

---

## 5. Divisão de Responsabilidades

Para manter o sistema seguro e atualizado:

*   **👨‍⚕️ Profissionais de Saúde (Dados):** Seu papel é definir os **Parâmetros**. Vocês dizem qual é o valor de `teto_dose` e o que vai em `vias_permitidas` usando o Painel Administrativo ou API de Admin. O motor obedecerá cegamente o que vocês cadastrarem.
*   **💻 Desenvolvedores (Lógica):** Seu papel é aprimorar a **Árvore**. Vocês criam novos "Nós" de decisão no código (ex: criar uma verificação nova para função renal) e otimizam a performance e segurança da API.


