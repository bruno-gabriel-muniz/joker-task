from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request, Response
from sqlalchemy import select

from joker_task.db.models import User
from joker_task.schemas import UserPublic, UserSchema, UserUpdate
from joker_task.service.dependencies import (
    T_Mapper,
    T_OAuth2PRF,
    T_Session,
    T_User,
)
from joker_task.service.security import (
    generate_access_token,
    generate_refresh_token,
    get_hash_password,
    verify_password,
    verify_refresh,
)
from joker_task.settings import Settings

auth_router = APIRouter(prefix='', tags=['auth'])


@auth_router.post(
    '/users/', response_model=UserPublic, status_code=HTTPStatus.OK
)
async def create_user(user: UserSchema, session: T_Session, mapper: T_Mapper):
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

    return mapper.map_user_public(user_db)


@auth_router.post('/login/', response_model=None, status_code=HTTPStatus.OK)
@auth_router.post(
    '/login',
    response_model=None,
    status_code=HTTPStatus.OK,
    include_in_schema=False,
)
async def login(
    response: Response, form_data: T_OAuth2PRF, session: T_Session
):
    # autenticação do usuário
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )
    if user is None or not verify_password(form_data.password, user.password):
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, detail='invalid email or password'
        )

    access_token = generate_access_token({'sub': user.email})
    refresh_token = generate_refresh_token({'sub': user.email})

    settings = Settings()  # type: ignore

    # 🍪 ACCESS TOKEN (curto)
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=settings.PROD,  # 🔴 True em produção (HTTPS)
        samesite='strict',
        max_age=60 * 15,  # 15 minutos
        path='/',
    )

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=settings.PROD,
        samesite='strict',
        max_age=60 * 60 * 15,  # 15 horas
        path='/',
    )


@auth_router.post('/refresh/', response_model=None, status_code=HTTPStatus.OK)
@auth_router.post(
    '/refresh',
    response_model=None,
    status_code=HTTPStatus.OK,
    include_in_schema=False,
)
async def refresh_token(
    request: Request, response: Response, session: T_Session
):
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, 'missing refresh token')

    new_access_token = await verify_refresh(refresh_token, session)

    settings = Settings()  # type: ignore

    response.set_cookie(
        key='access_token',
        value=new_access_token,
        httponly=True,
        secure=settings.PROD,
        samesite='lax',
        max_age=60 * 15,
        path='/',
    )


@auth_router.post('/logout/', response_model=None, status_code=HTTPStatus.OK)
@auth_router.post(
    '/logout',
    response_model=None,
    status_code=HTTPStatus.OK,
    include_in_schema=False,
)
async def logout(response: Response):
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/')


@auth_router.put(
    '/update_user/', response_model=UserPublic, status_code=HTTPStatus.OK
)
async def update_user(
    user_update: UserUpdate,
    current_user: T_User,
    session: T_Session,
    mapper: T_Mapper,
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

    return mapper.map_user_public(current_user)
