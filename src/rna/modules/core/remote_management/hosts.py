from abc import abstractmethod, ABC
from typing import List

from rna.modules.core.remote_management.schemas import HostFilterOptions, HostCreationSchema, \
    HostUpdateSchema, HostSchema


class HostManagement(ABC):
    """Base Class for Host Management"""

    @abstractmethod
    def get_host(self, user_identity, identifier) -> HostSchema:
        """
        Gets a single host given by host_id
        :param user_identity: where owner owns host
        :param identifier: for host
        :returns: Host Schema
        """

    @abstractmethod
    def get_host_list(self, user_identity, options: HostFilterOptions) -> List[HostSchema]:
        """
        Gets a list of hosts given
        :param user_identity: where owner owns host
        :param options: available filtering options

        - hostname
        - name
        :returns: List of Host Schema
        """

    @abstractmethod
    def create_host(self, user_identity, details: HostCreationSchema) -> HostSchema:
        """
        Create A New Host
        :param user_identity: where owner owns host
        :param details: details of host to be created
        """

    @abstractmethod
    def delete_host(self, user_identity, identifier):
        """
        Delete a Host by Id
        :param user_identity: where owner owns host
        :param identifier: unique host identity or id
        """

    @abstractmethod
    def update_host(self, user_identity, identifier, details: HostUpdateSchema):
        """
        Update an Existing Host
        :param user_identity: where owner owns host
        :param identifier: unique host identity or id
        :param details: host update info
        """
