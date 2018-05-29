from .app import app
from .auth import LoginView
from .auth import LogoutView

app.add_url_rule('/login', view_func=LoginView.as_view(
    'login', template_name='login.html.j2'))

app.add_url_rule('/logout', view_func=LogoutView.as_view(
    'logout', template_name='logout.html.j2'))


