from flask import Flask

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
toolbar = DebugToolbarExtension(app)



@app.route('/')
def main():
    return "Hello World"
