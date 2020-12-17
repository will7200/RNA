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
