from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.database.database import get_session
from joker_task.database.models import User
from joker_task.settings import Settings

pwd_context = PasswordHash.recommended()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token/')

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_OAuth2PB = Annotated[str, Depends(oauth2_scheme)]


def get_hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)


def generate_access_token(data: dict) -> str:
    settings = Settings()  # type: ignore

    to_encode = data.copy()
    delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    exp = delta + datetime.now(
        ZoneInfo('UTC'),
    )

    to_encode.update({'exp': exp})

    return encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)


async def get_user(token: T_OAuth2PB, session: T_Session):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    settings = Settings()  # type: ignore

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject_email = payload.get('sub')

        if not subject_email:
            raise credentials_exception

    except (DecodeError, ExpiredSignatureError):
        raise credentials_exception

    user = await session.scalar(
        select(User).where(User.email == subject_email)
    )

    if not user:
        raise credentials_exception

    return user
