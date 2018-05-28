from .app import app
from .auth import LoginView


app.add_url_rule('/login', view_func=LoginView.as_view(
    'login_page', template_name='login.html.j2'))


