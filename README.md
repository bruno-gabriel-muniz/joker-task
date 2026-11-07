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
- [Uso de IA no Desenvolvimento](#uso-de-ia-no-desenvolvimento)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Esquema do Banco de Dados](#esquema-do-banco-de-dados)
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

**Requisitos**: Python 3.14t-dev ou superior e Poetry. O Docker Compose é opcional.

> O projeto é disponibilizado como uma API. Após iniciá-la, a documentação interativa fica disponível em `http://localhost:8000/docs`.


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
Antes de iniciar a API, substitua `SECRET_KEY='YourSecretKey'` por uma chave secreta própria.


#### Como rodar o projeto?
```
poetry run alembic upgrade head
poetry app
```

#### Como rodar os testes?
```
poetry test
```

#### Como formatar e executar os linters?

```
poetry format
```

#### Rodando com Docker
```
docker compose up --build -d
docker compose exec api alembic upgrade head
```
---

## Uso de IA no Desenvolvimento Desse Projeto

O uso de ferramentas de IA nesse projeto tem o objetivo de explorar soluções mais eficientes, aumentar a confiabilidade do uso de IA no desenvolvimento de software e adquirir experiência prática com essas ferramentas.

As sugestões geradas são avaliadas de acordo com as interfaces e convenções do projeto e verificadas com testes e ferramentas de formatação. A IA auxilia o desenvolvimento, mas não substitui a revisão das mudanças nem a validação do código.

### Configuração do `AGENTS.md`

O AGENTS.md foi configurado para, além de passar os comandos básicos do projeto aos agents, criar um fluxo de desenvolvimento em que 100% de cobertura de código seja mantida enquanto a IA segue o que está definido nas interfaces, facilitando o gerenciamento da arquitetura e a expansão dela com auxílio de agentes com maior contexto de mundo e da intensão do projeto, do que de programação necessariamente.

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
│   │   ├── occurrence_service.py
│   │   ├── security.py
│   │   ├── tags_service.py
│   │   ├── task_collector.py
│   │   ├── task_service.py
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
├── AGENTS.md
├── poetry.lock
├── pyproject.toml
├── docker-compose.yml
├── LICENSE
└── README.md
```
---

## Esquema do Banco de Dados

```mermaid
erDiagram
    USERS {
        string email
        string username
        string password
        datetime updated_at
        datetime created_at
    }

    TASKS {
        int id_task
        string user_email
        string title
        string description
        boolean done
        datetime reminder
        string repetition
        string state
        int priority
        datetime updated_at
        datetime created_at
    }

    TASK_OCCURRENCES {
        int id_task_occurrence
        int id_task
        date occurrence_date
        boolean done
        datetime updated_at
        datetime created_at
    }

    TAGS {
        int id_tag
        string name
        string color_hex
        string user_email
        datetime updated_at
        datetime created_at
    }

    WORKBENCHS {
        int id_workbench
        string user_email
        string name
        json columns
        datetime updated_at
        datetime created_at
    }

    VIEWS {
        int id_view
        string user_email
        string name
        datetime updated_at
        datetime created_at
    }

    FILTERS {
        int id_filter
        int id_view
        string title
        string description
        boolean done
        json tags
        json reminder
        string repetition
        json state
        json priority
        int offset
        int limit
        datetime updated_at
        datetime created_at
    }

    TASK_TAG {
        int id_task
        int id_tag
    }

    TASK_WORKBENCH {
        int id_task
        int id_workbench
    }

    USERS ||--o{ TASKS : owns
    USERS ||--o{ TAGS : owns
    USERS ||--o{ WORKBENCHS : owns
    USERS ||--o{ VIEWS : owns

    TASKS ||--o{ TASK_OCCURRENCES : has

    TASKS ||--o{ TASK_TAG : has
    TAGS ||--o{ TASK_TAG : tagged

    TASKS ||--o{ TASK_WORKBENCH : has
    WORKBENCHS ||--o{ TASK_WORKBENCH : contains

    VIEWS ||--o{ FILTERS : has
```

---

## Arquitetura

```mermaid
---
config:
  theme: dark
---
flowchart TD

    subgraph Router["Camada HTTP (routers FastAPI)"]
        AuthRouter[auth]
        TaskRouter[tasks]
        TagRouter[tags]
        WorkbenchRouter[workbenches]
        ViewRouter[views]
    end

    subgraph Services["Serviços da aplicação"]
        Security[security]
        TaskCollector[task_collector]
        TaskService[task_service]
        TagService[tags_service]
        WorkbenchService[workbench_service]
        ViewService[view_service]
        FilterFactory[make_filters]
        OccurrenceService[occurrence_service]
    end
    AuthRouter --> Security

    TaskRouter --> TaskCollector
    TaskRouter --> TaskService
    TaskRouter --> TagService
    TaskRouter --> WorkbenchService
    TaskRouter --> OccurrenceService

    TagRouter --> TagService
    WorkbenchRouter --> WorkbenchService
    ViewRouter --> ViewService

    TaskCollector --> FilterFactory

    subgraph Mapper["Mapeamento"]
        Models[SQLAlchemy Models]
        Schemas[Pydantic Schemas]
    end
    
    subgraph ORM["Persistência"]
        Database[Database]
        SQLAlchemy[SQLAlchemy ORM]
    end

    Database --> SQLAlchemy --> Models --> Schemas
```

---

## Fluxo de Requisição

```mermaid
---
config:
  theme: dark
---
flowchart TD
    User[Usuário] -->|1| Request[Requisição]
    Request -->|2| Router[Roteador]
    Router -->|3| Services[Serviços]
    Services -->|4| ORM[ORM]
    ORM -->|5| Services
    Services -->|6| Router
    Router -->|7| Mapper[Mapeador]
    Mapper -->|8| Router
    Router -->|9| Response[Resposta]
    Response -->|10| User
```
---

### Principais módulos

- **auth**: Responsável pela autenticação e autorização.

- **security**: Implementa regras de segurança (tokens, hashing, validações).

- **tasks (router)**: Camada de entrada HTTP. Orquestra o fluxo da requisição.

- **occurrence_service**: Gerencia ocorrências de tarefas, como repetições e histórico.

- **task_collector**: Responsável por buscar tarefas no banco, aplicando filtros dinâmicos usando *Strategy* e o **make_filters**.

- **make_filters**: Camada que traduz os filtros para expressão SQL, utilizando o padrão *Factory*

- **task_service**: Gerencia as funções básicas das tasks.

- **tags_service**: Gerencia criação, reutilização, verificação de conflitos e associação de tags com as tasks.

- **workbench_service**: Gerencia coleta, verificação de conflitos e associação de workbenches com as tasks.

- **view_service**: Gerencia criação, reutilização, verificação de conflitos e associação de views com as tasks.

- **mapper**: Converte modelos ORM em schemas públicos, desacoplando banco de dados da API.

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
- [X] Implementar sistema para o rastreamento da ocorrência de tarefas
- [X] Implementar auxilío de desenvolvimento com agentes de IA, para estudar otimização e melhorias de confiabilidade.
- [ ] Implementação do sistema de repetição de tarefas
- [ ] Melhorar documentação de decisões arquiteturais
- [ ] Refatorações e melhorias arquiteturais contínuas

