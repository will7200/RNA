import pydantic
from flask import request, jsonify
from flask_login import login_required

from rna.modules.api import APIView
from rna.modules.core.users.models import UserDetailView, UserFilterOptions, UserUpdateSchema, UserCreationSchema
from rna.modules.core.users.users import AbstractUserManagement
from rna.modules.users.model import roles_has_one


class UserManagementAPI(APIView):
    """Controller for Exposing User Management"""

    decorators = [login_required, roles_has_one("admin", "api_user_management")]

    def __init__(self, management: AbstractUserManagement):
        self.management = management

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
