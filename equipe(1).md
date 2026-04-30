# Equipe de Desenvolvimento — IFAL Projetos

---

## Membros

| Membro           | Papel Principal                        |  
|------------------|----------------------------------------|
| Davi Laurindo    | Desenvolvedor Fullstack — Módulo Core  |
| Ketlyn Barbosa   | Desenvolvedor Fullstack — Módulo Acadêmico |

---

## Davi Laurindo

**Responsabilidade principal:** Infraestrutura, autenticação e módulo de projetos/equipes.

### Módulos sob sua responsabilidade

| Módulo                  | Descrição                                                                 |
|-------------------------|---------------------------------------------------------------------------|
| Autenticação e Acesso   | Login, controle de sessão, perfis de usuário e permissões (RF008)        |
| Gestão de Projetos      | Criação, edição e encerramento de projetos; definição de equipes (RF001, RF002) |
| Quadro Kanban           | Criação e movimentação de tarefas, prazos e responsáveis (RF003, RF004)  |
| Log e Auditoria         | Registro de operações críticas no sistema (RF009)                        |
| Infraestrutura          | Configuração do banco de dados, deploy, HTTPS e ambiente de produção     |

### Artefatos esperados

- Modelagem e criação do banco de dados relacional
- API REST dos módulos acima
- Interfaces de front-end dos módulos acima
- Configuração do ambiente (Docker, variáveis de ambiente, CI/CD)

---

## Ketlyn Barbosa

**Responsabilidade principal:** Entregas, relatórios, notificações e integração com Git.

### Módulos sob sua responsabilidade

| Módulo                        | Descrição                                                                       |
|-------------------------------|---------------------------------------------------------------------------------|
| Controle de Entregas          | Upload, versionamento, histórico e download de entregas (RF005, RF006)         |
| Integração com Git            | Vinculação de URL de repositório externo por projeto (RF007)                   |
| Avaliação de Entregas         | Interface para orientador comentar e avaliar entregas (RF011)                  |
| Relatórios                    | Geração automática com IA e relatório consolidado por curso (RF010, RF012)     |
| Notificações por E-mail       | Envio de alertas via SMTP em eventos relevantes (RF013)                        |

### Artefatos esperados

- API REST dos módulos acima
- Interfaces de front-end dos módulos acima
- Integração com API de IA para geração de relatórios
- Configuração do servidor SMTP institucional

---

## Responsabilidades Compartilhadas

| Atividade                          | Descrição                                                             |
|------------------------------------|-----------------------------------------------------------------------|
| Revisão de código (code review)    | Pull requests revisados pelo outro membro antes do merge             |
| Testes                             | Cada membro escreve testes para os módulos sob sua responsabilidade  |
| Documentação técnica               | Ambos documentam endpoints, modelos e decisões de arquitetura        |
| Reuniões de alinhamento            | Sincronização periódica para integração entre os módulos             |
| Definição da arquitetura           | Decisões de arquitetura tomadas em conjunto                          |

---

## Fluxo de Trabalho (Git)

- Branch principal: `main`
- Branch de desenvolvimento: `develop`
- Branches de feature: `feature/<nome-do-modulo>` (ex: `feature/kanban`, `feature/entregas`)
- Pull requests obrigatórios para merge em `develop`
- Code review obrigatório pelo outro membro antes do merge

---

*Documento vinculado ao [Documento de Visão](./README.md).*