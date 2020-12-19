import pydantic
from flask import jsonify, request
from flask_login import login_required, current_user

from rna.modules.api import APIView
from rna.modules.core.remote_management.hosts import HostManagement
from rna.modules.core.remote_management.schemas import HostDetailSchema, HostFilterOptions, HostCreationSchema, \
    HostUpdateSchema
from rna.modules.users.model import roles_has_one


class HostManagementAPI(APIView):
    decorators = [login_required, roles_has_one("admin", "api_host_management")]

    def __init__(self, management: HostManagement):
        self.management = management

    def get(self, host_id):
        if host_id is None:
            return jsonify(
                HostDetailSchema(many=True).dump(
                    self.management.get_host_list(current_user.id, HostFilterOptions(**request.args))))
        else:
            return jsonify(HostDetailSchema().dump(self.management.get_host(host_id, current_user.id)))

    def post(self):
        data = request.form or request.json
        try:
            return jsonify(HostDetailSchema().dump(
                self.management.create_host(current_user.id, HostCreationSchema(**data)))), 201
        except pydantic.error_wrappers.ValidationError as e:
            return jsonify({"message": "unable to add host", "errors": e.errors()}), 400

    def delete(self, host_id):
        # delete a single host
        self.management.delete_host(current_user.id, host_id)
        return "", 204

    def put(self, host_id):
        # update a single host
        data = request.form
        return jsonify(self.management.update_host(current_user.id, host_id, HostUpdateSchema(**data)))
