from datetime import datetime as dt
from datetime import date
from datetime import timedelta
import requests
from flask import session
from flask import url_for
from flask import redirect
from flask import flash
from .auth import user_factory
from .auth import TaigaAuthException
from .libutils import parse_time
from .libutils import epoch


class BaseTaigaClient:

    def __init__(self):
        self.user = None

    def init_app(self, app):
        self.app = app
        self.api = app.config['API_URL']
        # print("BaseTaigaClient.init_app(), self = ", dir(self))
        app.taiga_client = self

    def login(self, username, password=None):
        # print("BaseTaigaClient.login(%s): " % username)
        u = user_factory(username)
        assert u is not None
        if u.is_anonymous:
            u.login(username, password)
        self.user = u
        self.token = u.token

    @property
    def logged_in(self):
        # print("BaseTaigaClient.logged_in: self = ", dir(self))
        return self.user is not None

    @property
    def _auth_header(self):
        return {
            'Authorization': "Bearer %s" % self.token,
            'Content-Type': 'application/json'
        }

    def get(self, url, headers={}, **kwargs):
        hdrs = self._auth_header
        hdrs.update(headers)
        req = requests.get(url, **kwargs, headers=hdrs)
        if req.status_code == 401:
            self.app.logger.warn("Unauthorized access")
            flash("Unauthorized - you need to log in first")
            raise TaigaAuthException(req)
        return req

    def post(self, url, headers={}, **kwargs):
        hdrs = self._auth_header
        hdrs.update(headers)
        req = requests.post(url, **kwargs, headers=hdrs)
        if req.status_code == 401:
            self.app.logger.warn("Unauthorized access")
            flash("Unauthorized - you need to log in first")
            raise TaigaAuthException(req)
        return req

    def patch(self, url, headers={}, **kwargs):
        hdrs = self._auth_header
        hdrs.update(headers)
        req = requests.patch(url, **kwargs, headers=hdrs)
        if req.status_code == 401:
            self.app.logger.warn("Unauthorized access")
            flash("Unauthorized - you need to log in first")
            raise TaigaAuthException(req)
        return req


class TaigaGlobal(BaseTaigaClient):

    def autologin(self):
        print("TaigaGlobal.autologin(): session = ", session)
        if not self.logged_in:
            # print("TaigaGlobal.get_projects(): session = ", session)
            try:
                self.login(session['user_id'])
            except:
                self.login(session['username'], session['password'])

    def get_projects(self):
        """get all projects visible to the user described by 'auth'"""
        self.autologin()
        r = super().get(self.api + '/projects', )
        return r.json()

    def get_issues(self, pid):
        """get all issues for the given project"""
        self.autologin()
        r = super().get(self.api + '/issues?project=%d' % pid)
        il = [TaigaIssue(data=element) for element in r.json()]
        for issue in il:
            issue_cav = self.get_issue_custom_attribute_values(issue.id)
            if issue_cav:
                issue.update(issue_cav)
        return il

    def get_milestones(self, pid, sprintid=None):
        """get all milestones for the given project"""
        self.autologin()
        r = super().get(self.api + '/milestones?project=%d' % pid)
        mst = [TaigaMilestone(data=element) for element in r.json()]
        result = []
        if sprintid is not None:
            # weed out all the unwanted milestones:
            for m in mst:
                if m.id == sprintid:
                    result.append(m)
        else:
            result = mst
        return result

    def get_userstories(self, pid, sprintid):
        """get all user stories for the given sprint"""
        self.autologin()
        r = super().get(self.api + '/userstories?project=%d&milestone=%d' %
                        (pid, sprintid))
        usl = [TaigaUserStory(data=element) for element in r.json()]
        print("TaigaGlobal.get_userstories(): usl = ", usl)
        return usl

    def get_issue_custom_attributes(self, pid):
        """get custom attributes for issues for the given project"""
        self.autologin()
        r = super().get(self.api + '/issue-custom-attributes?project=%d' % pid)
        cal = r.json()
        return cal

    def get_issue_custom_attribute_values(self, issue_id):
        """get the custom values for the given issue id"""
        self.autologin()
        r = super().get(self.api + '/issues/custom-attributes-values/%d' %
                        issue_id)
        a_v = r.json()
        # print("custom attributes for issue %d: " % issue_id, a_v)
        if a_v['attributes_values'] == {}:
            return None
        return a_v['attributes_values']

    def get_issue_stati(self, pid):
        """get issue stati for the given project"""
        self.autologin()
        r = super().get(self.api + '/issue-statuses?project=%d' % pid)
        stati = r.json()
        return stati

    def get_issue_by_ref(self, pid, issue_ref):
        """get the issue identified by 'issue_ref'
        """
        self.autologin()
        r = super().get(self.api + '/issues/by_ref?ref=%d\&project=%d' %
                        (issue_ref, pid))
        return TaigaIssue(data=r.json())

    def reassign_userstories_and_close(self, pid, usl, sprintid=None):
        """put the user stories in 'usl' into the backlog, if
           'sprintid' is None, or assign them to the given
           sprint.
        """
        print("TaigaGlobal.reassign_userstories_and_close(): usl = ", usl)
        print("TaigaGlobal.reassign_userstories_and_close(): sprintid = ",
              sprintid)
        order = 1
        body = []
        if sprintid is None:
            newsprint = "null"
        else:
            newsprint = str(sprintid)
        for us in usl:
            body.append('{ "order": %d, "us_id": %d }' % (order, us))
            order += 1
        data = '{ "bulk_stories": [ %s ], "milestone_id": %s, '\
               '"project_id": %d }' % (", ".join(body), newsprint, int(pid))
        print("TaigaGlobal.reassign_userstories_and_close(): data = ", data)
        r = super().post(self.api + '/userstories/bulk_update_milestone',
                         data=data)
        if r.status_code != 204:  # some error occurred
            flash("Bulk user stories update failed.")
        return r


