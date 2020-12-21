import os
import subprocess
import tempfile

from rna.extensions import celery, db
from rna.modules.core.remote_management.schemas import ExecuteDetails, AuthenticationMethod
from rna.modules.remote_management.models import HostCommandEvent


def build_ssh_command(details: ExecuteDetails):
    host = details.hostname
    port = []
    command = ['ssh']
    temp = None
    if details.authentication_method == AuthenticationMethod.password:
        command = ['sshpass', '-p', details.password, 'ssh']
    elif details.authentication_method == AuthenticationMethod.key_pair:
        temp = tempfile.NamedTemporaryFile(prefix="delete_key_", delete=False)
        temp.write(details.private_key.encode())
        temp.write('\n'.encode())
        temp.close()
        command.extend(['-i', temp.name])
    if details.username:
        host = f'{details.username}@{host}'
    if details.port:
        port = ['-p', f'{details.port}']
    if len(port) != 0:
        command.extend(port)
    command.extend(['-o', 'StrictHostKeyChecking=no'])
    command.append(host)
    command.append(details.command)
    return command, temp


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
    command, temp = build_ssh_command(details)
    try:
        child = subprocess.Popen(command, shell=False,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = child.communicate(timeout=30)
        # Need to Delete the temporary file
        if temp:
            os.remove(temp.name)
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
