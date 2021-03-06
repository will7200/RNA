from typing import List

from rna.extensions import db
from rna.modules.core.users.models import UserCreationSchema, UserUpdateSchema, UserFilterOptions, \
    UserExists, UserDoesntExist
from rna.modules.core.users.users import AbstractUserManagement
from rna.modules.users.model import User


class DBUserManagement(AbstractUserManagement):
    """DBUserManagement handles user management at the database level"""

    def update_user(self, user_id, details: UserUpdateSchema) -> bool:
        user: User = User.query.get(user_id)
        user.update(details)
        db.session.add(user)
        return True

    def delete_user(self, user_id) -> bool:
        user = User.query.filter((User.id == user_id)).one_or_none()
        if user is None:
            raise UserDoesntExist(user_id)
        db.session.delete(user)
        db.session.commit()
        return True

    def create_user(self, details: UserCreationSchema) -> User:
        existing_user = User.query.filter((User.username == details.username) | (User.email == details.email)).all()
        if len(existing_user) > 0:
            raise UserExists(details.username, details.email)
        new_user = User(username=details.username, email=details.email, first_name=details.username,
                        last_name=details.last_name)
        new_user.set_password(details.password)
        db.session.add(new_user)
        db.session.commit()
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
