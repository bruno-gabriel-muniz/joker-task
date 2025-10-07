from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class UserUpdate(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    email: EmailStr
    username: str


class UserSchema(UserPublic):
    password: str


class Token(BaseModel):
    token: str
