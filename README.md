![Top Language](https://img.shields.io/github/languages/top/bruno-gabriel-muniz/joker-task)
![Build](https://github.com/bruno-gabriel-muniz/joker-task/actions/workflows/ci.yaml/badge.svg)
[![codecov](https://codecov.io/gh/bruno-gabriel-muniz/joker-task/branch/main/graph/badge.svg)](https://codecov.io/gh/bruno-gabriel-muniz/joker-task)

# joker-task

O joker-task visa ser um gerenciador de tarefas o mais versátil e simples possível, além de servir de caso de estudo para o uso de boas práticas de programação.

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
├── joker_task
│   ├── app.py
│   ├── database.py
│   ├── __init__.py
│   ├── models.py
│   ├── router
│   │   └── auth.py
│   ├── schemas.py
│   ├── service
│   │   └── security.py
│   └── setings.py
├── LICENSE
├── migrations
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
│       └── ...
├── poetry.lock
├── pyproject.toml
├── README.md
└── tests
    ├── conftest.py
    ├── __init__.py
    ├── test_auth.py
    ├── test_hello_world.py
    └── test_security.py

```

## Arquitetura Inicial

<img src="https://i.ibb.co/0y9mdsp8/Joker-Task.jpg" alt="Joker-Task" border="0">

- auth → autenticação/autorização
- security → executa tarefas de autenticação
- manager_task → gerencia as tarefas e os workbenchs  
- manager_db → manipulação de dados no banco
- manager_rsp → aplicação de filtros e resposta formatada para o usuário

Cascata de chamadas:
- User -> auth -> security
- User -> manager_task -> (manager_db, manager_rsp)

## Próximos Passos

- [X] Sistema de Login;
- [ ] Desenvolvimento dos tipos de Task através de TDD;
- [ ] Integração com os WorkBenchs, também com TDD; e
- [ ] Refatorações.
