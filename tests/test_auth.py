from functools import reduce

"""Uses hard-coded user account from the demo data set so far"""

def test_admin_login():
    """Testing the login process with a test client"""
    from main import app
    from main.auth import User, user_factory
    User.set_url(app.config['AUTH_URL'])
    with app.test_request_context():
        u = user_factory("admin")
        assert u
        u.login("admin", "123123")
        assert u.is_authenticated


def test_login_view():
    from main import app
    from main.auth import LoginView
    with app.test_client() as c:
        r = c.post("/login", data=dict(username="admin", password="123123"))
        assert r
        cookies = r.headers.get_all('Set-Cookie')
        assert True in ['username' in x for x in r.headers.get_all("Set-Cookie")]
