from flask import session
from flask import request
from flask import render_template
from flask import current_app
from flask import url_for
from flask import flash
from flask import make_response
from flask import redirect
from flask import abort
from flask.views import MethodView
from .libtaiga import authenticate
from .libutils import get_user_authtoken
from .libutils import set_username_cookie


class ProjectView(MethodView):

    def __init__(self, template_name):
        self.template_name = template_name

    def render_template(self, context):
        return render_template(self.template_name, **context)

    def get(self):
        response = make_response(self.render_template())
        set_username_cookie('username', uuid)
        return response
