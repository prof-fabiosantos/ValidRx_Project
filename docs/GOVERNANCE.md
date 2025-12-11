# 🏛️ Modelo de Governança e Desenvolvimento ValidRx

> **"Centralização da Visão, Descentralização da Execução."**

---

## 1. A Filosofia: O "Linux" da Segurança Clínica

Para que este projeto escale, seja validado e possa ser usado em hospitais, estamos adotando o modelo de desenvolvimento similar ao modelo do Kernel do Linux.

Não somos uma **"Catedral"** (onde um pequeno grupo constrói tudo fechado), somos um **"Bazar"** (onde a comunidade constrói junto), mas com uma camada rigorosa de curadoria, pois lidamos com vidas humanas.

### 🎯 Objetivo Estratégico

Evitar o gargalo central, permitindo que a inovação aconteça nas pontas (hospitais, universidades, devs autônomos), mantendo o núcleo (**ValidRx Core**) estável e seguro.

---

## 2. Papéis (Quem faz o quê?)

Para garantir qualidade **sem centralização excessiva**, definimos os seguintes papéis:

### 👑 BDFL (Benevolent Dictator For Life) – Líder Estratégico

- **Quem:** Fábio (Fundador).  
- **Papel:**  
  - Define a visão de longo prazo  
  - Define a arquitetura macro  
  - Tem o "Voto de Minerva" em impasses éticos ou técnicos  
  - Não escreve todo o código; aprova a direção

---

### 🛡️ Core Maintainers (Os "Tenentes")

- **Quem:** Um grupo restrito e confiável (2 a 4 pessoas) com permissão de *merge* no repositório oficial.
- **Papéis:**  
  - **Tech Lead:** Responsável por revisar código Python, segurança da API e performance.  
  - **Clinical Lead:** Responsável por revisar JSONs de regras médicas. Nada entra no banco de dados sem o "De Acordo" deste profissional.  
- **Papel:** São os guardiões da qualidade. Filtram o ruído antes que chegue ao BDFL.

---

### 👷 Contributors (A Comunidade)

- **Quem:** Qualquer desenvolvedor, médico ou estudante.  
- **Papel:** Enviam melhorias, correções e novas regras via **Pull Request (PR)**.

---

## 3. O Fluxo de Trabalho (Workflow)

Ninguém *comita* direto na branch principal (`main`). O fluxo de contribuição é padronizado:

1. **Fork**  
   O colaborador cria uma cópia do ValidRx para ele.

2. **Branch**  
   Desenvolve a solução (ex: "Regra para Malária" ou "Otimização do Docker").

3. **Pull Request (PR)**  
   Envia o código para análise.

4. **Automação (CI/CD)**  
   - Antes de qualquer humano olhar, robôs (**GitHub Actions**) testam o código.  
   - **Quebrou a regra da Adrenalina?** ❌ Rejeitado automaticamente.  
   - **Passou nos testes?** ✅ Vai para revisão humana.

5. **Code Review**  
   - Um **Maintainer** revisa.
   - Se aprovado, entra no **ValidRx Oficial**.

---

## 4. O Ecossistema de "Distribuições" (Distros)

Assim como o Linux tem o Ubuntu, o Debian e o RedHat, o ValidRx permite derivações para realidades locais, mantendo o núcleo comum.

### 🧠 ValidRx Core (Upstream)

A versão **"pura"**, mantida por nós.  
Contém as regras universais:
- Adrenalina  
- Insulina  
- Interações graves

### 🌎 ValidRx "Distros" (Downstream)

- **ValidRx SUS-AM**  
  Versão mantida pela Secretaria de Saúde ou Universidade local, que adiciona regras específicas para doenças tropicais.

- **ValidRx Rede Privada**  
  Versão customizada por uma rede de hospitais com o formulário de medicamentos próprio.

### ✅ Vantagem

Nós mantemos o **motor**.  
As pontas mantêm as **regras específicas**.  

Isso retira a carga de suporte customizado das costas do time principal e permite:
- Adaptação local sem fragmentar o núcleo de segurança
- Escala com curadoria central

---

## 5. Chamado à Liderança

Para que este modelo funcione, estamos buscando nossos **Maintainers**.

Não precisamos apenas de **mãos para codar**. Precisamos de:

- **Líderes Técnicos** que queiram garantir a robustez da arquitetura.  
- **Líderes Clínicos** que queiram assinar a responsabilidade pelas regras de segurança.

Se você quer ser um **guardião deste projeto**, dê um passo à frente. 🚀

---

Documento baseado nas práticas de governança da **Apache Software Foundation** e do **Linux Kernel Development**.
