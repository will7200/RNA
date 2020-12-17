from sqlalchemy import or_

from rna.modules.core.auth.authentication import AuthenticationManager
from rna.modules.core.users.models import UserDoesntExist
from rna.modules.users.model import User


class DBAuthentication(AuthenticationManager):
    def authenticate(self, username, password):
        if type(username) is User:
            return username.check_password(password)
        else:
            user = User.query.filter(
                or_(User.username == username, User.email == username)
            ).one_or_none()
            if user is None:
                raise UserDoesntExist(username=username, email=username)
            return user.check_password(password)


authenticator_service: AuthenticationManager = DBAuthentication()
