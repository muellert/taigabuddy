
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


def test_get_issues():
    """get the issues list for the project with id '2',
       which is where we have added the fields for dependency
       checking
    """
    import requests as req
    from main import app
    from main import tc
    api = taiga_login()
    with app.test_request_context():
        res = tc.get(api + "/issues?project=2")
        # import pdb; pdb.set_trace()
        assert res


def test_get_issues_chain():
    """this depends on our specific test data set.

       get an issue which has dependencies, plus the
       issues it depends on, and check whether the
       data structure is usable.
    """


def test_get_issues_ETA():
    import requests as req
    from main import app
    from main import tc
    api = taiga_login()
    with app.test_request_context():
        res = tc.get(api + "/issues/by_ref?ref=142&project=2")
        assert res
