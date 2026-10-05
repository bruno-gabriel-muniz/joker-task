![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Top Language](https://img.shields.io/github/languages/top/bruno-gabriel-muniz/joker-task)
![Build](https://github.com/bruno-gabriel-muniz/joker-task/actions/workflows/ci.yaml/badge.svg)
[![codecov](https://codecov.io/gh/bruno-gabriel-muniz/joker-task/branch/main/graph/badge.svg)](https://codecov.io/gh/bruno-gabriel-muniz/joker-task)

<img src="https://i.ibb.co/wZb6qrnZ/Joker-Task-Editado.png" alt="Joker-Task-Editado" border="0">

## Sobre o projeto

O **joker-task** é uma api de gerenciamento de tarefas em desenvolvimento que busca ser apenas o *espaço em branco* entre você e a conclusão das suas tarefas.

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

- **Workbenches**  
  Zonas de trabalho que facilitam a visualização recorrente de determinado conjunto de tarefas.

- **Views**  
  Filtros reutilizáveis que coletam tarefas com base em critérios específicos.

> A ideia é que qualquer técnica de organização surja da **combinação desses elementos**, e não de tipos rígidos de tarefas.

---

## Status atual

Atualmente, o projeto conta com:

- autenticação e autorização
- CRUD de tarefas e tags por usuário
- filtragem dinâmica de tarefas
- associação de tarefas via workbenches
- views reutilizáveis
- arquitetura modular com separação clara de responsabilidades
- testes automatizados com cobertura

O projeto está em evolução contínua, com foco em **qualidade de código**, **testabilidade** e **clareza arquitetural**.

---

## Sumário

- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Como Começar?](#como-começar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Database Schema](#database-schema)
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

## Como Começar?

### Backend

**Requisitos**: Python 3.14t-dev e Poetry.

> O projeto é disponibilizado como uma API, com documentação interativa disponível em /docs.


#### Como baixar o projeto?
```
git clone https://github.com/bruno-gabriel-muniz/joker-task
```

#### Como instalar as dependências?
```
poetry install
poetry self add 'poethepoet[poetry_plugin]'
```

#### Como configurar as variáveis de ambiente?
```
cp joker_task/.env.example joker_task/.env
```
Crie a sua própria chave secreta para o JWT.


#### Como rodar o projeto?
```
poetry run alembic upgrade head
poetry app
```

#### Como rodar os testes?
```
poetry test
```

#### Como usar os linters?

```
poetry format
```

#### Rodando com Docker
```
docker compose up --build -d
poetry run alembic upgrade head
```
---

## Estrutura do Projeto

```
.
├── joker_task
│   ├── db
│   │   ├── database.py
│   │   └── models.py
│   ├── interfaces
│   │   └── interfaces.py
│   ├── router
│   │   ├── auth.py
│   │   ├── tags.py
│   │   ├── tasks.py
│   │   ├── views.py
│   │   └── workbenches.py
│   ├── service
│   │   ├── dependencies.py
│   │   ├── make_filters.py
│   │   ├── mapper.py
│   │   ├── security.py
│   │   ├── tags_service.py
│   │   ├── task_collector.py
│   │   ├── view_service.py
│   │   └── workbench_service.py
│   ├── __init__.py
│   ├── app.py
│   ├── schemas.py
│   └── settings.py
├── migrations
│   └── ...
├── tests
│   └── ...
├── poetry.lock
├── pyproject.toml
├── docker-compose.yml
├── LICENSE
└── README.md
```
---

## Database Schema

```mermaid
erDiagram


    USERS {
        string email
        string password_hash
        datetime created_at
    }

    TASKS {
        int id
        string title
        text description
        boolean done
        json repetition
        json history
        int workbench_id
        datetime created_at
    }

    WORKBENCHS {
        int id
        string name
        datetime created_at
    }

    TASK_WORKBENCHS {
        int task_id
        int workbench_id
    }

    TAGS {
        int id
        string name
        string color
        datetime created_at
    }

    TASK_TAGS {
        int task_id
        int tag_id
    }

    VIEWS {
        int id
        string name
        int workbench_id
        datetime created_at
    }

    VIEW_FILTERS {
        int id
        int view_id
        json filters
    }

    USERS ||--o{ TASKS : owns
    USERS ||--o{ TAGS : owns
    USERS ||--o{ WORKBENCHS : owns
    USERS ||--o{ VIEWS : owns

    TASKS ||--o{ TASK_TAGS : has
    TAGS ||--o{ TASK_TAGS : tagged

    TASKS ||--o{ TASK_WORKBENCHS : has
    WORKBENCHS ||--o{ TASK_WORKBENCHS : contains

    VIEWS ||--o{ VIEW_FILTERS : has
```

---

## Arquitetura

```mermaid
---
config:
  theme: dark
---
flowchart TD
    User[Cliente / Usuário] --> Router

    subgraph Router Camada HTTP FastAPI Routers
        AuthRouter[auth]
        TaskRouter[tasks]
        TagRouter[tags]
        WorkbenchRouter[workbenches]
        ViewRouter[views]
    end
    Router --> Services

    subgraph Services Application Services
        Security[security]
        TaskCollector[task_collector]
        TagService[tags_service]
        WorkbenchService[workbench_service]
        ViewService[view_service]
        FilterFactory[make_filters]
    end
    AuthRouter --> Security

    TaskRouter --> TaskCollector
    TaskRouter --> TagService
    TaskRouter --> WorkbenchService

    TagRouter --> TagService
    WorkbenchRouter --> WorkbenchService
    ViewRouter --> ViewService

    TaskCollector --> FilterFactory
    Services --> ORM

    subgraph ORM Camada de Persistência
        Models[SQLAlchemy Models]
        DB[(Database)]
    end

    Models --> DB

    subgraph Mapper Mapper
        PublicSchemas[Public Schemas DTOs]
    end

    Router --> Mapper
```
---

### Principais módulos

- **auth**: Responsável pela autenticação e autorização.

- **security**: Implementa regras de segurança (tokens, hashing, validações).

- **tasks (router)**: Camada de entrada HTTP. Orquestra o fluxo da requisição.

- **task_collector**: Responsável por buscar tarefas no banco, aplicando filtros dinâmicos usando *Strategy* e o **make_filters**.

- **make_filters**: Camada que traduz os filtros para expressão SQL, utilizando o padrão *Factory*

- **tags_service**: Gerencia criação, reutilização, verificação de conflitos e associação de tags com as tasks.

- **workbench_service**: Gerencia coleta, verificação de conflitos e associação de workbenches com as tasks.

- **view_service**: Gerencia criação, reutilização, verificação de conflitos e associação de views com as tasks.

- **mapper**: Converte modelos ORM em schemas públicos, desacoplando banco de dados da API.

---

### Fluxo de chamadas

- `User → auth → security`
- `User → tasks → task_collector → mapper`
- `User → tasks → (tags_service, task_collector, workbench_service) → mapper`
- `User → tags → tags_service → mapper`
- `User → workbenches → workbench_service → mapper`
- `User → views → view_service → (task_collector) → mapper`

---

## Próximos Passos

- [X] Sistema de Login
- [X] Sistema de Logs
- [X] CRUD de Tasks
- [X] Router Tags
- [X] Integração com Workbenches
- [X] Filtros mais avançados (views reutilizáveis)
- [X] Evolução do domínio de Tags
- [X] Dockerizar o backend
- [ ] Implementação do sistema de repetição de tarefas
- [ ] Melhorar documentação de decisões arquiteturais
- [ ] Refatorações e melhorias arquiteturais contínuas

