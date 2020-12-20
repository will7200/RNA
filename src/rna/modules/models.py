import abc
import http

from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm.query import Query


class DeclarativeABCMeta(DeclarativeMeta, abc.ABCMeta):
    pass


_Base = declarative_base(metaclass=DeclarativeABCMeta)


# type: ignore
class Base(_Base):
    __abstract__ = True

    query: Query

    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class UpdateMixin:
    """
    Add a simple update() method to instances that accepts
    a dictionary of updates.
    """

    def update(self, values):
        for k, v in values.items():
            setattr(self, k, v)


class APIException(Exception):
    status_code = http.HTTPStatus.INTERNAL_SERVER_ERROR.value

    def __init__(self, message="Error Occurred", status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class ResourceExists(APIException):
    status_code = http.HTTPStatus.CONFLICT.value

    def __init__(self, message="Resource Already Exists", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class ResourceNotFound(APIException):
    status_code = http.HTTPStatus.NOT_FOUND.value

    def __init__(self, message="Resource Not Found", *args, **kwargs):
        super().__init__(message, *args, **kwargs)
