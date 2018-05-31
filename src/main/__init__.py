from .app import app
from .auth import LoginView
from .auth import LogoutView
from .projectviews import ProjectView

app.add_url_rule('/login', view_func=LoginView.as_view(
    'login', template_name='login.html.j2'))

app.add_url_rule('/logout', view_func=LogoutView.as_view(
    'logout', template_name='logout.html.j2'))

app.add_url_rule('/projects', view_func=ProjectView.as_view(
    'project_list', template_name='projectlist.html.j2'))


