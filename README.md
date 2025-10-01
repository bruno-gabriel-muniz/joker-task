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
│   ├── hello_world.py
│   ├── __init__.py
│   ├── joker_task.py
│   ├── schemas.py
├── LICENSE
├── poetry.lock
├── pyproject.toml
├── README.md
└── tests
    ├── conftest.py
    ├── __init__.py
    └── test_hello_world.py

```

## Arquitetura Inicial

<img src="https://i.ibb.co/prjcb5XT/Joker-Task.jpg" alt="Joker-Task" border="0">

- Security → autenticação/autorização
- Manager DB → manipulação de dados no banco
- Manager RSP → aplicação de filtros e resposta formatada para o usuário

## Próximos Passos

- [ ] Sistema de Login;
- [ ] Desenvolvimento dos tipos de Task através de TDD;
- [ ] Integração com os WorkBenchs, também com TDD; e
- [ ] Refatorações.
