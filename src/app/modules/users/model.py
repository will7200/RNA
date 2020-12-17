import datetime
import functools
from typing import Optional, Set, List

from flask import abort
from flask_login import current_user
from marshmallow_sqlalchemy import ModelSchema
from pydantic import BaseModel, validator
from sqlalchemy import Integer, Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from modules import Base, UpdateMixin
from modules.models import ResourceExists, ResourceNotFound


class User(Base, UpdateMixin):
    """User Model for database creation and use"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    # User Information
    username = Column(String(60), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    first_name = Column(String(32))
    last_name = Column(String(32))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    # Backend Information
    password_hash = Column(String(128))
    active = Column(Boolean(), default=True)
    roles: List['Role'] = relationship("Role", backref="users", cascade="all,delete", uselist=True)  # type: ignore
    role_names = association_proxy('roles', 'name')

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.active

    def get_id(self):
        return int(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return not self.is_authenticated


class Role(Base, UpdateMixin):
    """Role Model for database creation and use"""
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String())
    user_id = Column(Integer, ForeignKey('users.id'))


def roles_required(*role_names):
    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            missing_roles = [
                role_name
                for role_name in role_names
                if role_name not in current_user.role_names
            ]

            if missing_roles:
                abort(401, message="Missing role(s): {}".format(', '.join(missing_roles)))

            return original_route(*args, **kwargs)

        return decorated_route

    return decorator


def roles_has_one(*role_names):
    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            has_roles = [
                role_name
                for role_name in role_names
                if role_name in current_user.role_names
            ]

            if len(has_roles) == 0:
                abort(401)

            return original_route(*args, **kwargs)

        return decorated_route

    return decorator


class UserDetailView(ModelSchema):
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


class UserLoginSchema(BaseModel):
    username: str
    password: str
    remember_me: Optional[bool] = False


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
