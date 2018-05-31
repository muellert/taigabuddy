from flask import session


def get_user_uuid(r, attr="username"):
    return r.cookies.get(attr, None)


def get_user_authtoken(r, username):
    uuid = get_user_uuid(r)
    u = session[uuid]
    return u['auth_token']


def set_username_cookie(resp, uuid, exp=-1):
    if exp < 0:
        resp.set_cookie('username', uuid)
    else:
        resp.set_cookie('username', uuid, exp)
