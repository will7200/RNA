import subprocess

from rna.extensions import celery, db
from rna.modules.core.remote_management.schemas import ExecuteDetails, AuthenticationMethod
from rna.modules.remote_management.models import HostCommandEvent


def build_ssh_command(details: ExecuteDetails):
    host = details.hostname
    port = []
    command = ['ssh']
    if details.authentication_method == AuthenticationMethod.password:
        command = ['sshpass', '-p', details.password, 'ssh']
    if details.username:
        host = f'{details.username}@{host}'
    if details.port:
        port = ['-p', f'{details.port}']
    if len(port) != 0:
        command.extend(port)
    command.extend(['-o', 'StrictHostKeyChecking=no'])
    command.append(host)
    command.append(details.command)
    return command


def deserialize_into(argument):
    def decorator(function):
        def wrapper(self, arg, *args, **kwargs):
            arg = argument(**arg)
            result = function(self, arg, *args, **kwargs)
            return result

        return wrapper

    return decorator


@celery.task(bind=True, queue='execute_host_command')
@deserialize_into(ExecuteDetails)
def execute_host_command(self, details: ExecuteDetails):
    try:
        child = subprocess.Popen(build_ssh_command(details), shell=False,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = child.communicate(timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        event = HostCommandEvent(result=str(e), host_command_id=details.command_id,
                                 exit_code=-1, guid=self.request.id)
        db.session.add(event)
        db.session.commit()
        return str(e)
    stdout, stderr = result
    # noinspection PyTypeChecker
    event = HostCommandEvent(result=stdout.decode() + '\n' + stderr.decode(), host_command_id=details.command_id,
                             exit_code=child.returncode, guid=self.request.id)
    db.session.add(event)
    db.session.commit()
    return stdout.decode() + '\n' + stderr.decode()
