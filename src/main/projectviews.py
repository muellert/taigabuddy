from datetime import date, timedelta
from datetime import datetime as dt
from flask import session
from flask import request
from flask import current_app
from flask import url_for
from flask import flash
from flask import make_response
from flask import redirect
from flask import abort
from flask import g
from flask_login import login_required
from .auth import current_user
from .taiga import TaigaIssue
from .libutils import calculate_ETAs
from .libutils import get_user_uuid
from .libutils import issues_waiting
from .libutils import max_eta
from .gantt import issues_gantt
from .views import TemplateFinderViewBase
from .model import Log
from .model import SprintPoints
from .model import db_session

class ProjectListView(TemplateFinderViewBase):

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
            p['sprint_url'] = "/projects/%d/sprints" % p['id']
        context['projects'] = pl
        response = make_response(self.render_template(context))
        # print("uuid: ", user.get_id(), ", response: ", response)
        return response


class ProjectIssuesListView(TemplateFinderViewBase):

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


class ProjectSprintsListView(TemplateFinderViewBase):
    """list all the open sprints in this project"""

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
        msts = tc.get_milestones(pid=pid)
        today = dt.today().date()
        print("ProjectSprintsListView(): msts = ", msts)
        sprintlist = []
        usedsprints = set()
        for mst in msts:
            mst.sprint_url = '/sprint/%d/user_stories' % mst.id
            mst.startdate = mst.estimated_start
            mst.enddate = dt.strptime(mst.estimated_finish, "%Y-%m-%d").date()
            # print("ProjectSprintsListView.get(): milestone = %s" % mst)
            mst.is_open = not mst.closed
            if mst.enddate < today:
                mst.overdue = True
                if mst.is_open:
                    sprintlist.append(mst)
                    usedsprints.add(mst.id)
            else:
                mst.overdue = False
        for mst in msts:
            if mst.id not in usedsprints and mst.is_open \
               and not mst.overdue:
                sprintlist.append(mst)
                usedsprints.add(mst.id)
        for mst in msts:
            if mst.closed:
                sprintlist.append(mst)
        print("ProjectSprintsListView(): sprintlist = ", sprintlist)
        context['sprints'] = sprintlist
        context['projectid'] = pid
        response = make_response(self.render_template(context))
        return response


class ProjectSprintDetailsView(TemplateFinderViewBase):
    """list all the open user stories in this sprint"""

    @login_required
    def get(self, pid, sprintid):
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
        tc.autologin()
        today = dt.today()
        msts = tc.get_milestones(pid=pid)
        usl = tc.get_userstories(pid=pid, sprintid=sprintid)
        # print("ProjectSprintDetailsView(): msts = ", msts)
        # print("ProjectSprintsDetailsView(): usl = ", usl)
        targetsprints = []
        sprinttitle = ""
        for mst in msts:
            mst.sprint_url = '/userstories?project=%d' % mst.id
            overdue = dt.strptime(mst.estimated_finish, "%Y-%m-%d") < today
            # print("ProjectSprintsDetailsView.get(): mst.id = %d, "
            # "overdue: %s, closed: %s" % (mst.id, str(overdue), str(mst.closed)))
            if not mst.closed and mst.id != sprintid and not overdue:
                targetsprints.append(mst)
            if mst.id == sprintid:
                sprinttitle = mst.name
                print("found sprint title", sprinttitle)
                # print(" -- appended sprint %d" % mst.id)
        sprint_points = 0
        userstories_ids = []
        # print("ProjectSprintsDetailsView.get(): sprintid = %d" %
        #      sprintid)
        for us in usl:
            print("ProjectSprintsDetailsView.get(): sprint_points = %d" %
                  sprint_points)
            if not us.is_closed:
                sprint_points += us.total_points
                userstories_ids.append(us.id)
        print("ProjectSprintsDetailsView.get(): open userstories = ",
              userstories_ids)
        context['sprintid'] = sprintid
        context['sprintname'] = sprinttitle
        context['sprintpoints'] = sprint_points
        context['sprints'] = targetsprints
        context['userstories'] = usl
        context['projectid'] = pid
        session['open_userstories'] = userstories_ids
        # import pdb; pdb.set_trace()
        response = make_response(self.render_template(context))
        return response

    @login_required
    def post(self, pid, sprintid):
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
        tc.autologin()
        pc = request.path.split('/')
        pid = pc[2]
        # import pdb; pdb.set_trace()
        try:
            open_userstories = session['open_userstories']
        except:
            raise ValueError("""Called from the wrong context: """
                             """No user stories available.""")
        # don't do anything if the user pressed 'Cancel':
        if 'abort' in request.form:
            return redirect(url_for('project_sprint_list', pid=pid))
        next_sprint = request.form['next_sprint']
        if next_sprint == 'Z':
            flash("You need to make a choice for the next sprint")
            return redirect(request.referer)
        # the user selected the backlog as the target:
        if next_sprint == 'Y':
            r = tc.reassign_userstories_and_close(pid,
                                                  open_userstories,
                                                  sprintid="null")
            flash("status code: %d" % r.status_code)
            return redirect(url_for('project_sprint_list', pid=pid))
        # TBD.
        if next_sprint == 'X':
            return redirect(url_for("create_new_sprint"))
        # else:
        # the user selected the backlog as the target:
        r = tc.reassign_userstories_and_close(pid, open_userstories,
                                              next_sprint)
        flash("status code: %d" % r.status_code)
        return redirect(url_for('project_sprint_list', pid=pid))


class ProjectSprintAdjustPointsView(TemplateFinderViewBase):
    """let the user enter added or deleted points"""

    @login_required
    def get(self, pid, sprintid):
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
        tc.autologin()
        mst = tc.get_milestones(pid=pid, sprintid=sprintid)[0]
        context['sprintid'] = sprintid
        context['sprintname'] = mst.name
        context['points'] = mst.total_points
        context['projectid'] = pid
        response = make_response(self.render_template(context))
        return response

    @login_required
    def post(self, pid, sprintid):
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
        tc.autologin()
        now = dt.utcnow()
        if 'currentpoints' not in request.form:
            raise ValueError("Form submission corrupted")
        try:
            points = float(request.form['currentpoints'])
        except:
            points = 0.0
        sp = db_session.query(SprintPoints).filter_by(sprintid=sprintid).first()
        if not sp:
            sp = SprintPoints(sprintid=sprintid, who=user.name)
        start_points = sp.start_points or "unset"
        current_points = sp.current_points or "unset"
        print("start points: ", start_points,
              ", current points: ", current_points)
        logentry = "Sprint %d: User '%s' set initial sprint points to %0.2f" % (
            sprintid, user.name, points)
        if 'process_opening' in request.form:
            print(" the user pressed the record button")
            sp.start_points = points
        elif 'process_current' in request.form:
            logentry = "Sprint %d: User '%s' updated sprint points to %0.2f" % (
                sprintid, user.name, points)
            print(" the user pressed the update button")
            sp.current_points = points
        log = Log(timestamp=now, logentry=logentry)
        db_session.add(sp)
        db_session.add(log)
        db_session.commit()
        print("SprintPoints: ", sp)
        mst = tc.get_milestones(pid=pid, sprintid=sprintid)[0]
        context['sprintid'] = sprintid
        context['sprintname'] = mst.name
        context['points'] = mst.total_points
        context['start_points'] = start_points
        context['cur_points'] = current_points
        context['projectid'] = pid
        response = make_response(self.render_template(context))
        return response
