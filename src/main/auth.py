from flask import session
from flask import request
from flask import render_template
from flask import current_app
from flask import url_for
from flask import flash
from flask import make_response
from flask import redirect
from flask import abort
from flask.views import View
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
            raise ValueError("user %s: %s" % (username,
                                              data['_error_message']))
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
            r = authenticate(current_app.config['AUTH_URL'],
                             context['username'],
                             context['password'])
            print("after authentication: ", r)
            if r is not None:
                flash("User %s logged in" % r['full_name'])
                context['debug_message'] = str(r)
                uuid = r['uuid']
                session[uuid] = r
                response = make_response(self.render_template(context))
                response.set_cookie('username', uuid)
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
        response.set_cookie('username', '', 0)
        return response
