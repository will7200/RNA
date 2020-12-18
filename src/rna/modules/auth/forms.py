from typing import Optional

from pydantic import BaseModel, validator


class UserLoginSchema(BaseModel):
    username: str
    password: str
    remember_me: Optional[bool] = False

    @validator('password')
    def password_validate(cls, v):
        assert v != '', 'cannot be empty'
        return v

    @validator('username')
    def username_validate(cls, v):
        assert v != '', 'cannot be empty'
        return v
