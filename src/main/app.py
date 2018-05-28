from flask import Flask

has_DTB = False
try:
    from flask_debugtoolbar import DebugToolbarExtension
    # toolbar = DebugToolbarExtension()
    # has_DTB = True
except:
    pass

from .config import config
from .auth import User


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

# app = create_app(config=config.data())
app = create_app(config=config)

app.config['SECRET_KEY'] = "qeljq.48au8<F3>4aeh2liqb3hed,a i38<F4><F5>0<F5>"

User.set_url(app.config['AUTH_URL'])

@app.route('/')
def main():
    return "Hello World"


# if has_DTB is True:
#    toolbar.init_app(app)
