
def taiga_login():
    from main import app
    from main import tc
    username = 'admin'
    password = '123123'
    api = app.config['API_URL']
    with app.test_request_context():
        tc.login(username, password)
    return api


def test_api_get_projects():
    """tests the Taiga client class for getting the list of projects
       from Taiga
    """
    import requests as req
    from main import app
    from main import tc
    api = taiga_login()
    with app.test_request_context():
        res = tc.get(api + "/projects")
        assert res is not None
        print("len(result): ", len(res.json()))
        print("result: ", res.json())
        print("current user: ", tc.user.name)
