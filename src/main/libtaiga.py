import os.path
import requests


here = os.path.dirname(os.path.abspath(__file__))
configfile = "taigabuddy.yaml"


def authenticate(url, username, password):
    payload = {"username": username,
               "password": password,
               "type": "normal"
               }
    r = requests.post(url, data=payload)
    cooked = r.json()
    return cooked
