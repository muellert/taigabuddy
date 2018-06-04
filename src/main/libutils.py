from flask import session
from urllib.parse import urlparse, urljoin
from flask import request, url_for


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
