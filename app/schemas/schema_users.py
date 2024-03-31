from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    email: EmailStr


class UserInDB(User):
    password: str = Field(min_length=6, max_length=32)
