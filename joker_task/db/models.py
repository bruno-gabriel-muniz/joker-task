from datetime import datetime
from typing import List, Literal

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    tasks: Mapped[List['Task']] = relationship(
        back_populates='user', init=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        init=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, init=False, server_default=func.now()
    )


@table_registry.mapped_as_dataclass
class Task:
    __tablename__ = 'tasks'

    id_task: Mapped[int] = mapped_column(
        Integer, primary_key=True, init=False, autoincrement=True
    )
    user_email: Mapped[str] = mapped_column(ForeignKey('users.email'))
    user: Mapped['User'] = relationship(back_populates='tasks')

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    done: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tags: Mapped[List[str] | None] = mapped_column(
        JSON, nullable=True
    )  # reformular
    reminder: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    repetition: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # Implementação Temporária
    state: Mapped[str | None] = mapped_column(String, nullable=True)  # Kanban
    priority: Mapped[int | Literal[100]] = mapped_column(Integer, default=100)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        init=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, init=False, server_default=func.now()
    )
