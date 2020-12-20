# Define the User profile form
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, BooleanField, SubmitField, validators

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
    private_key = StringField('Private Key', validators=[RequiredIf(authentication_method='key_pair')])
    user_password = StringField('Current Password', default=None, validators=[
        RequiredIf(encrypt_authentication=True, exclude=lambda form: form['authentication_method'].data == '')])
    submit = SubmitField('Create')


class HostEditForm(FlaskForm):
    hostname = StringField('Hostname', validators=[validators.DataRequired('Hostname is required')])
    port = IntegerField('Port', validators=[validators.NumberRange(min=1, max=65535)], default=22)
    username = StringField('Username', default=None)
    password = StringField('Password', default=None, validators=[RequiredIf(authentication_method='password')])
    ssh_options = StringField('SSH Options')
    authentication_method = SelectField('Authentication Method',
                                        choices=[('', ''), ('password', "Password"), ('key_pair', "Key Pair")],
                                        default='')
    encrypt_authentication = BooleanField('Encrypt Authentication Method')
    private_key = StringField('Private Key', validators=[RequiredIf(authentication_method='key_pair')])
    user_password = StringField('Current Password', default=None, validators=[
        RequiredIf(encrypt_authentication=True, exclude=lambda form: form['authentication_method'].data == '')])
    submit = SubmitField('Update')
