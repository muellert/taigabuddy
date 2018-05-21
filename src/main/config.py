import os.path
import yaml

here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
configfile = "taigabuddy.yaml"


class Config:
    auth_url = None
    api_url = None
    DEBUG = True

    def load_config(self, configfile):
        """the config file is a YAML file the parameter is
        either an open file handle, or it is a string
        pointing to the configuration file.
        """
        cfh = configfile
        if isinstance(configfile, str):
            cfh = open(configfile)
        cf = yaml.load(cfh)
        return cf

    def setup(self, configfile):
        # target = os.path.join(here, "..", configfile)
        config = self.load_config(configfile)
        api_url = config['taiga']['api_url']
        auth_url = config['taiga']['auth_url']
        try:
            debug = config['taiga']['debug']
        except:
            debug = False
        self.DEBUG = debug
        self.auth_url = auth_url
        self.api_url = api_url
        return self

config = Config()

config.setup(os.path.join(here, configfile))
