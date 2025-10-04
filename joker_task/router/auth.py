from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.database import get_session
from joker_task.models import User
from joker_task.schemas import UserPublic, UserSchema
from joker_task.service.security import get_hash_password

T_Session = Annotated[AsyncSession, Depends(get_session)]


auth = APIRouter(prefix='', tags=['auth'])


@auth.post('/users/', response_model=UserPublic, status_code=HTTPStatus.OK)
async def create_user(user: UserSchema, session: T_Session):
    exist_conflict = await session.scalar(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    )

    if exist_conflict:
        raise HTTPException(
            HTTPStatus.CONFLICT, detail='email or username already in use'
        )

    user_db = User(user.email, user.username, get_hash_password(user.password))

    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)

    return user_db
