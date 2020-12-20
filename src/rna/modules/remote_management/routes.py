from rna.modules import api, base_app
from rna.modules.core.remote_management.host_commands import CommandManagement
from rna.modules.core.remote_management.host_executor import HostExecutor
from rna.modules.core.remote_management.hosts import HostManagement
from rna.modules.remote_management import DBHostManagement
from rna.modules.remote_management.services import CeleryHostExecutor, DBHostCommandManagement
from rna.modules.remote_management.views import HostManagementAPI, HostListView, HostView, HostManagementForm, \
    HostActions, CommandManagementActions

host_executor_service: HostExecutor = CeleryHostExecutor()
hosts_service: HostManagement = DBHostManagement(host_executor_service)
commands_service: CommandManagement = DBHostCommandManagement()

# API Routes
hosts_api = HostManagementAPI.as_view('hosts', management=hosts_service)
api.add_url_rule('/hosts', defaults={'host_id': None},
                 view_func=hosts_api, methods=['GET', ])
api.add_url_rule('/hosts', view_func=hosts_api, methods=['POST', ])
api.add_url_rule('/hosts/<int:host_id>', view_func=hosts_api,
                 methods=['GET', 'PUT', 'DELETE'])

# Web Routes
host_list = HostListView.as_view('hosts', management=hosts_service)
base_app.add_url_rule('/hosts', view_func=host_list, methods=['GET', ])

host_actions = HostActions.as_view('host_actions', management=hosts_service)
base_app.add_url_rule('/host/<int:host_id>/<string:action>', view_func=host_actions, methods=['GET'])

host_view = HostView.as_view('host', management=hosts_service)
base_app.add_url_rule('/host/<int:host_id>', view_func=host_view,
                      methods=['GET', ])

host_management_form = HostManagementForm.as_view('host_form', management=hosts_service)
base_app.add_url_rule('/form/host', view_func=host_management_form, methods=['GET', 'POST'])

commands_actions = CommandManagementActions.as_view('command_actions', management=hosts_service,
                                                    commands=commands_service, executor=host_executor_service)
base_app.add_url_rule('/host/<int:host_id>/command/<int:command_id>/<string:action>', view_func=commands_actions, methods=['GET'])
