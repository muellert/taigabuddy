import requests
from flask import current_app
from .auth import user_factory

class BaseTaigaClient:

    def __init__(self):
        self.api = current_app.config['API_URL']
        self.user = None

    def login(self, username, password):
        u = user_factory(username, password)
        self.user = u
        self.token = u.token

    @property
    def logged_in(self):
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

    def __init__(self, app):
        self.app = app

    def login(self, username, password):
        super().login(username, password)

    def get_projects(self):
        """get all projects visible to the user described by 'auth'"""
        if self.logged_in:
            r = super().get(apiurl + '/projects', )
            return r.json()
        else:
            return None
