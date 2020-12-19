from rna.modules import api, base_app
from rna.modules.core.remote_management.host_executor import HostExecutor
from rna.modules.core.remote_management.hosts import HostManagement
from rna.modules.remote_management.host_executor import CeleryHostExecutor
from rna.modules.remote_management.host_management import DBHostManagement
from rna.modules.remote_management.views import HostManagementAPI, HostListView, HostManagementView, HostManagementForm, \
    HostManagementActions

hosts_service: HostManagement = DBHostManagement()
host_executor_service: HostExecutor = CeleryHostExecutor()
hosts_api = HostManagementAPI.as_view('hosts', management=hosts_service)
api.add_url_rule('/hosts', defaults={'host_id': None},
                 view_func=hosts_api, methods=['GET', ])
api.add_url_rule('/hosts', view_func=hosts_api, methods=['POST', ])
api.add_url_rule('/hosts/<int:host_id>', view_func=hosts_api,
                 methods=['GET', 'PUT', 'DELETE'])

host_list = HostListView.as_view('hosts', management=hosts_service)
base_app.add_url_rule('/hosts', view_func=host_list, methods=['GET', ])

host_actions = HostManagementActions.as_view('host_actions', management=hosts_service)
base_app.add_url_rule('/host/<int:host_id>/<string:action>', view_func=host_actions, methods=['GET'])

host_management = HostManagementView.as_view('host', management=hosts_service)
base_app.add_url_rule('/host/<int:host_id>', view_func=host_management,
                      methods=['GET', ])
host_management_form = HostManagementForm.as_view('host_form', management=hosts_service)
base_app.add_url_rule('/form/host', view_func=host_management_form, methods=['GET', 'POST'])
