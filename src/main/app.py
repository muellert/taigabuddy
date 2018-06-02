from flask import Flask
from flask import json
from flask import session
from flask import request
from flask import redirect
from flask import url_for


has_DTB = False
try:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension()
    has_DTB = True
except:
    pass


from .config import config
from .auth import User
from .taiga import TaigaGlobal


class TBJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, User):
            return o.as_dict()
        else:
            return json.JSONEncoder.default(self, o)


### The Factory:
def create_app(config={}, environment=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config['ENVIRONMENT'] = environment
    app.config.from_object(config)
    try:
        app.config.from_envvar('TAIGABUDDY_SETTINGS')
    except:
        pass
    return app


app = create_app(config=config)

app.config['SECRET_KEY'] = "qeljq.48au8<F3>4aeh2liqb3hed,a i38<F4><F5>0<F5>"

app.json_encoder = TBJsonEncoder

User.set_url(app.config['AUTH_URL'])

taiga_client = TaigaGlobal(app)


@app.route('/')
def main():
    u = None
    try:
        u = request.cookies['username']
    except:
        redirect(url_for('login'))
    return "Hello %s" % session[u]['full_name']


if has_DTB is True:
    toolbar.init_app(app)
