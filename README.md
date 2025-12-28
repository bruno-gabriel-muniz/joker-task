![Top Language](https://img.shields.io/github/languages/top/bruno-gabriel-muniz/joker-task)
![Build](https://github.com/bruno-gabriel-muniz/joker-task/actions/workflows/ci.yaml/badge.svg)
[![codecov](https://codecov.io/gh/bruno-gabriel-muniz/joker-task/branch/main/graph/badge.svg)](https://codecov.io/gh/bruno-gabriel-muniz/joker-task)

<img src="https://i.ibb.co/wZb6qrnZ/Joker-Task-Editado.png" alt="Joker-Task-Editado" border="0">

## Sobre o projeto

O **joker-task** é uma API de gerenciamento de tarefas em desenvolvimento que busca ser apenas o *espaço em branco* entre você e a conclusão das suas tarefas.

A ideia central é oferecer um sistema de organização **flexível**, **simples de manter** e **agnóstico a metodologias** específicas de produtividade.

Em vez de impor regras, o sistema fornece estruturas mínimas que podem ser combinadas livremente.

---

## Conceitos principais

O domínio do sistema é organizado em três conceitos centrais, além dos usuários:

- **Tasks**  
  Um único tipo de tarefa, capaz de representar diferentes estratégias de organização, como:
  - lembretes
  - quadros Kanban
  - trackers
  - ou tarefas simples, sem estrutura adicional

- **Workbenches** *(planejado)*  
  Zonas de trabalho que facilitam a visualização recorrente de determinado conjunto de tarefas.

- **Views** *(planejado)*  
  Filtros reutilizáveis que coletam tarefas com base em critérios específicos.

> A ideia é que qualquer técnica de organização surja da **combinação desses elementos**, e não de tipos rígidos de tarefas.

---

## Status atual

Atualmente, o projeto conta com:

- autenticação e autorização
- CRUD de tarefas
- sistema de tags por usuário
- filtragem dinâmica de tarefas
- arquitetura modular com separação clara de responsabilidades
- testes automatizados com cobertura

O projeto está em evolução contínua, com foco em **qualidade de código**, **testabilidade** e **clareza arquitetural**.

---

## Sumário

- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Arquitetura](#arquitetura)
- [Próximos Passos](#próximos-passos)

---

## Tecnologias Utilizadas

- **Python**
- **FastAPI**
- **SQLAlchemy (async)**
- **Alembic**
- **Pytest**
- **Docker**

---

## Estrutura do Projeto

```
.
├── .github
│ └── workflows
│ └── ci.yaml
├── joker_task
│ ├── db
│ │ ├── database.py
│ │ └── models.py
│ ├── router
│ │ ├── auth.py
│ │ ├── tasks.py
│ │ └── tags.py
│ ├── service
│ │ ├── security.py
│ │ ├── task_collector.py
│ │ ├── tags_controler.py
│ │ ├── make_filters.py
│ │ └── mapper.py
│ ├── interfaces
│ │ └── interfaces.py
│ ├── app.py
│ ├── schemas.py
│ └── settings.py
├── migrations
│ ├── env.py
│ ├── README
│ └── versions
│ └── ...
├── tests
│ └── ...
├── pyproject.toml
└── README.md
```
---

## Arquitetura

<img src="https://i.ibb.co/tPZNP6BZ/diagrama-de-modulos.png" alt="diagrama de modulos" border="0">

### Principais módulos

- **auth**: Responsável pela autenticação e autorização.

- **security**: Implementa regras de segurança (tokens, hashing, validações).

- **tasks (router)**: Camada de entrada HTTP. Orquestra o fluxo da requisição.

- **task_collector**: Responsável por buscar tarefas no banco, aplicando filtros dinâmicos usando *Strategy* e o **make_filters**.

- **make_filters**: Camada que traduz os filtros para expressão SQL, utilizando o padrão *Factory*

- **tags_controler**: Gerencia criação, reutilização, atualização e associação de tags por usuário.

- **mapper**: Converte modelos ORM em schemas públicos, desacoplando banco de dados da API.

---

### Fluxo de chamadas

- `User → auth → security`
- `User → tasks → task_collector → mapper`
- `User → tasks → (tags_controler, task_collector) → mapper`
- `User → tags → tags_controler → mapper`

---

## Próximos Passos

- [X] Sistema de Login
- [X] Sistema de Logs
- [X] CRUD de Tasks
- [X] Router Tags
- [ ] Integração com Workbenches
- [ ] Filtros mais avançados (views reutilizáveis)
- [ ] Evolução do domínio de Tags
- [ ] Refatorações e melhorias arquiteturais contínuas

