from flask import url_for
from .app import app
from .app import taiga_client as tc
from .auth import LoginView
from .auth import LogoutView
from .auth import login_manager
from .projectviews import ProjectListView
from .projectviews import ProjectIssuesListView
from .projectviews import ProjectSprintsListView
from .projectviews import ProjectSprintDetailsView
from .projectviews import ProjectSprintAdjustPointsView
from .projectviews import ProjectSprintsStatsView

app.add_url_rule('/', view_func=LoginView.as_view(
    'index', template_name='index.html.j2'))

app.add_url_rule('/login', view_func=LoginView.as_view(
    'login', template_name='login.html.j2'))

app.add_url_rule('/logout', view_func=LogoutView.as_view(
    'logout', template_name='logout.html.j2'))

with app.app_context():
    login_manager.login_view = url_for("login")
    login_manager.logout_view = url_for("logout")

app.add_url_rule('/projects/', view_func=ProjectListView.as_view(
    'project_list', template_name='projectlist.html.j2'))

app.add_url_rule('/projects/<int:pid>/issues', view_func=ProjectIssuesListView.as_view(
    'project_issue_list', template_name='issueslist.html.j2'))

app.add_url_rule('/projects/<int:pid>/sprint_stats', view_func=ProjectSprintsStatsView.as_view(
    'project_sprint_stats', template_name='sprintstats.html.j2'))

app.add_url_rule('/projects/<int:pid>/sprints', view_func=ProjectSprintsListView.as_view(
    'project_sprint_list', template_name='sprintlist.html.j2'))

app.add_url_rule('/sprints/<int:pid>/<int:sprintid>/details', view_func=ProjectSprintDetailsView.as_view(
    'project_sprint_details', template_name='sprintdetails.html.j2'))

app.add_url_rule('/sprints/<int:pid>/<int:sprintid>/adjust_points', view_func=ProjectSprintAdjustPointsView.as_view(
    'project_sprint_adjustpoints', template_name="sprintadjustpoints.html.j2"))
