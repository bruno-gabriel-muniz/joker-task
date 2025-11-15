![Top Language](https://img.shields.io/github/languages/top/bruno-gabriel-muniz/joker-task)
![Build](https://github.com/bruno-gabriel-muniz/joker-task/actions/workflows/ci.yaml/badge.svg)
[![codecov](https://codecov.io/gh/bruno-gabriel-muniz/joker-task/branch/main/graph/badge.svg)](https://codecov.io/gh/bruno-gabriel-muniz/joker-task)

<img src="https://i.ibb.co/wZb6qrnZ/Joker-Task-Editado.png" alt="Joker-Task-Editado" border="0">

O joker-task é uma API de gerenciamento de tarefas em desenvolvimento que busca ser apenas o espaço em branco entre você e a conclusão das suas tarefas. Ou seja, um sistema de organização que não é trabalhoso e nem difícil de se manter a longo prazo.

Para isso, eu organizei o sistema de tarefas em apenas três pontos principais além dos usuários:

- Tasks: um único tipo de tarefa que pode ter qualquer técnica de gerenciamento, seja lembretes, colunas de quadro kanban, trakers ou nenhum;
- Workbenches: zonas que facilitam a visualização recorrente de determinado tipo de tarefa;
- Views: filtros que coletam determinadas tarefas.

<!--(Futuramente: Imagem explicativa)-->

Até agora o sistema conta apenas com o sistema de autenticação, mas a ideia é que ele cresça com o tempo e se torne um sistema robusto e flexível.

## Sumário
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Arquitetura Inicial](#arquitetura-inicial)
- [Próximos Passos](#próximos-passos)

## Tecnologias Utilizadas

- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pytest
- Docker

## Estrutura do Projeto

```
.
├── .github
│   └── workflows
│       └── ci.yaml
├── joker_task
│   ├── db
│   │   ├── database.py
│   │   └── models.py
│   ├── router
│   │   ├── auth.py
│   │   └── tasks.py
│   ├── service
│   │   └── security.py
│   ├── __init__.py
│   ├── app.py
│   ├── schemas.py
│   └── settings.py
├── migrations
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
│       └─── ...
├── tests
│   ├── conftest.py
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_hello_world.py
│   ├── test_security.py
│   └── test_tasks.py
├── .gitignore
├── LICENSE
├── poetry.lock
├── pyproject.toml
└── README.md


```

## Arquitetura Inicial

<img src="https://i.ibb.co/NgYJvRmF/Screenshot-2025-11-15-12-04-16.png" alt="Screenshot-2025-11-15-12-04-16" border="0">

- auth → autenticação/autorização
- security → executa tarefas de autenticação
- tasks → gerencia as tarefas e os workbenches
- task_collector → busca e coleta as tasks conforme os filtros

Cascata de chamadas:
- User -> auth -> security
- User -> tasks -> task_collector

## Próximos Passos

- [X] Sistema de Login;
- [X] Sistema de Logs;
- [ ] Desenvolvimento do CRUD de Task através de TDD;
- [ ] Integração com os workbenches, também com TDD; e
- [ ] Refatorações.
