import os
import sys
_top_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_top_dir, "appdirs-1.2.0"))
import appdirs
import ConfigParser

class ClassProperty(property):
    """Decorator to be used because it is not possible to combine
    @property and @classmethod normally.

    Code from:
    http://stackoverflow.com/questions/128573/using-property-on-classmethods    

    Use it like this:
        @ClassProperty
        @property
        def afunc():
            return stuff

    """
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class PreferenceCreationError(Exception):
    """Error to be thrown when prefs could not be created.

    This could be thrown when the directory or the file could not
    be created.

    :param path: Path that could not be created
    :type path: str
    """
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return repr(self.path)

class Settings(object):
    _DEFAULTS = {
            "SERVER_ADDRESS":'%s ; %s' %
                ('http://apps.olin.edu', 
                 'Location of the server to connect to'),
            "WEB_ADDRESS":'%s ; %s' %
                ('http://apps.olin.edu/ui/mapui.php',
                 'What website to open when "Open Map" is clicked'),
            "REFRESH_FREQ":'%i ; %s' %
                (300,
                 'How often to refresh the location, in seconds')
            } 

    APP_NAME = "MaraudersMap"
    APP_AUTHOR = "ohack"

    #SERVER_ADDRESS = 'http://apps.olin.edu'
    #WEB_ADDRESS = 'http://apps.olin.edu/ui/mapui.php'
    #SERVER_ADDRESS = 'http://acl.olin.edu/map'
    #WEB_ADDRESS = 'http://acl.olin.edu/map/ui/mapui.php'

    @classmethod
    def init(cls):
        prefs_dir = appdirs.user_data_dir(cls.APP_NAME, cls.APP_AUTHOR)
        prefs_file_path = os.path.join(prefs_dir, "config.txt")

        cls._config_parser = ConfigParser.RawConfigParser(cls._DEFAULTS)
        cls._config_parser.add_section('User Defined')
       
        # Create the preferences directory if necessary
        if not os.path.isdir(prefs_dir):
            try:
                os.makedirs(prefs_dir)
            except Exception as e:
                print type(e)
                print "Failed to create preferences directory!"
                print e
                raise PreferenceCreationError(prefs_dir)
        
        # Create the preferences file if necessary, with defaults
        if not os.path.isfile(prefs_file_path):
            try:
                with open(prefs_file_path, 'w') as prefs_file:
                    cls._config_parser.write(prefs_file)
            except Exception as e:
                print "Failed to create preferences file"
                print e
                raise PreferenceCreationError(prefs_file_path)

    def write_defaults_to_file():
       pass 
 
    @ClassProperty
    @classmethod
    def SERVER_ADDRESS(cls):
        raw_value = cls._config_parser.get('User Defined', 'SERVER_ADDRESS')
        return raw_value.split(';')[0].strip()

    @ClassProperty
    @classmethod
    def WEB_ADDRESS(cls):
        raw_value = cls._config_parser.get('User Defined', 'WEB_ADDRESS')
        return raw_value.split(';')[0].strip()

    @ClassProperty
    @classmethod
    def REFRESH_FREQ(cls):
        raw_value = cls._config_parser.get('User Defined', 'REFRESH_FREQ')
        return raw_value.split(';')[0].strip()

if __name__ == "__main__":
    Settings.init()
    print Settings.SERVER_ADDRESS
