from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from jwt import encode
from pwdlib import PasswordHash

from joker_task.settings import Settings

pwd_context = PasswordHash.recommended()


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
