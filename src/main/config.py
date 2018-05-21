import os.path
import yaml

here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
configfile = "taigabuddy.yaml"


class Config:
    """Load the configuration from a YAML file and set attributes
       on an instance of this object.
    """

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
        config = self.load_config(configfile)
        print("config from file: ", config)

        if 'api_url' not in config or \
           'auth_url' not in config:
            raise ValueError("You must specify a Taiga instance to access")

        for k, v in config.items():
            self.__setattr__(k, v)
        return self

config = Config()

config.setup(os.path.join(here, configfile))
