from typing import Optional

from pydantic import BaseModel, validator


class UserLoginSchema(BaseModel):
    username: str
    password: str
    remember_me: Optional[bool] = False

    @validator('password')
    def passwords_match(cls, v):
        assert v != '', 'must contain a value'
        return v
