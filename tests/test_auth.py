from functools import reduce

"""Uses hard-coded user account from the demo data set so far"""

def test_admin_login():
    """Testing the login process with a test client"""
    from main import app
    with app.test_client() as c:
        rv = c.post("/login", data=dict(username="admin",
                                        password="123123"))
        cookies = rv.headers.get_all('Set-Cookie')
        result = reduce((lambda x, y: x or y),
                        map((lambda x: "username" in x), cookies))
        assert result


def test_user_class():
    from main.auth import User
    from main import app
    url = app.config['AUTH_URL']
    u = User(url, username="admin", password="123123")
    assert u.token is not None and isinstance(u.token, str)
