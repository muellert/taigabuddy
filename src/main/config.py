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
        print("\nConfig.setup(%s): attributes = %s\n" % (configfile, dir(self)))
        if not (hasattr(self, 'API_URL') and hasattr(self, 'AUTH_URL')):
            raise ValueError("You must specify a Taiga instance to access")
        self.dbsetup()
        if hasattr(self, 'db_url'):
            self.__setattr__('SQLALCHEMY_DATABASE_URI', self.db_url)
        if hasattr(self, 'DB_URL'):
            self.__setattr__('SQLALCHEMY_DATABASE_URI', self.DB_URL)
        print("\nConfig.setup(): SQLALCHEMY_DATABASE_URI = ", self.SQLALCHEMY_DATABASE_URI)
        if hasattr(self, 'DEBUG'):
            self.__setattr__('SQLALCHEMY_ECHO', True)

    def dbsetup(self, params={}):
        """get a database set up. separated from setup() in order to allow for
           overriding during test.

           If 'params' is being passed in, it needs to have the full database
           configuration inside. Otherwise, the database configuration is taken
           from "magic" attributes of 'self'.
        """
        print("Config.dbsetup(): config = ", dir(self))
        db_url = None
        if params != {}:
            if 'db_url' in params:
                db_url = params['db_url']
            elif params['DB_DRIVER'] == 'sqlite':
                db_url = "sqlite://%s" % params['DB_PATH']
            else:
                # database is not SQLite:
                password = urlencode("", params['DB_PASS'])[1:]
                db_url = "%s@%s:%s@%s:%s/%s" % \
                         (params['DB_DRIVER'], params['DB_USER'],
                          password, params['DB_HOST'],
                          params['DB_PORT'], params['DB_NAME'])
        elif hasattr(self, 'DB_URL'):
            self.__setattr__('db_url', self.DB_URL)
        else:
            # take the db configuration from 'self':
            print(" -- orig password = ->%s<-" % self.DB_PASS)
            password = urlencode({"": self.DB_PASS})[1:]
            print(" -- password = ->%s<-" % password)
            db_url = "%s://%s:%s@%s:%s/%s" % \
                     (self.DB_DRIVER, self.DB_USER,
                      password, self.DB_HOST,
                      self.DB_PORT, self.DB_NAME)
        print(" -- db_url: ", db_url)
        self.__setattr__('db_url', db_url)


config = Config()

config.setup(os.path.abspath(os.path.join(here, configfile)))

dbconf = os.path.abspath(os.path.join(here, dbconfig))
if os.path.exists(dbconf):
    config.setup(dbconf)

localconf = os.path.abspath(os.path.join(here, configfile2))
if os.path.exists(localconf):
    config.setup(localconf)
