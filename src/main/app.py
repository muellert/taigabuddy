from flask import Flask
from flask_login import LoginManager

try:
    from flask_debugtoolbar import DebugToolbarExtension
except:
    pass
# from flask import render_template
# from flask import request
# from flask import flash


from .config import config


def genApp():
    app = Flask(__name__, instance_relative_config=True)
    try:
        app.config.from_object(config)
    except:
        pass
    try:
        app.config.from_envvar('TAIGABUDDY_SETTINGS')
    except:
        pass
    app.logger.debug("app config: %s" % str(app.config))
    return app


app = genApp()
app.config['SECRET_KEY'] = "qeljq.48au8<F3>4aeh2liqb3hed,a i38<F4><F5>0<F5>"
toolbar = DebugToolbarExtension(app)

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def main():
    return "Hello World"
