from datetime import datetime as dt
from datetime import date
from datetime import timedelta
import requests
from flask import current_app
from flask import session
from .auth import current_user
from .auth import user_factory


class BaseTaigaClient:

    def __init__(self):
        # print("BaseTaigaClient.__init__()")
        self.user = None

    def init_app(self, app):
        self.app = app
        self.api = app.config['API_URL']
        # print("BaseTaigaClient.init_app(), self = ", dir(self))
        app.taiga_client = self

    def login(self, username):
        u = user_factory(username)
        assert u is not None
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
        return requests.get(url, **kwargs, headers=hdrs)
        
    def post(self, url, headers={}, **kwargs):
        hdrs = self._auth_header
        hdrs.update(headers)
        return requests.post(url, **kwargs, headers=hdrs)


class TaigaGlobal(BaseTaigaClient):

    def autologin(self):
        if not self.logged_in:
            # print("TaigaGlobal.get_projects(): session = ", session)
            self.login(session['user_id'])

    def get_projects(self):
        """get all projects visible to the user described by 'auth'"""
        self.autologin()
        r = super().get(self.api + '/projects', )
        return r.json()

    def get_issues(self, pid):
        """get all issues for the given project"""
        self.autologin()
        r = super().get(self.api + '/issues?project=%d' % pid, )
        self.get_issue_custom_attributes(pid)
        return [TaigaIssue(data=element) for element in r.json()]

    def get_issue_custom_attributes(self, pid):
        """get custom attributes for issues for the given project"""
        self.autologin()
        r = super().get(self.api + '/issue-custom-attributes')
        cal = r.json()
        print("---TaigaGlobal.get_issue_custom_attributes(): cal=", cal)
        result = [field for field in cal if field['project'] == pid]
        print("TaigaGlobal.get_issue_custom_attributes(): result=", result)
        return result

    def get_issue_custom_attribute_values(self, issue_id):
        """get the custom values for the given issue id"""
        self.autologin()
        print("get_issue_custom_attribute_values(%d)" % issue_id)
        r = super().get(self.api + '/issues/custom-attributes-values/%d' % issue_id)
        a_v = r.json()
        print("custom attributes for issue %d: " % issue_id, a_v)
        if a_v['attributes_values'] == {}:
            return None
        return a_v['attributes_values']


class TaigaIssueCustomFields:
    """encapsulate the data types for the various custom fields

       we need this to set appropriate defaults for unset fields
       very clumsy, but we do it by the name of the field
    """

    field_type_map = {
        'due_date': 'date',
        'depends_on': 'list',
        'est_time': 'timedelta',
    }

    def get_default(self, fieldname):
        field_type = self.field_type_map.get(fieldname, "")
        if field_type == 'date':
            return date(1970, 1, 1)
        elif field_type == 'list':
            return []
        elif field_type == 'timedelta':
            return timedelta()
        else:
            raise ValueError("Unknown field name %s" % fieldname)

    def sanity_check(self):
        fieldnames = self.field_type_map.keys()
        result = True
        for f in fieldnames:
            result = result and f in self.data
        return result

    def string_to_value(self, name, s_value):
        """convert string to the given type according to the
           definitions above
        """
        d = self.get_default(name)
        v = None
        if isinstance(d, timedelta):
            # needs proper parsing for days and hours
            v = int(s_value)
        elif isinstance(d, type([1, ])):
            v = s_value.split()
        elif isinstance(d, date):
            v = dt.strptime(s_value, "%Y-%m-%d").date()
        else:
            raise ValueError("illegal attribute value %s for field %s" %
                             (s_value, name))
        return v


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

class TaigaIssue(TaigaIssueCustomFields):

    custom_fields = []

    def __init__(self, data={}):
        """add all the potentially missing custom fields, but empty"""
        for f in self.custom_fields:
            name = f['name']
            if name not in data:
                data[name] = self.get_default(name)
        self.data = data

    @classmethod
    def set_custom_fields(cls, fields):
        cls.custom_fields = fields

    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]
        raise

    def index_to_field(self, s_index):
        """calculate the field name for the given index

           'field' is given as a numerical(!!) string
        """
        print("---TaigaIssue.index_to_field(%d): cal = " % self.id, s_index)
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

    def calculate_ETA(self, start_date=None):
        """calculate an estimated ETA"""


    @property
    def id(self):
        return self.data['id']


def calculate_dependencies(issue_list):
    """Calculate a dependency graph for the items given in the list 'l'

       The items need to have a field 'depends_on'
    """
