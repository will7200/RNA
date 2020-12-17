import pydantic
from flask import jsonify, request
from flask.views import MethodView
from flask_login import login_required

from rna.modules import api
from rna.modules.core.users.models import UserDetailView, UserFilterOptions, UserUpdateSchema, UserCreationSchema
from rna.modules.models import APIException
from rna.modules.users.management import DBUserManagement, AbstractUserManagement
from rna.modules.users.model import roles_has_one


class UserManagementAPI(MethodView):
    """Controller for Exposing User Management"""

    decorators = [login_required, roles_has_one("admin", "api_user_management")]

    def __init__(self, management: AbstractUserManagement):
        self.management = management

    def dispatch_request(self, *args, **kwargs):
        meth = getattr(self, request.method.lower(), None)

        # If the request method is HEAD and we don't have a handler for it
        # retry with GET.
        if meth is None and request.method == "HEAD":
            meth = getattr(self, "get", None)

        assert meth is not None, "Unimplemented method %r" % request.method
        try:
            return meth(*args, **kwargs)
        except APIException as e:
            return jsonify(e.to_dict()), e.status_code

    def get(self, user_id):
        if user_id is None:
            return jsonify(
                UserDetailView(many=True).dump(self.management.get_user_list(UserFilterOptions(**request.args))))
        else:
            return jsonify(UserDetailView().dump(self.management.get_user(user_id)))

    def post(self):
        data = request.form or request.json
        try:
            return jsonify(UserDetailView().dump(self.management.create_user(UserCreationSchema(**data))))
        except pydantic.error_wrappers.ValidationError as e:
            return jsonify({"message": "unable to add user", "errors": e.errors()}), 400

    def delete(self, user_id):
        # delete a single user
        self.management.delete_user(user_id)
        return "", 204

    def put(self, user_id):
        # update a single user
        data = request.form
        return jsonify(self.management.update_user(user_id, UserUpdateSchema(**data)))


# manage
users_service: AbstractUserManagement = DBUserManagement()
user_api = UserManagementAPI.as_view('users', management=users_service)
api.add_url_rule('/users', defaults={'user_id': None},
                 view_func=user_api, methods=['GET', ])
api.add_url_rule('/users', view_func=user_api, methods=['POST', ])
api.add_url_rule('/users/<int:user_id>', view_func=user_api,
                 methods=['GET', 'PUT', 'DELETE'])