########################################################################
# classes for Taiga contents:


class ListNestedAttributesMixin:

    """this class is intended as a base class to encapsulate attribute
       access to nested 'data' objects, which usually hold a JSON that
       was generated by Taiga.
    """

    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]


class TaigaIssueCustomFields:
    """encapsulate the data types for the various custom fields

       THIS IS STRICTLY FOR OUR DEPENDENCY ENGINE, NOT FOR
       CUSTOM FIELDS IN GENERAL!

       we need this to set appropriate defaults for unset fields
       very clumsy, but we do it by the name of the field
    """
    custom_fields = []

    field_type_map = {
        'due_date': 'date',
        'depends_on': 'list',
        'est_time': 'timedelta',
        'eta': 'date',
    }

    @classmethod
    def setup(cls, data):
        cls.custom_fields = data

    def get_default(self, fieldname):
        field_type = self.field_type_map.get(fieldname, "")
        if field_type == 'date':
            return epoch
        elif field_type == 'list':
            return []
        elif field_type == 'timedelta':
            return timedelta()
        else:
            # raise ValueError("Unknown field name %s" % fieldname)
            return None

    def string_to_value(self, name, s_value):
        """convert string to the given type according to the
           definitions above
        """
        d = self.get_default(name)
        if d is None:
            return None
        v = None
        if isinstance(d, timedelta):
            v = parse_time(s_value)
        elif isinstance(d, type([1, ])):
            v = list(map(lambda x: int(x), s_value.split()))
        elif isinstance(d, date):
            v = dt.strptime(s_value, "%Y-%m-%d").date()
        else:
            raise ValueError("illegal attribute value %s for field %s" %
                             (s_value, name))
        return v

    def sanitise(self):
        """make sure all issues have our custom fields"""
        fieldnames = self.field_type_map.keys()
        for f in fieldnames:
            if f not in self.data:
                self.data[f] = self.get_default(f)


""" Sample custom attributes for issue 106:

{
 'version': 4,
 'attributes_values': {
   '26': '2018-06-22',    /* due date */
   '29': '23:00',         /* estimated effort in time */
   '27': '141'            /* list of dependencies, refers to the 'ref' field */
 },
 'issue': 106             /* id of the issue in question */
}
"""


class TaigaIssueStates:
    """encapsulate the status of an issue.

       the purpose is to be able to compute (synthesise)
       attributes on issues, like when will it be ready,
       will it be overdue etc.
    """
    issue_stati = {}

    @classmethod
    def setup(cls, array):
        """produce the array of states with index->state"""
        for element in array:
            values = {'name': element['slug'],
                      'is_closed': element['is_closed']}
            cls.issue_stati[element['id']] = values

    @property
    def is_closed(self):
        return self.issue_stati[self.status]['is_closed']

    @property
    def is_active(self):
        return self.issue_stati[self.status]['name'] in \
            ("in-progress", "ready-for-test", "new")

    @property
    def is_postponed(self):
        return self.issue_stati[self.status]['name'] == 'postponed'

    @property
    def is_waiting(self):
        return self.issue_stati[self.status]['name'] in \
            ('postponed', 'needs-info')


class TaigaIssue(TaigaIssueCustomFields,
                 TaigaIssueStates,
                 ListNestedAttributesMixin):

    pid = None

    def __init__(self, data={}):
        """add all the potentially missing custom fields, but empty"""
        self.data = data
        super().sanitise()

    @classmethod
    def configure(cls, tc, pid):
        """configure custom fields and issue stati for this project"""
        cal = {}
        stati = {}
        try:
            stati = tc.get_issue_stati(pid)
            TaigaIssueStates.setup(stati)
            cal = tc.get_issue_custom_attributes(pid)
            TaigaIssueCustomFields.setup(cal)
        except:
            flash("Some problem occurred, starting over")
            return redirect(url_for("index"))

    @property
    def id(self):
        return self.data['id']

    def index_to_field(self, s_index):
        """calculate the field name for the given index

           'field' is given as a numerical(!!) string
        """
        # print("---TaigaIssue.index_to_field(%d): cal = " %
        #       self.id, s_index)
        index = int(s_index)
        name = None
        for field in self.custom_fields:
            if field['id'] == index:
                name = field['name']
                break
        return name

    def update(self, cal):
        """set the custom attributes for this issue
           'cal' is a dictionary as being returned from Taiga
        """
        print("---TaigaIssue.update(%d): cal = " % self.id, cal)
        for index, s_value in cal.items():
            fieldname = self.index_to_field(index)
            field_value = self.string_to_value(fieldname, s_value)
            self.data[fieldname] = field_value


class TaigaMilestone(ListNestedAttributesMixin):

    pid = None

    def __init__(self, data={}):
        self.data = data

    def __str__(self):
        return "TaigaMilestone<(%s)>" % str(self.data)


class TaigaUserStory(ListNestedAttributesMixin):

    def __init__(self, data={}):
        self.data = data

    def __str__(self):
        return "TaigaUserStory: " + str(self.data)

    @property
    def allpoints(self):
        """calculate the sum of all points in this user story"""
        return self.total_points or 0
