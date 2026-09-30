FROM python:3.14

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root

COPY . .

CMD ["fastapi", "run", "joker_task/app.py", "--port", "8000"]