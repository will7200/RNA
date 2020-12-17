from abc import ABC, abstractmethod
from typing import List

from rna.extensions import db
from rna.modules.core.users.models import UserDetailView, UserCreationSchema, UserUpdateSchema, UserFilterOptions, \
    UserExists, UserDoesntExist
from rna.modules.users.model import User


class AbstractUserManagement(ABC):
    """Base Class for User Management"""

    @abstractmethod
    def get_user(self, user_id) -> UserDetailView:
        """
        Gets a single user given by user_id
        :param user_id:
        :returns: User View
        """
        pass

    @abstractmethod
    def get_user_list(self, options: UserFilterOptions) -> List[UserDetailView]:
        pass

    @abstractmethod
    def create_user(self, details: UserCreationSchema) -> UserDetailView:
        pass

    @abstractmethod
    def delete_user(self, user_id):
        pass

    @abstractmethod
    def update_user(self, user_id, details: UserUpdateSchema):
        pass


class DBUserManagement(AbstractUserManagement):
    """DBUserManagement handles user management at the database level"""

    def update_user(self, user_id, details: UserUpdateSchema) -> bool:
        user: User = User.query.get(user_id)
        user.update(details)
        return True

    def delete_user(self, user_id) -> bool:
        user = User.query.filter((User.id == user_id)).one_or_none()
        if user is None:
            raise UserDoesntExist(user_id)
        db.session.delete(user)
        return True

    def create_user(self, details: UserCreationSchema) -> User:
        existing_user = User.query.filter((User.username == details.username) | (User.email == details.email)).all()
        if len(existing_user) > 0:
            raise UserExists(details.username, details.email)
        new_user = User(username=details.username, email=details.email, first_name=details.username,
                        last_name=details.last_name)
        new_user.set_password(details.password)
        db.session.add(new_user)
        return new_user

    def get_user(self, user_id) -> User:
        if type(user_id) is int:
            _found = User.query.get(user_id)
        else:
            _found = User.query.filter(User.username == user_id).one_or_none()
        if _found:
            return _found
        raise UserDoesntExist(user_id)

    def get_user_list(self, options: UserFilterOptions) -> List[User]:
        base = User.query
        if options.username:
            base = base.filter(User.username.like(f"%{options.username}%"))
        return base.all()
