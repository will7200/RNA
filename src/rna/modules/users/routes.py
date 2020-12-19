from rna.modules import api
from rna.modules.users.management import DBUserManagement, AbstractUserManagement
from rna.modules.users.views import UserManagementAPI

# manage
users_service: AbstractUserManagement = DBUserManagement()
user_api = UserManagementAPI.as_view('users', management=users_service)
api.add_url_rule('/users', defaults={'user_id': None},
                 view_func=user_api, methods=['GET', ])
api.add_url_rule('/users', view_func=user_api, methods=['POST', ])
api.add_url_rule('/users/<int:user_id>', view_func=user_api,
                 methods=['GET', 'PUT', 'DELETE'])
