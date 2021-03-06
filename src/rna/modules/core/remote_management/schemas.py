from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, root_validator, validator

from rna.modules.models import ResourceExists, ResourceNotFound, APIException


class HostFilterOptions(BaseModel):
    name: Optional[str]
    hostname: Optional[str]


class AuthenticationMethod(str, Enum):
    password = 'password'
    key_pair = 'key_pair'


class HostSchema(BaseModel):
    id: int
    name: str
    hostname: str
    port: int = 22
    username: Optional[str]
    ssh_options: Optional[str]
    authentication_method: Optional[AuthenticationMethod]
    password: Optional[str]
    private_key: Optional[str]
    # Password or private key will be encrypted with the users current password.
    encrypt_authentication: Optional[bool]


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
        if values.get('encrypt_authentication') is True:
            user_password: Optional[str] = values.get('user_password')
            if user_password is None:
                raise ValueError("user_password must be set if encrypting authentication credentials")
        return values

    @validator('port', pre=True, whole=True, check_fields=False, allow_reuse=True)
    def _port_as_int(cls, v):
        if v == '':
            return 22
        return int(v)

    @validator('authentication_method', pre=True, whole=True, check_fields=False, allow_reuse=True)
    def _authentication_method_if_blank(cls, v):
        if v == '':
            return None
        return v


class HostCreationSchema(HostBaseModel):
    name: str
    hostname: str
    port: int = 22
    username: Optional[str]
    ssh_options: Optional[str]
    authentication_method: Optional[AuthenticationMethod]
    password: Optional[str]
    private_key: Optional[str]
    # Password or private key will be encrypted with the users current password.
    encrypt_authentication: Optional[bool]
    user_password: Optional[str]


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


class CommandDetailSchema(BaseModel):
    id: int
    command: str
    host_id: int


class CommandCreationSchema(BaseModel):
    command: str
    host_id: int


class CommandUpdateSchema(BaseModel):
    command: str


class CommandHistorySchema(BaseModel):
    id: int
    guid: str
    result: str
    exit_code: str
    completed_at: datetime


# Executor
class ExecuteDetails(HostSchema):
    command_id: int
    command: str


class ExecutedDetails(BaseModel):
    result: str
    exit_code: int


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


class InvalidEncryptionPassword(APIException):
    def __init__(self, message="Invalid Password", *args, **kwargs):
        self.message = message


class CommandDoesntExist(ResourceNotFound):
    def __init__(self, command_id=None, host_id=None, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.command_id = command_id
        self.host_id = host_id
        self.message = "Command does not exist for Host"
