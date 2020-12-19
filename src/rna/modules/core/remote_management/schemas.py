from enum import Enum
from typing import Optional, Any

from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema
from pydantic import BaseModel, root_validator, validator

# Host Management
from rna.modules.models import ResourceExists, ResourceNotFound


class HostDetailSchema(ModelSchema):
    class Meta:
        fields = ("name", "hostname", "username", "port", "ssh_options")

    password_required_to_run = fields.Method("requires_password")

    def requires_password(self, obj):
        if 'encrypt_authentication' in obj and obj.encrypt_authentication:
            return True
        return False


class HostFilterOptions(BaseModel):
    name: Optional[str]
    hostname: Optional[str]


class AuthenticationMethod(str, Enum):
    password = 'password'
    key_pair = 'key_pair'


class HostBaseModel(BaseModel):
    @root_validator(allow_reuse=True)
    def check_model(cls, values):
        auth_method: AuthenticationMethod = values.get('authentication_method')
        if auth_method is AuthenticationMethod.password:
            password: str = values.get('password')
            if password == '':
                raise ValueError("password cannot be blank")
        elif auth_method is AuthenticationMethod.key_pair:
            private_key: str = values.get('private_key')
            if private_key == '':
                raise ValueError("private_key cannot be blank")
            # TODO check that the private key is good
        return values


class HostCreationSchema(HostBaseModel):
    name: str
    hostname: str
    port: int = 22
    username: str = 'root'
    ssh_options: Optional[str]
    authentication_method: Optional[AuthenticationMethod]
    password: Optional[str]
    private_key: Optional[str]
    # Password or private key will be encrypted with the users current password.
    encrypt_authentication: Optional[bool]

    @validator('port', pre=True, whole=True)
    def _port_as_int(cls, v):
        if v == '':
            return 22
        return int(v)

    @validator('authentication_method', pre=True, whole=True)
    def _authentication_method_if_blank(cls, v):
        if v == '':
            return None
        return int(v)


class HostUpdateSchema(HostBaseModel):
    hostname: Optional[str]
    username: Optional[str]
    port: Optional[int]
    ssh_options: Optional[str]
    authentication_method: Optional[AuthenticationMethod]
    password: Optional[str]
    private_key: Optional[str]
    # Password or private key will be encrypted with the users current password.
    encrypt_authentication: Optional[bool]


# Executor
class ExecuteDetails(BaseModel):
    command: str
    hostname: str
    port: int = 22
    username: str = 'root'
    ssh_options: Optional[str]
    authentication_method: Optional[AuthenticationMethod]
    password: Optional[str]
    private_key: Optional[str]


class ExecutedDetails(BaseModel):
    result: str


# Exceptions


class HostExists(ResourceExists):
    def __init__(self, name=None, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.name = name
        self.message = "Host Already Exists with name"


class HostDoesntExist(ResourceNotFound):
    def __init__(self, name=None, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.name = name
        self.message = "Host does not exist"
