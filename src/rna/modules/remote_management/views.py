import pydantic
from flask import jsonify, request, render_template, flash, redirect, url_for
from flask.views import MethodView
from flask_login import login_required, current_user
from marshmallow_sqlalchemy import ModelSchema

from rna.modules.api import APIView
from rna.modules.core.remote_management.host_commands import CommandManagement
from rna.modules.core.remote_management.host_executor import HostExecutor
from rna.modules.core.remote_management.hosts import HostManagement
from rna.modules.core.remote_management.schemas import HostFilterOptions, HostCreationSchema, \
    HostUpdateSchema, HostExists, HostDoesntExist, ExecuteDetails, CommandCreationSchema, CommandUpdateSchema, \
    InvalidEncryptionPassword
from rna.modules.remote_management.forms import HostAddForm, HostEditForm, CommandAddForm, CommandEditForm
from rna.modules.users.model import roles_has_one


class HostDetailSchema(ModelSchema):
    class Meta:
        fields = ("name", "hostname", "username", "port", "ssh_options", "encrypt_authentication")


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
        self.management.update_host(current_user.id, host_id, HostUpdateSchema(**data))
        return ""


class HostListView(MethodView):
    decorators = [login_required]

    def __init__(self, management: HostManagement):
        self.management = management

    def get(self):
        return render_template("remote_management/index.html", title="Host Management",
                               hosts=self.management.get_host_list(current_user.id, HostFilterOptions()))


class HostView(MethodView):
    decorators = [login_required]

    def __init__(self, management: HostManagement):
        self.management = management

    def get(self, host_id):
        host = self.management.get_host(current_user.id, host_id)
        return render_template("remote_management/host.html", title="Host Management",
                               host=host)


class HostActions(MethodView):
    decorators = [login_required]

    def __init__(self, management: HostManagement):
        self.management = management

    def get(self, host_id, action):
        try:
            if action == 'DELETE':
                self.management.delete_host(current_user.id, host_id)
            if action == 'EDIT':
                self.management.get_host(current_user.id, host_id)
                return redirect(url_for('app.host_edit', host_id=host_id))
        except HostDoesntExist:
            flash("Host Doesn't Exist")
        return redirect(url_for('app.hosts'))


class HostAddView(MethodView):
    decorators = [login_required]

    def __init__(self, management: HostManagement):
        self.management = management

    def _render_form(self, **kwargs):
        return render_template("remote_management/forms/host_add.html", title="Add Host", **kwargs)

    def get(self):
        form = HostAddForm(request.form)
        return self._render_form(form=form)

    def post(self):
        form = HostAddForm(request.form)
        if not form.validate():
            return self._render_form(form=form), 400
        try:
            data = HostCreationSchema(**request.form)
        except pydantic.error_wrappers.ValidationError as e:
            flash(e.errors(), "error")
            return self._render_form(form=form), 400
        try:
            l = self.management.create_host(current_user.id, data)
            return render_template("remote_management/forms/host_added.html", title='Host Added', host=l), 201
        except HostExists as e:
            flash(e.to_dict(), "error")
            return self._render_form(form=form), 400


class HostEditView(MethodView):
    decorators = [login_required]

    def __init__(self, management: HostManagement):
        self.management = management

    def _render_form(self, **kwargs):
        return render_template("remote_management/forms/host_edit.html", title="Edit Host", **kwargs)

    def get(self, host_id):
        host = self.management.get_host(current_user.id, host_id)
        form = HostEditForm(request.form, obj=host)
        return self._render_form(form=form, host=host)

    def post(self, host_id):
        host = self.management.get_host(current_user.id, host_id)
        form = HostEditForm(request.form)
        if not form.validate():
            return self._render_form(form=form, host=host), 400
        try:
            data = HostUpdateSchema(**request.form)
        except pydantic.error_wrappers.ValidationError as e:
            flash(e.errors(), "error")
            return self._render_form(form=form, host=host), 400
        self.management.update_host(current_user.id, host.id, data)
        return redirect(url_for('app.host', host_id=host_id))


