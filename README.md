# Documento de Visão

**Projeto:** IFAL Projetos — Gestão de Projetos Acadêmicos

| Campo        | Descrição                                  |
|--------------|--------------------------------------------|
| Versão       | 1.0                                        |
| Data         | Abril de 2026                              |
| Status       | Em Revisão                                 |
| Metodologia  | RUP — Fase de Elaboração, Iteração 1       |

---

## Sumário

- [Documento de Visão](#documento-de-visão)
  - [Sumário](#sumário)
  - [1. Introdução](#1-introdução)
    - [1.1 Propósito](#11-propósito)
    - [1.2 Escopo](#12-escopo)
    - [1.3 Definições, Acrônimos e Abreviações](#13-definições-acrônimos-e-abreviações)
    - [1.4 Visão Geral do Documento](#14-visão-geral-do-documento)
  - [2. Posicionamento](#2-posicionamento)
    - [2.1 Oportunidade de Negócio](#21-oportunidade-de-negócio)
    - [2.2 Declaração do Problema](#22-declaração-do-problema)
    - [2.3 Declaração de Posição do Produto](#23-declaração-de-posição-do-produto)
  - [3. Partes Interessadas e Usuários](#3-partes-interessadas-e-usuários)
    - [3.1 Partes Interessadas (Stakeholders)](#31-partes-interessadas-stakeholders)
    - [3.2 Perfis de Usuários](#32-perfis-de-usuários)
      - [3.2.1 Administrador do Sistema](#321-administrador-do-sistema)
      - [3.2.2 Coordenador de Curso](#322-coordenador-de-curso)
      - [3.2.3 Professor Orientador](#323-professor-orientador)
      - [3.2.4 Aluno](#324-aluno)
  - [4. Visão Geral do Produto](#4-visão-geral-do-produto)
    - [4.1 Perspectiva do Produto](#41-perspectiva-do-produto)
    - [4.2 Principais Funções](#42-principais-funções)
    - [4.3 Suposições e Dependências](#43-suposições-e-dependências)
  - [5. Requisitos Funcionais](#5-requisitos-funcionais)
  - [6. Requisitos Não Funcionais](#6-requisitos-não-funcionais)
  - [7. Restrições, Dependências e Precedências](#7-restrições-dependências-e-precedências)
    - [7.1 Restrições](#71-restrições)
    - [7.2 Dependências](#72-dependências)
    - [7.3 Riscos Identificados](#73-riscos-identificados)

---

## 1. Introdução

### 1.1 Propósito

Este documento define a visão de alto nível do **IFAL Projetos**, uma plataforma de gestão de projetos integradores e Trabalhos de Conclusão de Curso (TCC). Descreve os problemas a serem resolvidos, as necessidades das partes interessadas, as características do produto e os requisitos do sistema. Serve como base para alinhar a equipe de desenvolvimento e os stakeholders durante todas as fases do projeto.

### 1.2 Escopo

O IFAL Projetos abrange os seguintes processos institucionais:

- Criação e gerenciamento de projetos com definição de equipe
- Controle de tarefas e prazos via quadro Kanban
- Controle de versões de entregas e documentos
- Integração com repositórios Git (link de repositórios externos)
- Geração automática de relatórios de progresso com apoio de IA
- Controle de acesso baseado em perfis (aluno, orientador, coordenador)

**Fora do escopo (versão 1.0):**

- Portal de pagamento de taxas acadêmicas
- Integração nativa com GitHub/GitLab via API (somente link externo)
- Aplicativo móvel
- Integração com sistemas externos (SUAP, MEC)

### 1.3 Definições, Acrônimos e Abreviações

| Termo       | Definição                                                                          |
|-------------|------------------------------------------------------------------------------------|
| RUP         | Rational Unified Process — metodologia de desenvolvimento de software              |
| UC          | Use Case (Caso de Uso)                                                             |
| RF          | Requisito Funcional                                                                |
| RNF         | Requisito Não Funcional                                                            |
| TCC         | Trabalho de Conclusão de Curso                                                     |
| Projeto     | Agrupamento de tarefas, entregas e membros com objetivo acadêmico definido         |
| Kanban      | Metodologia visual de gestão de tarefas por colunas de status                     |
| Entrega     | Artefato ou documento submetido por uma equipe em uma etapa do projeto             |
| Orientador  | Professor responsável por acompanhar e avaliar um projeto                          |
| IA          | Inteligência Artificial — usada para geração automática de relatórios              |
| Admin       | Administrador do sistema                                                           |

### 1.4 Visão Geral do Documento

Este documento está organizado nas seguintes seções: posicionamento do produto, partes interessadas, visão geral do produto, requisitos funcionais, requisitos não funcionais e restrições.

---

## 2. Posicionamento

### 2.1 Oportunidade de Negócio

Instituições de ensino como o IFAL enfrentam dificuldades no acompanhamento e organização de projetos acadêmicos de longa duração, como projetos integradores e TCCs. A ausência de uma ferramenta centralizada gera desorganização, perda de prazos, dificuldade de comunicação entre alunos e orientadores e baixa rastreabilidade das entregas. Uma plataforma dedicada representa uma oportunidade de elevar a qualidade e a taxa de conclusão desses projetos.

### 2.2 Declaração do Problema

| Elemento                          | Descrição                                                                                                                      |
|-----------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| **O problema de**                 | Falta de organização e acompanhamento estruturado em projetos acadêmicos longos                                               |
| **Afeta**                         | Alunos, professores orientadores e coordenação de curso                                                                       |
| **Cujo impacto é**                | Perda de prazos, retrabalho, comunicação descentralizada e dificuldade de avaliação do progresso                              |
| **Uma solução bem-sucedida seria**| Uma plataforma integrada que centralize a gestão de projetos, tarefas, entregas e relatórios com rastreabilidade completa      |

### 2.3 Declaração de Posição do Produto

| Elemento               | Descrição                                                                                                                                    |
|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| **Para**               | Instituições de ensino médio e superior, especialmente o IFAL                                                                               |
| **Que**                | Necessitam organizar e acompanhar projetos integradores e TCCs de forma centralizada                                                         |
| **O IFAL Projetos é**  | Uma plataforma web de gestão de projetos acadêmicos                                                                                         |
| **Que oferece**        | Criação de projetos com equipe, Kanban de tarefas, controle de versões de entregas, integração com Git e geração automática de relatórios com IA |
| **Diferente de**       | Planilhas, grupos de mensagens e ferramentas genéricas não adaptadas ao contexto acadêmico                                                   |
| **Nosso produto garante** | Rastreabilidade completa, controle de acesso por perfil e visibilidade do progresso em tempo real                                         |

---

## 3. Partes Interessadas e Usuários

### 3.1 Partes Interessadas (Stakeholders)

| Stakeholder              | Papel             | Interesse                                                         |
|--------------------------|-------------------|-------------------------------------------------------------------|
| Direção / Reitoria       | Patrocinador      | Melhoria de indicadores acadêmicos e conformidade institucional   |
| Coordenação de Curso     | Usuário/Aprovador | Acompanhamento dos projetos e gestão de orientadores              |
| Professores Orientadores | Usuário Principal | Acompanhamento e avaliação dos projetos sob sua responsabilidade  |
| Alunos                   | Usuário Final     | Gestão de tarefas, envio de entregas e comunicação com orientador |
| Equipe de TI / IFAL      | Suporte           | Manutenção, segurança e infraestrutura da plataforma              |

### 3.2 Perfis de Usuários

#### 3.2.1 Administrador do Sistema

| Atributo             | Descrição                                               |
|----------------------|---------------------------------------------------------|
| Representante        | Equipe de TI do IFAL                                   |
| Responsabilidade     | Configuração, manutenção e controle de acesso ao sistema |
| Critério de sucesso  | Sistema estável, com auditoria e backup funcionais      |
| Nível técnico        | Alto                                                    |

#### 3.2.2 Coordenador de Curso

| Atributo             | Descrição                                                               |
|----------------------|-------------------------------------------------------------------------|
| Representante        | Coordenadores de graduação e pós-graduação                             |
| Responsabilidade     | Supervisão dos projetos, alocação de orientadores e emissão de relatórios |
| Critério de sucesso  | Visibilidade completa do progresso dos projetos e desempenho das equipes |
| Nível técnico        | Médio                                                                   |

#### 3.2.3 Professor Orientador

| Atributo             | Descrição                                                               |
|----------------------|-------------------------------------------------------------------------|
| Representante        | Docentes com projetos sob orientação                                    |
| Responsabilidade     | Acompanhamento de tarefas, avaliação de entregas e feedback às equipes  |
| Critério de sucesso  | Interface simples para revisão de entregas e comunicação com alunos     |
| Nível técnico        | Baixo a médio                                                           |

#### 3.2.4 Aluno

| Atributo             | Descrição                                                                                    |
|----------------------|----------------------------------------------------------------------------------------------|
| Representante        | Discentes matriculados em disciplinas de projeto ou TCC                                      |
| Responsabilidade     | Criação de tarefas, envio de entregas, vinculação de repositório Git e consulta de feedbacks |
| Critério de sucesso  | Acesso ágil, visual e intuitivo para gerir as etapas do próprio projeto                      |
| Nível técnico        | Baixo a médio                                                                                |

---

## 4. Visão Geral do Produto

### 4.1 Perspectiva do Produto

O IFAL Projetos é uma aplicação web stand-alone que, na fase inicial, integra-se ao servidor de e-mail institucional para envio de notificações e permite vinculação de repositórios Git externos (GitHub, GitLab) via URL. Futuras versões poderão incluir integração direta com APIs de plataformas de versionamento e sistemas institucionais como o SUAP.

Os principais atores (Aluno, Orientador, Coordenador e Admin) interagem com a aplicação web, que persiste dados em banco relacional e envia notificações via servidor SMTP institucional.

```
Aluno ──────────────┐
Professor Orientador ┤
Secretária ──────────┼──► Sistema IFAL Projetos (Web) ──► Banco de Dados
Coordenador ─────────┤                                └──► Servidor de E-mail
Admin ───────────────┘
```

### 4.2 Principais Funções

| ID  | Função                                                                      | Prioridade |
|-----|-----------------------------------------------------------------------------|------------|
| F01 | Gestão de projetos (criação, edição, encerramento) com definição de equipe  | Alta       |
| F02 | Quadro Kanban com tarefas, responsáveis, prazos e status                    | Alta       |
| F03 | Controle de versões de entregas (upload, histórico, download)               | Alta       |
| F04 | Vinculação de repositórios Git externos por projeto                         | Alta       |
| F05 | Controle de acesso baseado em perfis                                        | Alta       |
| F06 | Geração automática de relatórios de progresso com apoio de IA               | Média      |
| F07 | Notificações por e-mail em eventos relevantes                               | Baixa      |

### 4.3 Suposições e Dependências

- A instituição dispõe de infraestrutura de servidor web e banco de dados relacional
- Os usuários possuem acesso à internet e navegador moderno
- Existe um servidor SMTP institucional para envio de e-mails
- O sistema operará em ambiente seguro com HTTPS
- Alunos possuem conta institucional para autenticação
- A API de IA para geração de relatórios estará disponível na fase de construção

---

## 5. Requisitos Funcionais

| ID    | Descrição                                                                                                                   | Prioridade | UC Relacionado |
|-------|-----------------------------------------------------------------------------------------------------------------------------|------------|----------------|
| RF001 | O sistema deve permitir criar, editar, visualizar e encerrar projetos acadêmicos                                            | Alta       | UC001          |
| RF002 | O sistema deve permitir definir a equipe de um projeto, incluindo alunos e orientador                                       | Alta       | UC001          |
| RF003 | O sistema deve oferecer quadro Kanban para criação e gestão de tarefas com responsável e prazo                              | Alta       | UC002          |
| RF004 | O sistema deve permitir mover tarefas entre colunas de status (A Fazer, Em Andamento, Concluído)                            | Alta       | UC002          |
| RF005 | O sistema deve permitir o upload de arquivos como entregas versionadas por etapa do projeto                                 | Alta       | UC003          |
| RF006 | O sistema deve manter histórico de versões das entregas com data, autor e possibilidade de download                         | Alta       | UC003          |
| RF007 | O sistema deve permitir vincular a URL de um repositório Git externo ao projeto                                             | Alta       | UC004          |
| RF008 | O sistema deve controlar acesso por perfis: Admin, Coordenador, Orientador e Aluno                                          | Alta       | UC005          |
| RF009 | O sistema deve registrar log de todas as operações críticas                                                                 | Alta       | UC005          |
| RF010 | O sistema deve gerar automaticamente relatório de progresso do projeto com apoio de IA                                      | Média      | UC006          |
| RF011 | O sistema deve permitir ao orientador avaliar e comentar entregas diretamente na plataforma                                 | Média      | UC003          |
| RF012 | O sistema deve gerar relatório consolidado de projetos por curso para o coordenador                                         | Média      | UC007          |
| RF013 | O sistema deve enviar notificações por e-mail em eventos como prazo próximo, nova entrega e novo comentário                 | Baixa      | —              |

---

## 6. Requisitos Não Funcionais

| ID     | Categoria        | Descrição                                                                                          |
|--------|------------------|----------------------------------------------------------------------------------------------------|
| RNF001 | Desempenho       | O sistema deve responder a 95% das requisições em menos de 3 segundos                             |
| RNF002 | Disponibilidade  | O sistema deve ter disponibilidade mínima de 99% no horário comercial                             |
| RNF003 | Segurança        | Todas as comunicações devem ser criptografadas (TLS/HTTPS)                                        |
| RNF004 | Segurança        | Senhas devem ser armazenadas com hash bcrypt; sessões devem expirar após 30 min de inatividade    |
| RNF005 | Usabilidade      | A interface deve ser acessível em dispositivos desktop e tablets modernos                          |
| RNF006 | Manutenibilidade | O código deve seguir padrões documentados e ter cobertura de testes ≥ 70%                         |
| RNF007 | Escalabilidade   | O sistema deve suportar até 2.000 usuários simultâneos sem degradação                             |
| RNF008 | Auditoria        | O sistema deve registrar data, hora, usuário e ação em todas as operações de escrita              |
| RNF009 | Armazenamento    | O sistema deve suportar upload de arquivos de até 50 MB por entrega                               |

---

## 7. Restrições, Dependências e Precedências

### 7.1 Restrições

- O sistema deve ser desenvolvido como aplicação web
- O banco de dados deve ser relacional (PostgreSQL ou MySQL)
- O sistema deve ser compatível com Chrome, Firefox, Edge e Safari (últimas 2 versões)
- O prazo para entrega da versão 1.0 é de 6 meses a partir do início da fase de construção
- A geração de relatórios por IA deve utilizar API externa com contrato de privacidade aprovado pela instituição

### 7.2 Dependências

- Disponibilidade de servidor de banco de dados antes do início do desenvolvimento
- Definição e aprovação do modelo de dados na fase de Elaboração
- Integração com SMTP institucional para envio de notificações
- Contratação ou disponibilização de API de IA para geração de relatórios
- Definição do modelo de autenticação (SSO institucional ou cadastro próprio)

### 7.3 Riscos Identificados

| Risco                                               | Probabilidade | Impacto | Mitigação                                           |
|-----------------------------------------------------|---------------|---------|-----------------------------------------------------|
| Mudança de escopo durante o desenvolvimento         | Alta          | Alto    | Controle rígido de mudanças via processo RUP        |
| Dificuldade de adoção pelos usuários                | Média         | Médio   | Treinamento, tutoriais e manual do usuário          |
| Indisponibilidade ou custo elevado da API de IA     | Média         | Médio   | Geração de relatório manual como fallback           |
| Falha de integração com SMTP institucional          | Baixa         | Baixo   | Funcionalidade de e-mail é de baixa prioridade      |
| Escalabilidade insuficiente com crescimento de projetos | Baixa     | Alto    | Testes de carga na fase de transição                |