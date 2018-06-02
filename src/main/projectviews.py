from flask import session
from flask import request
from flask import render_template
from flask import current_app
from flask import url_for
from flask import flash
from flask import make_response
from flask import redirect
from flask import abort
from flask import g
from flask.views import MethodView
from .taiga import TaigaGlobal
from .auth import current_user
from .libutils import get_user_uuid
from .libutils import get_user_authtoken
from .libutils import set_username_cookie


class ProjectListView(MethodView):

    def __init__(self, template_name):
        self.template_name = template_name

    def render_template(self, context):
        return render_template(self.template_name, **context)

    def get(self):
        context = {}
        user = g.user
        api = current_app.config.get('API_URL')
        token = user.token
        pl = (api, token)
        context['projects'] = pl
        response = make_response(self.render_template(context))
        print("uuid: ", uuid, ", response: ", response)
        # import pdb; pdb.set_trace()
        # set_username_cookie(response, uuid)
        return response
