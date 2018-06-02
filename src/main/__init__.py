from .app import app
from .app import taiga_client
from .auth import LoginView
from .auth import LogoutView
from .projectviews import ProjectListView

app.add_url_rule('/login', view_func=LoginView.as_view(
    'login', template_name='login.html.j2'))

app.add_url_rule('/logout', view_func=LogoutView.as_view(
    'logout', template_name='logout.html.j2'))

app.add_url_rule('/projects', view_func=ProjectListView.as_view(
    'project_list', template_name='projectlist.html.j2'))


