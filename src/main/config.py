import os.path
import yaml
from urllib.parse import urlencode


here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
configfile = "taigabuddy.yaml"
dbconfig = "taigabuddy_db.yaml"
configfile2 = "taigabuddy_local.yaml"


class Config:
    """Load the configuration from a YAML file and set attributes
       on an instance of this object.
    """

    def __init__(self):
        self.config = {}

    def _load_config(self, configfile):
        """the config file is a YAML file the parameter is
        either an open file handle, or it is a string
        pointing to the configuration file.
        """
        cfh = configfile
        if isinstance(configfile, str):
            cfh = open(configfile)
        cf = yaml.load(cfh)
        cfh.close()
        return cf

    def setup(self, configfile):
        config = self._load_config(configfile)
        print("Config.setup(%s): config = %s" % (configfile, str(config)))
        if not config:
            return
        for k, v in config.items():
            u = k.upper()
            self.__setattr__(u, v)
        print("Config.setup(%s): attributes = %s" % (configfile, dir(self)))
        if not (hasattr(self, 'API_URL') and hasattr(self, 'AUTH_URL')):
            raise ValueError("You must specify a Taiga instance to access")

    def dbsetup(self, params={}):
        """get a database set up. separated from setup() in order to allow for
           overriding during test.

           If 'params' is being passed in, it needs to have the full database
           configuration inside. Otherwise, the database configuration is taken
           from "magic" attributes of 'self'.
        """
        db_url = None
        if params != {}:
            if 'db_url' in params:
                db_url = params['db_url']
            elif params['db_driver'] == 'sqlite':
                db_url = "sqlite://%s" % params['db_path']
            else:
                # database is not SQLite:
                password = urlencode("", params['db_pass'])[1:]
                db_url = "%s@%s:%s@%s:%s/%s" % \
                         (params['db_driver'], params['db_user'],
                          password, params['db_host'],
                          params['db_port'], params['db_name'])
        else:
            # take the db configuration from 'self':
            password = urlencode("", self.db_pass)[1:]
            db_url = "%s@%s:%s@%s:%s/%s" % \
                     (self.db_driver, self.db_user,
                      password, self.db_host,
                      self.db_port, self.db_name)


config = Config()

config.setup(os.path.abspath(os.path.join(here, configfile)))

dbconf = os.path.abspath(os.path.join(here, dbconfig))
if os.path.exists(dbconf):
    config.setup(dbconf)

localconf = os.path.abspath(os.path.join(here, configfile2))
if os.path.exists(localconf):
    config.setup(localconf)
