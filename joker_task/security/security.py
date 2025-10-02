from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def get_hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)
