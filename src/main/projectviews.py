from datetime import date, timedelta
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
from .taiga import TaigaIssue
# from .libutils import create_graph
from .libutils import calculate_ETAs
from .libutils import get_user_uuid
from .libutils import issues_waiting
from .libutils import max_eta
from .gantt import issues_gantt

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
        issues_graph_css_class="taigagantt"
        try:
            user = g.user
        except:
            c = get_user_uuid(request)
            user = current_user(c)
        api = current_app.config.get('API_URL')
        token = user.token
        tc = current_app.taiga_client
        tc.autologin()
        TaigaIssue.configure(tc, pid)
        il = tc.get_issues(pid=pid)
        # print("ProjectIssuesListView.get(): il = ", il)
        ig = dict(map(lambda x: (x.ref, x), il))
        # print("ProjectIssuesListView.get() after map(): il = ", il)
        # now calculate the ETAs for all issues:
        calculate_ETAs(ig)
        last_eta = max_eta(ig)
        tomorrow = date.today() + timedelta(days=1)
        flash("ETA for the last issue: " + str(last_eta))
        waiting = issues_waiting(ig)
        if waiting > 0:
            flash("There are %d issues waiting" % waiting)
        active = [ig[i] for i in ig if not ig[i].is_closed]
        aig = dict(map(lambda x: (x.ref, x), active))
        ganttchart = issues_gantt(aig)
        context['issues_graph_css_class'] = issues_graph_css_class
        context['graph'] = ganttchart
        context['issues'] = active
        context['tomorrow'] = tomorrow
        context['projectid'] = pid
        response = make_response(self.render_template(context))
        return response
