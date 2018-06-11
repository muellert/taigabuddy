import sys
import requests
from flask import session
from flask import request
from flask import current_app
from flask import url_for
from flask import flash
from flask import make_response
from flask import redirect
from flask import abort
from flask import g
from flask_login import LoginManager
from flask_login import login_user, logout_user
from .views import TemplateFinderViewBase


from flask.views import View
from .libutils import set_username_cookie


login_manager = LoginManager()


class TaigaAuthException(Exception):
    def __init__(self, orig):
        self.e_data = orig


class User:
    """What is a single user?

       A user in this context is the JSON result returned from
       successfully authenticating against Taiga.

       Relies on flask_login for storing the user data
    """
    auth_url = None

    def __init__(self, data={}, url=None):
        # print("User.__init__: data = ", data)
        if 'data' in data:
            self.data = data['data']
        else:
            self.data = data
        self.auth_url = url or self.auth_url or data['auth_url'] or ''
        if 'is_active' in self.data:
            self.is_active = data['is_active']
        else:
            self.is_active = False

    def login(self, username, password):
        self.username = username
        data = None
        if not self.is_active:
             data = self.authenticate(self.auth_url, username, password)
        # print("User.login(): data: ", data)
        if getattr(data, '_error_message', None):
            raise TaigaAuthException(data)
        else:
            self.is_active = True
            self.data = data
        # print("User.login(): is_authenticated: ", self.is_authenticated)
        session[self.data['uuid']] = self.data['username']
        session[self.data['username']] = self.data
        session['username'] = self.data['username']
        g.user = self
        return self

    def authenticate(self, url, username, password):
        """authenticate against a Taiga instance"""
        payload = {"username": username,
                   "password": password,
                   "type": "normal"
                   }
        r = requests.post(url, data=payload)
        cooked = r.json()
        # print("auth.User.authenticate(): result = ", cooked)
        # self.data = cooked
        return cooked

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return not self.is_active

    def get_id(self):
        # print("User.get_id(): self = ", self.data['uuid'])
        return self.data['uuid']

    @property
    def token(self):
        return self.data['auth_token']

    @property
    def name(self):
        # print("User.name(): self.data.name = ", self.data['full_name_display'])
        return self.data['full_name_display']

    @classmethod
    def set_url(cls, url):
        cls.auth_url = url

    def as_dict(self):
        return dict(data=self.data,
                    _auth_url=self.auth_url,
                    is_active=self.is_active)


def current_user(username=None):
    result = None
    try:
        u = g.user
        print("current_user: found ", u.data['uuid'])
        result = u
    except:
        print("current_user: nothing found")
        u = user_factory(username)
        result = u
    return result


@login_manager.user_loader
def user_factory(username):
    """return a User object - either a new one, or a reference to
       one which already passed authentication

       If the User object is new, then it is an anonymous user
       and will not be added to the session, or to 'g'.
    """
    result = None
    # print("==> user_factory(%s) called" % username)
    u = getattr(g, 'user', None)
    if u:
        # print("g.user = ", g.user.name)
        if u.data['uuid'] == username:
            result = u
        else:
            # got the wrong user from 'g'
            result = User()
    else:
        print("--> user_factory(): no g.user object")
        if username in session:
            # print("--> user_factory(): reloading user from session")
            # print("--> user_factory(): user = ", session[username])
            try:
                # username was a UUID
                result = User(data=session[session[username]])
            except:
                # username was actually a username
                result = User(data=session[username])
            g.user = result
        else:
            # user was also not in the session
            result = User()
    return result


class LoginView(TemplateFinderViewBase, View):
    """Display the login form and log the user in."""
    methods = ("GET", "POST")

    def dispatch_request(self):
        context = {'username': "", 'password': ''}
        response = None
        if request.method == 'POST':
            context.update(request.values.to_dict())
            u = User()
            u.login(context['username'], context['password'])
            if u is not None:
                print("LoginView.dispatch: before login_user():")
                # print("g = ", dir(g))
                if 'user' in g:
                    print("g.user = ", g.user)
                # print("session = ", session)
                login_user(u)
                flash("User %s logged in" % u.name)
                context['debug_message'] = str(u)
                g.user = u
                response = make_response(self.render_template(context))
                set_username_cookie(response, u.data['uuid'])
            else:
                abort(401)
            if 'next' in session:
                url = session.get('next', None)
                print("session has a next url: ", url)
                return redirect(url or url_for("project_list"))
            else:
                print("session has NO next url")
        if not response:
            response = make_response(self.render_template(context))
        return response


class LogoutView(TemplateFinderViewBase, View):
    """Log the current user out by calling flask_login's method
       and unsetting his cookie.
    """
    methods = ("GET", "POST")

    def dispatch_request(self):
        u = None
        context = {'username': "anonymous user"}
        response = None
        print(">>> LogoutView()")
        try:
            # u = request.cookies.get('username', None)
            u = current_user()
            import pdb; pdb.set_trace()
            # print("---LogoutView(): type(u) = %s" % str(type(u)))
            # print("---LogoutView(): dir(u) = %s" % str(dir(u)))
            # print("---LogoutView(): u.name = %s" % u.name)
            # print("---LogoutView(): u.items() = %s" % str(u.data.items()))
            # print("---LogoutView(): session =", session)
            # print("---LogoutView(): cookies =", request.cookies)
            current_app.logger.info("user: %s" % u)
            logout_user()
        except:
            print("---LogoutView(): raised an exception: %s" % str(sys.exc_info()[0]))
            flash("You were not logged in, anyway")
        response = make_response(self.render_template(context))
        # set_username_cookie(response, '', 0)
        return response
