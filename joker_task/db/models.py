from datetime import datetime
from typing import List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
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
        Integer, primary_key=True, autoincrement=True
    )
    user_email: Mapped[str] = mapped_column(ForeignKey('users.email'))
    user: Mapped['User'] = relationship(back_populates='tasks')

    done: Mapped[bool] = mapped_column(Boolean, nullable=True)
    tag: Mapped[str] = mapped_column(String, nullable=True)
    reminder: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    repetition: Mapped[str] = mapped_column(
        String, nullable=True
    )  # Implementação Temporária
    state: Mapped[str] = mapped_column(String, nullable=True)  # Kanban
    priority: Mapped[int] = mapped_column(Integer, default=100)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        init=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, init=False, server_default=func.now()
    )
