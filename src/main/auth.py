import requests
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
import json
from flask.views import View
from .libutils import set_username_cookie


class TaigaAuthProblem(Exception):
    def __init__(self, orig):
        self.e_data = orig


class User:
    """What is a single user?

       A user in this context is the JSON result returned from
       successfully authenticating against Taiga.

       Relies on the session for storing the user data
    """
    auth_url = None

    def __init__(self, data=None, url=None):
        self.auth_url = self.auth_url or url
        self.data = data

    def login(self, username, password):
        self.username = username
        data = None
        if username in session:
            if  (session[username] is None or
                 '_error_message' in session[username]):
                data = self.authenticate(self.auth_url, username, password)
            else:
                data = session['username']
        else:
            data = self.authenticate(self.auth_url, username, password)
        if '_error_message' in data:
            raise TaigaAuthProblem(data)
        else:
            self.data = data
        session[username] = data

    def authenticate(self, url, username, password):
        """authenticate against a Taiga instance"""
        payload = {"username": username,
                   "password": password,
                   "type": "normal"
                   }
        r = requests.post(url, data=payload)
        cooked = r.json()
        return cooked

    @property
    def is_authenticated(self):
        return self.data['username'] in session

    def get_id(self):
        return session[self.data['username']]

    @property
    def token(self):
        return self.data['auth_token']

    @property
    def uuid(self):
        return self.data['uuid']

    @property
    def name(self):
        return self.data['username']

    @classmethod
    def set_url(cls, url):
        cls.auth_url = url

    def as_dict(self):
        return dict(data=self.data, _auth_url=self.auth_url)


def current_user():
    return g.user


def user_factory(username, password):
    """return a User object - either a new one, or a reference to
       one which already passed authentication
    """
    if username in session:
        return session[username]
    else:
        u = User()
        u.login(username, password)
        if '_error_message' in u.data:
            return None
        session[u.username] = u
        g.user = u
        return u


class LoginView(View):
    """Display the login form and log the user in."""
    methods = ("GET", "POST")

    def __init__(self, template_name):
        self.template_name = template_name

    def render_template(self, context):
        return render_template(self.template_name, **context)

    def dispatch_request(self):
        context = {'username': "", 'password': ''}
        response = None
        if request.method == 'POST':
            context.update(request.values.to_dict())
            u = user_factory(context['username'], context['password'])
            if u is not None:
                flash("User %s logged in" % u.name)
                context['debug_message'] = str(u)
                uuid = u.uuid
                g.user = u.name
                response = make_response(self.render_template(context))
                set_username_cookie(response, uuid)
            else:
                abort(401)
        if not response:
            response = make_response(self.render_template(context))
        return response


class LogoutView(View):
    """Log the current user out by deleting his session entry
       and unsetting his cookie.
    """
    methods = ("GET", "POST")

    def __init__(self, template_name):
        self.template_name = template_name

    def render_template(self, context):
        return render_template(self.template_name, **context)

    def dispatch_request(self):
        u = None
        context = {'username': "anonymous user"}
        response = None
        try:
            # import pdb; pdb.set_trace()
            u = request.cookies.get('username', None)
            current_app.logger.info("user: %s" % u)
            context = {'username': session[u]['full_name']}
            del session[u]
        except:
            flash("You were not logged in, anyway")
        response = make_response(self.render_template(context))
        # delete the cookie:
        set_username_cookie(response, '', 0)
        return response
