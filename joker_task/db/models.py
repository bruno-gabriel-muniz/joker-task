from datetime import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
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
    tags: Mapped[List['Tag']] = relationship(back_populates='user', init=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        init=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, init=False, server_default=func.now()
    )


task_tag = Table(
    'task_tag',
    table_registry.metadata,
    Column('id_task', ForeignKey('tasks.id_task'), primary_key=True),
    Column('id_tag', ForeignKey('tags.id_tag'), primary_key=True),
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
    reminder: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    repetition: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # Implementação Temporária # TODO
    state: Mapped[str | None] = mapped_column(String, nullable=True)  # Kanban

    tags: Mapped[List['Tag']] = relationship(
        'Tag',
        secondary=task_tag,
        back_populates='tasks',
        lazy='selectin',
    )
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


@table_registry.mapped_as_dataclass
class Tag:
    __tablename__ = 'tags'
    __table_args__ = (UniqueConstraint('user_email', 'name'),)

    id_tag: Mapped[int] = mapped_column(
        Integer, primary_key=True, init=False, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)

    user_email: Mapped[str] = mapped_column(ForeignKey('users.email'))
    user: Mapped['User'] = relationship(back_populates='tags')

    tasks: Mapped[List['Task']] = relationship(
        'Task',
        secondary=task_tag,
        back_populates='tags',
        lazy='selectin',
        init=False,
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
