from abc import abstractmethod, ABC
from typing import List

from rna.modules.core.remote_management.schemas import CommandDetailSchema, CommandCreationSchema, \
    CommandUpdateSchema, CommandHistorySchema


class CommandManagement(ABC):
    """Base Class for command Management"""

    @abstractmethod
    def get_command_history(self, user_identity, identifier) -> List[CommandHistorySchema]:
        """
        Gets a single command given by command_id
        :param user_identity: where owner owns command
        :param identifier: for command
        :returns: command Schema
        """

    @abstractmethod
    def get_command(self, user_identity, identifier) -> CommandDetailSchema:
        """
        Gets a single command given by command_id
        :param user_identity: where owner owns command
        :param identifier: for command
        :returns: command Schema
        """

    @abstractmethod
    def get_command_list(self, user_identity, identifier) -> List[CommandDetailSchema]:
        """
        Gets a list of commands given
        :param identifier: for command
        :param user_identity: where owner owns command
        :returns: List of command Schema
        """

    @abstractmethod
    def create_command(self, user_identity, details: CommandCreationSchema) -> CommandDetailSchema:
        """
        Create A New command
        :param user_identity: where owner owns command
        :param details: details of command to be created
        """

    @abstractmethod
    def delete_command(self, user_identity, identifier):
        """
        Delete a command by Id
        :param user_identity: where owner owns command
        :param identifier: unique command identity or id
        """

    @abstractmethod
    def update_command(self, user_identity, identifier, details: CommandUpdateSchema):
        """
        Update an Existing command
        :param user_identity: where owner owns command
        :param identifier: unique command identity or id
        :param details: command update info
        """