class CommandManagementActions(MethodView):
    decorators = [login_required]

    def __init__(self, management: HostManagement, commands: CommandManagement, executor: HostExecutor):
        self.management = management
        self.executor = executor
        self.commands = commands

    def post(self, host_id, command_id, action):
        if action == 'RUN':
            command = self.commands.get_command(current_user.id, command_id)
            form = request.form
            if 'password' not in form or form['password'] == '':
                flash("Password is empty", "error")
                host = self.management.get_host(current_user.id, command.host_id)
                return render_template('remote_management/forms/run_password.html', host=host, command=command), 400
            try:
                host = self.management.get_host(current_user.id, command.host_id, password=form['password'])
            except InvalidEncryptionPassword:
                flash("Invalid password", "error")
                host = self.management.get_host(current_user.id, command.host_id)
                return render_template('remote_management/forms/run_password.html', host=host, command=command), 400
            self.executor.execute_command(ExecuteDetails(
                command_id=command.id,
                command=command.command,
                **host.to_dict()  # type: ignore
            ))
            return redirect(url_for('app.host', host_id=host.id))
        return redirect(request.referrer)

    def get(self, host_id, command_id, action):
        if action == 'DELETE':
            command = self.commands.delete_command(current_user.id, command_id)
            return redirect(request.referrer)

        command = self.commands.get_command(current_user.id, command_id)
        if action == 'RUN':
            host = self.management.get_host(current_user.id, command.host_id)
            if host.encrypt_authentication:
                return render_template('remote_management/forms/run_password.html', host=host, command=command)
            r = self.executor.execute_command(ExecuteDetails(
                command_id=command.id,
                command=command.command,
                **host.to_dict()  # type: ignore
            ))
            return redirect(request.referrer)
        if action == 'EDIT':
            self.management.get_host(current_user.id, host_id)
            return redirect(url_for('app.command_edit', host_id=host_id, command_id=command.id))
        raise Exception(f"Unknown Action {action}")


class CommandAddView(MethodView):
    decorators = [login_required]

    def __init__(self, management: CommandManagement, host_management: HostManagement):
        self.management = management
        self.host_management = host_management

    def _render_form(self, **kwargs):
        return render_template("remote_management/forms/command_add.html", title="Add Command", **kwargs)

    def get(self, host_id):
        form = CommandAddForm(request.form)
        return self._render_form(form=form, host=self.host_management.get_host(current_user.id, host_id))

    def post(self, host_id):
        host = self.host_management.get_host(current_user.id, host_id)
        form = CommandAddForm(request.form)
        if not form.validate():
            return self._render_form(form=form, host=host), 400
        try:
            data = CommandCreationSchema(**request.form, host_id=host.id)
        except pydantic.error_wrappers.ValidationError as e:
            flash(e.errors(), "error")
            return self._render_form(form=form, host=host), 400
        self.management.create_command(current_user.id, data)
        return redirect(url_for('app.host', host_id=host_id))


class CommandEditView(MethodView):
    decorators = [login_required]

    def __init__(self, management: CommandManagement, host_management: HostManagement):
        self.management = management
        self.host_management = host_management

    def _render_form(self, **kwargs):
        return render_template("remote_management/forms/command_edit.html", title="Edit Command", **kwargs)

    def get(self, host_id, command_id):
        command = self.management.get_command(current_user.id, command_id)
        form = CommandEditForm(request.form, obj=command)
        return self._render_form(form=form, command=command,
                                 host=self.host_management.get_host(current_user.id, host_id))

    def post(self, host_id, command_id):
        host = self.host_management.get_host(current_user.id, host_id)
        command = self.management.get_command(current_user.id, command_id)
        form = CommandEditForm(request.form)
        if not form.validate():
            return self._render_form(form=form, command=command, host=host), 400
        try:
            data = CommandUpdateSchema(**request.form)
        except pydantic.error_wrappers.ValidationError as e:
            flash(e.errors(), "error")
            return self._render_form(form=form, command=command, host=host), 400
        self.management.update_command(current_user.id, command.id, data)
        return redirect(url_for('app.host', host_id=host_id))


class CommandEventView(MethodView):
    decorators = [login_required]

    def __init__(self, management: CommandManagement, host_management: HostManagement):
        self.management = management
        self.host_management = host_management

    def get(self, host_id, command_id):
        host = self.host_management.get_host(current_user.id, host_id)
        command = self.management.get_command(current_user.id, command_id)
        return render_template("remote_management/command_events.html", title="Command Event History", command=command,
                               host=host, history=self.management.get_command_history(current_user.id, command_id))
