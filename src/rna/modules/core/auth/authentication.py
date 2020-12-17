from abc import abstractmethod, ABC


class AuthenticationManager(ABC):
    """
    Used to handle the authentication process. A default is implemented,
    however this interface is provided in case alternative flows are needed.
    If a user successfully passes through the entire authentication process,
    then it should be returned to the caller.
    """

    @abstractmethod
    def authenticate(self, identifier, secret):
        """
        This method is abstract.
        :param str identifier: An identifier for the user, typically this is
            either a username or an email.
        :param str secret: A secret to verify the user is who they say they are
        :returns: A fully authenticated but not yet logged in user
        :rtype: :class:`User<flaskbb.user.models.User>`
        """
        pass
