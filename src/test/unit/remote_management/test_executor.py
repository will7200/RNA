from rna.modules.core.remote_management.schemas import ExecuteDetails, AuthenticationMethod
from rna.modules.remote_management.tasks import build_ssh_command


def test_build_ssh_command():
    command = build_ssh_command(ExecuteDetails(
        id=1, name='localhost', hostname='localhost', command_id=1, command='ip route'
    ))
    assert ' '.join(command) == "ssh -p 22 -o StrictHostKeyChecking=no localhost ip route"
    command = build_ssh_command(ExecuteDetails(
        id=1, name='localhost', hostname='localhost', command_id=1, command='ip route',
        authentication_method=AuthenticationMethod.password, password='password'
    ))
    assert ' '.join(command) == "sshpass -p password ssh -p 22 -o StrictHostKeyChecking=no localhost ip route"

    command = build_ssh_command(ExecuteDetails(
        id=1, name='localhost', hostname='localhost', command_id=1, command='ip route',
        authentication_method=AuthenticationMethod.password, password='password', username='root'
    ))
    assert ' '.join(command) == "sshpass -p password ssh -p 22 -o StrictHostKeyChecking=no root@localhost ip route"
