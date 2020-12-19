from typing import List

from flask_login import current_user

from rna.extensions import db
from rna.modules.core.remote_management.hosts import HostManagement
from rna.modules.core.remote_management.schemas import HostUpdateSchema, HostCreationSchema, HostFilterOptions, \
    HostExists, HostDoesntExist
from rna.modules.remote_management.models import Host


class DBHostManagement(HostManagement):
    """DBHostManagement handles host management at the database level"""

    def update_host(self, user_identity, identifier, details: HostUpdateSchema) -> bool:
        host: Host = Host.query.filter(Host.user_id == user_identity).get(identifier)
        host.update(details)
        return True

    def delete_host(self, user_identity, identifier) -> bool:
        host = Host.query.filter(Host.user_id == user_identity).filter((Host.id == identifier)).one_or_none()
        if host is None:
            raise HostDoesntExist(identifier)
        db.session.delete(host)
        return True

    def create_host(self, user_identity, details: HostCreationSchema) -> Host:
        existing_host = Host.query.filter(Host.user_id == user_identity).filter(Host.name == details.name).all()
        if len(existing_host) > 0:
            raise HostExists(details.hostname, details.name)
        new_host = Host(name=details.name, hostname=details.hostname, port=details.port,
                        username=details.username, ssh_options=details.ssh_options,
                        authentication_method=details.authentication_method, password=details.authentication_method,
                        private_key=details.private_key, encrypt_authentication=details.encrypt_authentication,
                        user_id=current_user.id)
        db.session.add(new_host)
        return new_host

    def get_host(self, user_identity, identifier) -> Host:
        if type(identifier) is int:
            _found = Host.query.filter(Host.user_id == user_identity).get(identifier)
        else:
            _found = Host.query.filter(Host.user_id == user_identity).filter(Host.name == identifier).one_or_none()
        if _found:
            return _found
        raise HostDoesntExist(identifier)

    def get_host_list(self, user_identity, options: HostFilterOptions) -> List[Host]:
        base = Host.query
        if options.hostname:
            base = base.filter(Host.name.like(f"%{options.name}%"))
        if options.hostname:
            base = base.filter(Host.hostname.like(f"%{options.hostname}%"))
        return base.all()
