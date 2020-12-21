from typing import Optional

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from pydantic import BaseModel, validator

from rna.modules.models import ResourceExists, ResourceNotFound


class UserDetailView(SQLAlchemyAutoSchema):
    """UserDetailSchema exposes the correct fields when marshalling the request over the api"""

    class Meta:
        fields = ("username", "email", "first_name", "last_name")


class UserCreationSchema(BaseModel):
    """User Model for creating a new user"""
    username: str
    email: str
    password: str
    first_name: Optional[str]
    last_name: Optional[str]

    @validator('username')
    def name_must_contain_space(cls, v):
        if len(v) > 60:
            raise ValueError("Username is too long")
        assert v.isalnum(), 'must be alphanumeric'
        return v

    @validator('password')
    def passwords_match(cls, v):
        assert v != '', 'must contain a value'
        return v


class UserUpdateSchema(BaseModel):
    """User Model for updating a current user"""
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


class UserFilterOptions(BaseModel):
    """UserFilterOptions holds optional filter that may be used to get a subset of results"""
    username: Optional[str]


class UserExists(ResourceExists):
    def __init__(self, username=None, email=None, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.username = username
        self.email = email
        self.message = "User Already Exists with username and/or email"


class UserDoesntExist(ResourceNotFound):
    def __init__(self, username=None, email=None, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.username = username
        self.email = email
        self.message = "User does not exist"
