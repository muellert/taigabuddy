from flask import session
from flask import request
from flask import render_template
from flask import current_app
from flask import url_for
from flask import flash
from flask import make_response
from flask import redirect
from flask import abort
from flask import g
from flask.views import MethodView
from flask_login import login_required
from .auth import current_user
from .libutils import get_user_uuid
from .taiga import calculate_dependencies
from .taiga import TaigaIssue

class ProjectListView(MethodView):

    def __init__(self, template_name):
        self.template_name = template_name

    def render_template(self, context):
        return render_template(self.template_name, **context)

    @login_required
    def get(self):
        context = {}
        user = None
        try:
            user = g.user
        except:
            c = get_user_uuid(request)
            user = current_user(c)
        api = current_app.config.get('API_URL')
        token = user.token
        pl = current_app.taiga_client.get_projects()
        # print("ProjectListView.get(): pl = ", pl)
        for p in pl:
            p['issue_url'] = "/projects/%d/issues" % p['id']
        context['projects'] = pl
        response = make_response(self.render_template(context))
        # print("uuid: ", user.get_id(), ", response: ", response)
        return response


class ProjectIssuesListView(MethodView):

    def __init__(self, template_name):
        self.template_name = template_name

    def render_template(self, context):
        return render_template(self.template_name, **context)

    @login_required
    def get(self, pid):
        context = {}
        user = None
        try:
            user = g.user
        except:
            c = get_user_uuid(request)
            user = current_user(c)
        api = current_app.config.get('API_URL')
        token = user.token
        tc = current_app.taiga_client
        cal = tc.get_issue_custom_attributes(pid=pid)
        TaigaIssue.set_custom_fields(cal)
        il = tc.get_issues(pid=pid)
        # print("ProjectIssuesListView.get(): issues = ", il)
        context['issues'] = il
        for issue in il:
            issue_cav = tc.get_issue_custom_attribute_values(issue.id)
            if issue_cav:
                issue.update(issue_cav)
        context['dependencies'] = calculate_dependencies(il)
        context['projectid'] = pid
        response = make_response(self.render_template(context))
        # print("uuid: ", user.get_id(), ", response: ", response)
        return response
