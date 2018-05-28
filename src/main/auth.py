from flask import session
from flask import request
from flask import render_template
from flask.views import View


# from flask_login import UserMixin
from .libtaiga import authenticate


class User:
    """What is a single user?

       A user in this context is the JSON result returned from
       successfully authenticating against Taiga.
    """
    auth_url = None

    def __init__(self, username, password):
        self.username = username
        data = authenticate(auth_url, username, password)
        if '_error_message' in data:
            raise ValueError("user %s: %s" % (username, data['_error_message']))
        else:
            self.data = data

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
        return self.data['uuid']

    @classmethod
    def set_url(cls, url):
        cls.auth_url = url


class LoginView(View):
    """Display the login form."""
    methods = ("GET", "POST")

    def __init__(self, template_name):
        self.template_name = template_name

    def render_template(self, context):
        return render_template(self.template_name, **context)

    def dispatch_request(self):
        context = {'username': "", 'password': ''}
        # import pdb; pdb.set_trace()
        context.update(request.values.to_dict())
        return self.render_template(context)
