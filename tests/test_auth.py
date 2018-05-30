from functools import reduce

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
