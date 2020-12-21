from urllib.parse import urlparse, parse_qs

import pydantic
from flask import render_template, flash, abort, redirect, request, url_for
from flask.views import MethodView
from flask_login import login_user, logout_user, login_required, current_user

from rna.modules import logger
from rna.modules.auth.forms import UserLoginSchema
from rna.modules.core.auth.authentication import AuthenticationManager
from rna.modules.core.users.models import UserDoesntExist
from rna.modules.utils.helpers import is_safe_url


class Logout(MethodView):
    decorators = [login_required]

    def get(self):
        logout_user()
        flash("Logged out", "success")
        return redirect(url_for("app.login"))


class Login(MethodView):
    def __init__(self, users_service, authenticator: AuthenticationManager):
        self.users_service = users_service
        self.authenticator = authenticator

    def get(self):
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return render_template("auth/login.html", title="Sign In")

    def post(self):
        try:
            data = UserLoginSchema(**request.form)
        except pydantic.error_wrappers.ValidationError as e:
            flash(e.errors(), "error")
            return render_template("auth/login.html", title="Sign In"), 400

        users_service = self.users_service
        authenticator = self.authenticator
        try:
            user = users_service.get_user(data.username)
        except UserDoesntExist as e:
            logger.info('%s failed to log in', e.username)
            flash(f"User {e.username} does not exist", "error")
            return render_template("auth/login.html", title="Sign In"), 401

        if authenticator.authenticate(user, data.password):
            logger.info('%s logged in successfully', user.username)
            next_link = request.args.get('next')
            if next_link is None:
                next_link = parse_qs(urlparse(request.referrer).query).get('next', None)
                if next_link:
                    next_link = next_link[0]
            if not is_safe_url(next_link):
                return abort(400)
            if login_user(user, remember=data.remember_me):
                return redirect(next_link or url_for('index'))
            else:
                logger.warn("%s tried to login", user.username)
                flash("account is not active", "error")
                return render_template("auth/login.html", title="Sign In"), 401
        else:
            logger.info('%s failed to log in', user.username)
            flash("Invalid Username/Password Combination", "error")
            return render_template("auth/login.html", title="Sign In"), 401
