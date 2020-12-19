import pydantic
from flask import jsonify, request, render_template, flash, redirect, url_for
from flask.views import MethodView
from flask_login import login_required, current_user

from rna.modules.api import APIView
from rna.modules.core.remote_management.hosts import HostManagement
from rna.modules.core.remote_management.schemas import HostDetailSchema, HostFilterOptions, HostCreationSchema, \
    HostUpdateSchema, HostExists, HostDoesntExist
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


class HostListView(MethodView):
    decorators = [login_required]

    def __init__(self, management: HostManagement):
        self.management = management

    def get(self):
        return render_template("remote_management/index.html", title="Host Management",
                               hosts=self.management.get_host_list(current_user.id, HostFilterOptions()))


class HostManagementView(MethodView):
    decorators = [login_required]

    def __init__(self, management: HostManagement):
        self.management = management

    def get(self, host_id):
        return render_template("remote_management/host.html", title="Host Management",
                               host=self.management.get_host(current_user.id, host_id))


class HostManagementActions(MethodView):
    decorators = [login_required]

    def __init__(self, management: HostManagement):
        self.management = management

    def get(self, host_id, action):
        try:
            if action == 'delete':
                self.management.delete_host(current_user.id, host_id)
        except HostDoesntExist:
            flash("Host Doesn't Exist")
        return redirect(url_for('app.hosts'))


class HostManagementForm(MethodView):
    decorators = [login_required]

    def __init__(self, management: HostManagement):
        self.management = management

    def _render_form(self, **kwargs):
        return render_template("remote_management/forms/host_add_form.html", title="Add Host", **kwargs)

    def get(self):
        return self._render_form(form={})

    def post(self):
        try:
            data = HostCreationSchema(**request.form)
        except pydantic.error_wrappers.ValidationError as e:
            flash(e.errors(), "error")
            return self._render_form(form=request.form)
        try:
            l = self.management.create_host(current_user.id, data)
            return render_template("remote_management/forms/host_added.html", title='Host Added', host=l)
        except HostExists as e:
            flash(e.to_dict(), "error")
            return self._render_form(form=request.form)
