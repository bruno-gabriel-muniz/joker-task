from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class UserPublic(BaseModel):
    email: EmailStr
    username: str


class UserSchema(UserPublic):
    password: str
