# Define the User profile form
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, BooleanField, SubmitField, validators, TextAreaField

from rna.modules.core.remote_management.schemas import AuthenticationMethod
from rna.modules.core.utils.form_validators import RequiredIf


class HostAddForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired('name is required')])
    hostname = StringField('Hostname', validators=[validators.DataRequired('Hostname is required')])
    port = IntegerField('Port', validators=[validators.NumberRange(min=1, max=65535)], default=22)
    username = StringField('Username', default=None)
    password = StringField('Password', default=None, validators=[RequiredIf(authentication_method='password')])
    ssh_options = StringField('SSH Options')
    authentication_method = SelectField('Authentication Method',
                                        choices=[('', ''), ('password', "Password"), ('key_pair', "Key Pair")],
                                        default='')
    encrypt_authentication = BooleanField('Encrypt Authentication Method')
    private_key = TextAreaField('Private Key', validators=[RequiredIf(authentication_method='key_pair')])
    user_password = StringField('Current Password', default=None, validators=[
        RequiredIf(encrypt_authentication=True, exclude=lambda form: form['authentication_method'].data == '')])
    submit = SubmitField('Create')


def coerce_to_string(enum):
    def coerce(name):
        if isinstance(name, enum):
            return name.value
        return name

    return coerce


class HostEditForm(FlaskForm):
    hostname = StringField('Hostname', validators=[validators.DataRequired('Hostname is required')])
    port = IntegerField('Port', validators=[validators.NumberRange(min=1, max=65535)], default=22)
    username = StringField('Username', default=None)
    password = StringField('Password', default=None, validators=[RequiredIf(authentication_method='password')])
    ssh_options = StringField('SSH Options')
    authentication_method = SelectField('Authentication Method',
                                        choices=[('', ''), ('password', "Password"), ('key_pair', "Key Pair")],
                                        coerce=coerce_to_string(AuthenticationMethod))
    encrypt_authentication = BooleanField('Encrypt Authentication Method')
    private_key = TextAreaField('Private Key', validators=[RequiredIf(authentication_method='key_pair')])
    user_password = StringField('Encryption Password', default=None, validators=[
        RequiredIf(encrypt_authentication=True, exclude=lambda form: form['authentication_method'].data == '')])
    submit = SubmitField('Update')


class CommandAddForm(FlaskForm):
    command = StringField('Command', validators=[validators.DataRequired('Command is required')])
    submit = SubmitField('Save')


class CommandEditForm(CommandAddForm):
    submit = SubmitField('Update')
