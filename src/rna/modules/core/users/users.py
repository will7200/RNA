from abc import abstractmethod, ABC
from typing import List

from rna.modules.core.users.models import UserDetailView, UserFilterOptions, UserCreationSchema, UserUpdateSchema


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
        """
        Gets a list of users given
        :param options: available filtering options

        - username
        - TBD
        :returns: List of User View
        """
        pass

    @abstractmethod
    def create_user(self, details: UserCreationSchema) -> UserDetailView:
        """
        Create A New User
        :param details: details of user to be created
        """
        pass

    @abstractmethod
    def delete_user(self, user_id):
        """
        Delete a User by Id
        :param user_id: unique user identity or id
        """
        pass

    @abstractmethod
    def update_user(self, user_id, details: UserUpdateSchema):
        """
        Update an Existing User
        :param user_id: unique user identity or id
        :param details: user update info
        """
        pass
