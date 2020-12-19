from flask import Blueprint, request, jsonify
from flask.views import MethodView

from . import register_blueprint
from .models import APIException

api = Blueprint("api", __name__)


@api.route('/api/version')
def version():
    return 'v1'


class APIView(MethodView):
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


register_blueprint(api, url_prefix='/api/v1')
