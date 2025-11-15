from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import User
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

auth_router = APIRouter(prefix='', tags=['auth'])


@auth_router.post(
    '/users/', response_model=UserPublic, status_code=HTTPStatus.OK
)
async def create_user(user: UserSchema, session: T_Session):
    logger.info('checking for conflict')
    exist_conflict = await session.scalar(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    )

    if exist_conflict:
        logger.info('a conflict was found, returning an error message')
        raise HTTPException(
            HTTPStatus.CONFLICT, detail='email or username already in use'
        )

    logger.info('creating the new user')
    user_db = User(user.email, user.username, get_hash_password(user.password))

    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)

    logger.info('returning the new user')
    return user_db


@auth_router.post('/token/', response_model=Token, status_code=HTTPStatus.OK)
async def get_access_token(form_data: T_OAuth2PRF, session: T_Session):
    logger.info('geting user in db')
    user_db = await session.scalar(
        select(User).where(User.email == form_data.username)
    )
    if user_db is None or not verify_password(
        form_data.password, user_db.password
    ):
        logger.info('incorrect username or password, returning an error')
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, detail='incorrect email or password'
        )

    logger.info('returnig the token')
    return {'access_token': generate_access_token({'sub': user_db.email})}


@auth_router.put(
    '/update_user/', response_model=UserPublic, status_code=HTTPStatus.OK
)
async def update_user(
    user_update: UserUpdate, current_user: T_User, session: T_Session
):
    logger.info('checking conflicts')
    if user_update.username != current_user.username:
        have_conflict = await session.scalar(
            select(User).where(User.username == user_update.username)
        )

        if have_conflict:
            logger.info('username conflict found, returning an error')
            raise HTTPException(
                HTTPStatus.CONFLICT, 'username is already in use'
            )

        current_user.username = user_update.username

    current_user.password = get_hash_password(user_update.password)

    logger.info('saving changes')
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    logger.info('returning user')
    return current_user
