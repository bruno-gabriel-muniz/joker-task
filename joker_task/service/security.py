from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated, Literal
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException, Request, Response
from jwt import InvalidTokenError, decode, encode
from loguru import logger
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import User
from joker_task.settings import Settings

pwd_context = PasswordHash.recommended()


T_Session = Annotated[AsyncSession, Depends(get_session)]


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
    delta = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE)
    exp = delta + datetime.now(
        ZoneInfo('UTC'),
    )

    to_encode.update({'exp': exp, 'type': 'refresh'})

    return encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)


def verify_token(
    token: str, expected_type: Literal['access', 'refresh']
) -> dict:
    settings = Settings()  # type: ignore

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except InvalidTokenError:
        logger.info('token verification failed: invalid token')
        raise HTTPException(HTTPStatus.UNAUTHORIZED, detail='invalid token')
    except Exception:  # pragma: no cover
        logger.warning(
            'token verification failed: unexpected error'
        )  # pragma: no cover
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, 'invalid token'
        )  # pragma: no cover

    if payload.get('sub') is None:
        logger.info('token verification failed: no subject email')
        raise HTTPException(HTTPStatus.UNAUTHORIZED, detail='invalid token')

    if payload.get('type') != expected_type:
        logger.info('token verification failed: wrong token type')
        raise HTTPException(HTTPStatus.UNAUTHORIZED, detail='invalid token')

    return payload


async def get_user(
    request: Request, response: Response, session: T_Session
) -> User:
    settings = Settings()  # type: ignore
    token = request.cookies.get('access_token') or ''

    try:
        payload: dict[str, str] = verify_token(token, 'access')
    except HTTPException:
        token = request.cookies.get('refresh_token') or ''
        payload = verify_token(token, 'refresh')

        response.set_cookie(
            key='access_token',
            value=generate_access_token({'sub': payload['sub']}),
            httponly=True,
            secure=settings.PROD,  # True em produção (HTTPS)
            samesite='strict',
            max_age=60 * 15,  # 15 minutos
            path='/',
        )

    user = await session.scalar(
        select(User).where(User.email == payload.get('sub'))
    )

    if not user:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'invalid token')

    return user
