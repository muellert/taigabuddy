import os.path
import requests
import yaml


here = os.path.dirname(os.path.abspath(__file__))
configfile = "taigabuddy.yaml"

class Config:
    auth_url = None
    api_url = None


def load_config(configfile):
    """the config file is a YAML file the parameter is
       either an open file handle, or it is a string
       pointing to the configuration file.
    """
    cfh = configfile
    if isinstance(configfile, str):
        cfh = open(configfile)
    cf = yaml.load(cfh)
    return cf


def setup(configfile=configfile):
    target = os.path.join(here, "..", configfile)
    config = load_config(target)
    api_url = config['taiga']['api_url']
    auth_url = config['taiga']['auth_url']
    config = Config()
    config.auth_url = auth_url
    config.api_url = api_url
    return config


def authenticate(url, username, password):
    payload = {"username": username,
               "password": password,
               "type": "normal"
               }
    r = requests.post(url, data=payload)
    cooked = r.json()
    if '_error_message' in cooked:
        return cooked
    token = cooked['auth_token']
    return token
