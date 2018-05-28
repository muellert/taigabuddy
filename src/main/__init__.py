from .app import app
from .auth import LoginView

# import pdb; pdb.set_trace()
app.add_url_rule('/login', view_func=LoginView.as_view(
    'login_page', template_name='login.html.j2'))


