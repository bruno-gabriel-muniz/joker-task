from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError, decode, encode
from loguru import logger
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import User
from joker_task.settings import Settings

pwd_context = PasswordHash.recommended()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_OAuth2PB = Annotated[str, Depends(oauth2_scheme)]


def get_hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)


def generate_access_token(data: dict) -> str:
    logger.info(f'generating access token for user: {data["sub"]}')
    settings = Settings()  # type: ignore

    to_encode = data.copy()
    delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    exp = delta + datetime.now(
        ZoneInfo('UTC'),
    )

    to_encode.update({'exp': exp, 'type': 'access'})

    return encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)


def generate_refresh_token(data: dict) -> str:
    logger.info(f'generating refresh token for user: {data["sub"]}')
    settings = Settings()  # type: ignore

    to_encode = data.copy()
    delta = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE)
    exp = delta + datetime.now(
        ZoneInfo('UTC'),
    )

    to_encode.update({'exp': exp, 'type': 'refresh'})

    return encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)


async def verify_refresh(token: str, session: T_Session) -> str:
    settings = Settings()  # type: ignore

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except InvalidTokenError:
        logger.info('refresh token verification failed: invalid token')
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, detail='invalid refresh token'
        )
    except Exception:  # pragma: no cover
        logger.warning(
            'refresh token verification failed: unexpected error'
        )  # pragma: no cover
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, 'invalid refresh token'
        )  # pragma: no cover

    if payload.get('sub') is None:
        logger.info('refresh token verification failed: no subject email')
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, detail='invalid refresh token'
        )

    if payload.get('type') != 'refresh':
        logger.info('refresh token verification failed: wrong token type')
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, detail='invalid refresh token'
        )

    user = await session.scalar(
        select(User).where(User.email == payload['sub'])
    )

    if not user:
        logger.info('refresh token verification failed: user not found')
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, detail='invalid refresh token'
        )

    return generate_access_token({'sub': payload['sub']})


async def get_user(request: Request, session: T_Session) -> User:
    token = request.cookies.get('access_token')

    if not token:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'not authenticated')

    settings = Settings()  # type: ignore

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except InvalidTokenError:
        logger.info('access token verification failed: invalid token')
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'invalid access token')
    except Exception:  # pragma: no cover
        logger.warning(
            'access token verification failed: unexpected error'
        )  # pragma: no cover
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, 'invalid access token'
        )  # pragma: no cover

    if payload.get('sub') is None:
        logger.info('access token verification failed: no subject email')
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'invalid access token')

    if payload.get('type') != 'access':
        logger.info('access token verification failed: wrong token type')
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'invalid access token')

    user = await session.scalar(
        select(User).where(User.email == payload.get('sub'))
    )

    if not user:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'invalid access token')

    return user
