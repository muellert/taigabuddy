


def test_api_get_projects():
    """tests the Taiga client class for getting the list of projects
       from Taiga
    """
    import requests as req
    from main import app
    from main.taiga import TaigaGlobal
    username = 'admin'
    password = '123123'
    api = app.config['API_URL']
    with app.test_request_context():
        tg = TaigaGlobal(app, username, password)
        assert tg is not None
        res = tg.get(api + "/projects")
        assert res is not None
        print("len(result): ", len(res.json()))
        print("result: ", res.json())
