import os.path
import requests


def authenticate(url, username, password):
    payload = {"username": username,
               "password": password,
               "type": "normal"
               }
    r = requests.post(url, data=payload)
    cooked = r.json()
    return cooked

