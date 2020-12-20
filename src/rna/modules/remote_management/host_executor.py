from celery.result import AsyncResult

from rna.modules.core.remote_management.host_executor import HostExecutor
from rna.modules.core.remote_management.schemas import ExecuteDetails
from rna.modules.remote_management.tasks import execute_host_command


class CeleryHostExecutor(HostExecutor):
    def execute_command(self, details: ExecuteDetails):
        task = execute_host_command.delay(details.hostname, details.command, details.host_command_id)
        return task.id

    def retrieve_execution(self, identifier):
        res = AsyncResult(identifier)
        try:
            result = res.get(timeout=1)
            data = {"task_id": identifier,
                    "data"   : {"result": result, **res._get_task_meta()}}
        except TimeoutError:
            data = {"task_id": identifier,
                    "data"   : {"running": True, **res._get_task_meta()}}
        except Exception as e:
            t = res._get_task_meta()
            if isinstance(t['result'], BaseException):
                res = t.pop('result')
                t['result'] = str(res)
            data = {"task_id": identifier,
                    "data"   : {
                        "error": e.args[0],
                        **t}
                    }
        return data
