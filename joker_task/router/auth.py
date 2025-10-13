from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.database.database import get_session
from joker_task.database.models import User
from joker_task.schemas import Token, UserPublic, UserSchema, UserUpdate
from joker_task.service.security import (
    generate_access_token,
    get_hash_password,
    get_user,
    verify_password,
)

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_OAuth2PRF = Annotated[OAuth2PasswordRequestForm, Depends()]
T_User = Annotated[User, Depends(get_user)]

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


@auth.post('/token/', response_model=Token, status_code=HTTPStatus.OK)
async def get_access_token(form_data: T_OAuth2PRF, session: T_Session):
    user_db = await session.scalar(
        select(User).where(User.email == form_data.username)
    )
    if user_db is None or not verify_password(
        form_data.password, user_db.password
    ):
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, detail='incorrect email or password'
        )

    return {'token': generate_access_token({'sub': user_db.email})}


@auth.put(
    '/update_user/', response_model=UserPublic, status_code=HTTPStatus.OK
)
async def update_user(
    user_update: UserUpdate, current_user: T_User, session: T_Session
):
    if user_update.username != current_user.username:
        have_conflict = await session.scalar(
            select(User).where(User.username == user_update.username)
        )

        if have_conflict:
            raise HTTPException(
                HTTPStatus.CONFLICT, 'username is already in use'
            )

        current_user.username = user_update.username

    current_user.password = get_hash_password(user_update.password)

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return current_user
