from rna.modules import api
from rna.modules.core.remote_management.hosts import HostManagement
from rna.modules.remote_management.host_management import DBHostManagement
from rna.modules.remote_management.views import HostManagementAPI

hosts_service: HostManagement = DBHostManagement()
hosts_api = HostManagementAPI.as_view('hosts', management=hosts_service)
api.add_url_rule('/hosts', defaults={'host_id': None},
                 view_func=hosts_api, methods=['GET', ])
api.add_url_rule('/hosts', view_func=hosts_api, methods=['POST', ])
api.add_url_rule('/hosts/<int:host_id>', view_func=hosts_api,
                 methods=['GET', 'PUT', 'DELETE'])
