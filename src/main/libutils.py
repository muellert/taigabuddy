import re
import csv
import requests as req
from datetime import datetime as dt
from datetime import date
from datetime import timedelta
from urllib.parse import urlparse, urljoin
from flask import session
from flask import request, url_for
from flask import current_app


epoch = date(1970, 1, 1)


def get_user_uuid(r, attr="username"):
    # import pdb; pdb.set_trace()
    cookie = r.cookies.get(attr, None)
    # assert cookie is not None
    print("cookie: ", cookie)
    print("all cookies: ", r.cookies)
    print("all headers: ", r.headers)
    print("session: ", session)
    return cookie

def get_user_authtoken(r, username):
    uuid = get_user_uuid(r)
    u = session[uuid]
    return u.data['auth_token']


def set_username_cookie(resp, uuid, exp=-1):
    if not uuid:
        return
    if exp < 0:
        resp.set_cookie('username', uuid)
    else:
        resp.set_cookie('username', uuid, exp)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


class Tree(dict):
    root = None
    leaves = []

    def __init__(self, node, leaves=[]):
        self.root = node
        self.leaves.extend(leaves)

    def add_child(self, node):
        self.leaves.extend(list(node))

    def as_list(self):
        result = []


def issues_waiting(il):
    sum = 0
    for i in il:
        if il[i].is_waiting:
            sum += 1
    return sum


def parse_time(s):
    """parse the given string into a timedelta object

       the purpose is to flexibly handle days and hour specs


       time formtats:

       2d 5 => 2 days, 5 hours
       2d 5:40 => 2 days, 5 hours
       23 => 23 hours (but at 8hrs/day)
    """
    result = None
    a = s.split('d')
    h = 0
    if len(a) == 2:
        d = int(a[0])
        try:
            hm = a[1].split(':')
            h = int(hm[1])
        except:
            pass
    else:
        d = 0
    # adjust for workday length (8 hrs/day)
    d += h / 8
    h = h % 8
    result = timedelta(days=d, hours=h)
    return result


def record_eta(il, ref, eta):
    il[ref].eta = max(il[ref].eta, eta)
    return eta


def calculate_ETA(il, ref, start_date=None, seen=None):
    """calculate an estimated ETA

       for 'issue' out of the issue list 'il'

       the 'issue' parameter is the value of the 'ref' attribute
       of an issue, used to find the issue
    """
    issue = il[ref]
    print("TaigaIssue.calculate_ETA(): issue.data = ", issue.data)
    if seen and ref in seen:
        current_app.logger.error("Issues cycle detection: %d in %s" %
                                 (ref, seen))
    if not seen:
        seen = set([ref])
    print("calculate_ETA(%d): eta = %s" % (ref, str(issue.eta)))
    # if ref == 117:
    #     import pdb; pdb.set_trace()
    eta = date.today()
    if start_date is None:
        start_date = epoch
    start = max(start_date, eta)
    # get out if the issue is already closed:
    if issue.is_closed:
        s = issue.finished_date
        print("   issue was closed on ", s)
        eta = dt.strptime(s.split('T')[0], "%Y-%m-%d").date()
        eta = record_eta(il, ref, eta)
        return eta
    # else try to recursively calculate a start date as a basis for
    # calculating the ETA of this issue
    deps = issue.depends_on
    if not start:
        start = eta
    if deps is not []:
        seen.add(ref)
        for d in deps:
            print("   working on dependency %d" % d)
            eta = max(eta, calculate_ETA(il, d, start, seen=seen))
    else:
        print("   no dependencies for %d" % ref)
    if issue.due_date is None:
        dd = eta + max(issue.est_time, timedelta(days=1))
    else:
        dd = issue.due_date
    eta = max(eta, dd)
    eta = record_eta(il, ref, eta)
    print("   end result eta = ", eta)
    return eta


def calculate_ETAs(il):
    for i in il:
        il[i].eta = calculate_ETA(il, i, start_date=None, seen=None)


def max_eta(il):
    """calculate the last ETA for all issues in the structure 'il'"""
    result = epoch
    for i in il:
        print("max_eta(): result = ", result)
        result = max(il[i].eta, result)
    return result


class TaigaSprintStats:
    sprintname = None
    points = 0.0
    is_closed = None

    def __init__(self, sprintname=None, points=0.0, is_closed=False):
        self.sprintname = sprintname
        self.points = points
        self.is_closed = is_closed

    def add_points(self, points):
        self.points += points

    def __repr__(self):
        return "<TaigaSprintStats(%s, %f, %s)" % (
            self.sprintname, self.points, str(self.is_closed))


def read_sprint_stats(url):
    """read the userstories stats report CSV from Taiga, which we use for
       sprint statistics (hence the fnction name)

       returns a dictionary with the Sprint titles and their total points
    """
    result = {}
    try:
        r = req.get(url)
    except:
        result = {"__message": "Could not fetch CSV. Status code: %d %s" % (r.status_code, r.reason)}

    c = csv.reader(r.text.split("\r\n"))
    h = next(c)
    headers = dict([ (h[i], i) for i in range(len(h)) ])
    # print("CSV read, headers = ", headers)
    have_sprint = 'sprint' in headers
    have_subject = 'subject' in headers
    for row in c:
        if len(row) == 0:
            continue
        # print("read_sprint_stats: row = ", row)
        if have_sprint and have_subject:
            rowtitle = row[headers['sprint']] or row[headers['subject']]
        elif have_sprint:
            rowtitle = row[headers['sprint']]
        elif have_subject:
            rowtitle = row[headers['subject']]
            if not re.match(".*\d\.\d.*", rowtitle):
                continue
        else:
            raise ValueError("Unknown table structure, doesn't have a 'sprint'"
                             " colum and also not a 'subject' column")
        if rowtitle not in result:
            tss = TaigaSprintStats(rowtitle)
            result[rowtitle] = tss
        else:
            tss = result[rowtitle]
        csv_closed = row[headers['is_closed']]
        if csv_closed.lower() == 'true':
            tss.is_closed = True
        else:
            tss.is_closed = False
        csv_points = row[headers['total-points']].strip()
        try:
            points = float(csv_points)
            result[rowtitle].add_points(points)
        except:
            pass                # column had no value
        # print(" -- read_sprint_stats: tss = ", tss)
    # print(" -- read_sprint_stats: result = ", result)
    return result
