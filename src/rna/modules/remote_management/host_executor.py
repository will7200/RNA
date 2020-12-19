import subprocess

from celery.result import AsyncResult

from rna.extensions import celery
from rna.modules.core.remote_management.host_executor import HostExecutor
from rna.modules.core.remote_management.schemas import ExecuteDetails


@celery.task(bind=True)
def execute_host_command(hostname, command):
    return subprocess.Popen("ssh {host} {cmd}".format(host=hostname, cmd=command), shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(timeout=30)


class CeleryHostExecutor(HostExecutor):
    def execute_command(self, details: ExecuteDetails):
        task = execute_host_command(details.hostname, details.command)
        print(task)
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
