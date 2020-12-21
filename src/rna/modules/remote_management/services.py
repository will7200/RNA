from typing import List

from celery.result import AsyncResult
from flask_login import current_user

from rna.extensions import db
from rna.modules.core.remote_management.host_commands import CommandManagement
from rna.modules.core.remote_management.host_executor import HostExecutor
from rna.modules.core.remote_management.hosts import HostManagement
from rna.modules.core.remote_management.schemas import ExecuteDetails, HostUpdateSchema, HostDoesntExist, \
    HostCreationSchema, HostExists, HostFilterOptions, CommandUpdateSchema, CommandCreationSchema, CommandDetailSchema, \
    CommandDoesntExist, CommandHistorySchema
from rna.modules.remote_management.models import Host, HostCommand, HostCommandEvent
from rna.modules.remote_management.tasks import execute_host_command


class CeleryHostExecutor(HostExecutor):
    def execute_command(self, details: ExecuteDetails):
        task = execute_host_command.delay(details.dict())
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


class DBHostManagement(HostManagement):
    """DBHostManagement handles host management at the database level"""

    def __init__(self, executor: HostExecutor):
        self.executor = executor

    def update_host(self, user_identity, identifier, details: HostUpdateSchema) -> bool:
        host: Host = Host.query.filter(Host.user_id == user_identity).filter((Host.id == identifier)).one_or_none()
        host.update(details.dict())
        db.session.add(host)
        db.session.commit()
        return True

    def delete_host(self, user_identity, identifier) -> bool:
        host = Host.query.filter(Host.user_id == user_identity).filter((Host.id == identifier)).one_or_none()
        if host is None:
            raise HostDoesntExist(identifier)
        db.session.delete(host)
        db.session.commit()
        return True

    def create_host(self, user_identity, details: HostCreationSchema) -> Host:
        existing_host = Host.query.filter(Host.user_id == user_identity).filter(Host.name == details.name).all()
        if len(existing_host) > 0:
            raise HostExists(details.hostname, details.name)
        new_host = Host(name=details.name, hostname=details.hostname, port=details.port,
                        username=details.username, ssh_options=details.ssh_options,
                        authentication_method=details.authentication_method, password=details.password,
                        private_key=details.private_key, encrypt_authentication=details.encrypt_authentication,
                        user_id=current_user.id)
        # add default "ip route" command
        new_host.commands.append(HostCommand(command="ip route"))
        db.session.add(new_host)
        db.session.commit()

        self.executor.execute_command(
            ExecuteDetails(command_id=new_host.commands[0].id, command=new_host.commands[0].command,
                           **new_host.to_dict()))
        return new_host

    def get_host(self, user_identity, identifier) -> Host:
        if type(identifier) is int:
            _found = Host.query.filter(Host.user_id == user_identity, Host.id == identifier).one_or_none()
        else:
            _found = Host.query.filter(Host.user_id == user_identity, Host.name == identifier).one_or_none()
        if _found:
            return _found
        raise HostDoesntExist(identifier)

    def get_host_list(self, user_identity, options: HostFilterOptions) -> List[Host]:
        base = Host.query.filter(Host.user_id == user_identity)
        if options.hostname:
            base = base.filter(Host.name.like(f"%{options.name}%"))
        if options.hostname:
            base = base.filter(Host.hostname.like(f"%{options.hostname}%"))
        return base.all()


class DBHostCommandManagement(CommandManagement):
    def get_command_history(self, user_identity, identifier) -> List[CommandHistorySchema]:
        return HostCommandEvent.query.join(HostCommand).join(Host).filter(
            Host.user_id == user_identity,
            HostCommand.id == identifier
        ).order_by(HostCommandEvent.completed_at.desc()).all()

    def get_command(self, user_identity, identifier) -> CommandDetailSchema:
        _found = HostCommand.query.join(Host).filter(Host.user_id == user_identity,
                                                     HostCommand.id == identifier).one_or_none()
        if _found:
            return _found
        raise CommandDoesntExist(identifier)

    def get_command_list(self, user_identity, identifier) -> List[CommandDetailSchema]:
        _found = HostCommand.query.join(Host).filter(Host.user_id == user_identity, Host.id == identifier).all()
        return _found

    def create_command(self, user_identity, details: CommandCreationSchema) -> CommandDetailSchema:
        command = HostCommand(command=details.command, host_id=details.host_id)
        db.session.add(command)
        db.session.commit()
        return command

    def delete_command(self, user_identity, identifier):
        command = HostCommand.query.join(Host).filter(Host.user_id == user_identity,
                                                      HostCommand.id == identifier).one_or_none()
        if command is None:
            raise CommandDoesntExist(identifier)
        db.session.delete(command)
        db.session.commit()
        return True

    def update_command(self, user_identity, identifier, details: CommandUpdateSchema):
        command = HostCommand.query.join(Host).filter(Host.user_id == user_identity,
                                                      HostCommand.id == identifier).one_or_none()
        command.update(details.dict())
        db.session.add(command)
        db.session.commit()
        return True
