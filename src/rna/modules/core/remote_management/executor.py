from abc import abstractmethod, ABC

from rna.modules.core.remote_management.schemas import ExecuteDetails, ExecutedDetails


class Executor(ABC):
    """Base Class that handles remote execution on remote host"""

    @abstractmethod
    def execute_command(self, details: ExecuteDetails) -> str:
        """
        Execute command on remote host
        :param details:
        :return: unique identifier of job submitted
        """
        pass

    @abstractmethod
    def retrieve_execution(self, identifier) -> ExecutedDetails:
        """
        Retrieve information of submitted execution command
        :param identifier:
        :return: ExecutedDetails
        """
        pass
