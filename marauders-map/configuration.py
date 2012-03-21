import os
import sys
_top_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_top_dir, "appdirs-1.2.0"))
import appdirs
import ConfigParser


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


class SettingsNotInitializedError(Exception):
    def __init__(self):
        self.msg = "Call Settings.init() before using Settings!"


class Settings(object):
    """A class to manipulate application settings.

    Use it like this:

    .. code-block:: python

        from configuration import Settings
        Settings.init() # Make it possible to use Settings
        # Read settings from file
        print Settings.SERVER_ADDRESS
        # Change the settings and write those changes to file
        Settings.SERVER_ADDRESS = "http://somewebsite.blah"

    .. warning:: Never create a settings instance!

    :class attributes:
        * **SERVER_ADDRESS** (str) - Where to post server requests
            Default: ``http://apps.olin.edu``
        * **WEB_ADDRESS** (str) - Web address of the map; used when
            "Open Map" is clicked

            Default: ``http://apps.olin.edu/ui/mapui.php``
        * **REFRESH_FREQ** (int) - How often to refresh the location, in
            seconds

            Default: ``300``

    """

    _READY = False  # Has init() been called?

    # XXX: These comments get stripped out as soon as changes are written...
    _DEFAULTS = {
            "SERVER_ADDRESS": '%s ; %s' %
                ('http://apps.olin.edu',
                 'Location of the server to connect to'),
            "WEB_ADDRESS": '%s ; %s' %
                ('http://apps.olin.edu/ui/mapui.php',
                 'What website to open when "Open Map" is clicked'),
            "REFRESH_FREQ": '%i ; %s' %
                (300,
                 'How often to refresh the location, in seconds')
            }

    APP_NAME = "MaraudersMap"  # Used to define prefs path
    APP_AUTHOR = "ohack"  # Used to define prefs path

    @classmethod
    def init(cls):
        """Call this before using Settings. Calling it multiple times
        should be harmless.

        Creates preferences directory & file in the appropriate location for
        the current OS if it doesn't exist and sets up the class attributes
        with appropriate values.
        The file is called ``config.txt``.

        .. warning:: A limitation of the ConfigParser module that we are
            using is that it strips out comments from the config file, which
            is annoying in cases where the user wants to make changes
            manually. If we want to remove this limitation, we should use
            configobj: http://www.voidspace.org.uk/python/configobj.html
        """
        cls._prefs_dir = appdirs.user_data_dir(cls.APP_NAME, cls.APP_AUTHOR)
        cls._prefs_file_path = os.path.join(cls._prefs_dir, "config.txt")

        cls._config_parser = ConfigParser.RawConfigParser(cls._DEFAULTS)
        cls._config_parser.add_section('User Defined')

        # Create the preferences directory if necessary
        if not os.path.isdir(cls._prefs_dir):
            try:
                os.makedirs(cls._prefs_dir)
            except Exception as e:
                print type(e)
                print "Failed to create preferences directory!"
                print e
                raise PreferenceCreationError(cls._prefs_dir)

        # Create the preferences file if necessary, with defaults
        if not os.path.isfile(cls._prefs_file_path):
            try:
                cls.write_prefs_to_file()
            except Exception as e:
                print "Failed to create preferences file"
                print e
                raise PreferenceCreationError(prefs_file_path)
        # Read prefs from the file
        else:
            cls.read_prefs_from_file()

        cls._READY = True

    @classmethod
    def write_prefs_to_file(cls):
        """Writes preferences to file. You shouldn't need to call this
        manually because it gets called every time a setting is changed.

        .. note:: Every time this method is called, all comments in the
            file will be overwritten (with rare exceptions)
        """
        with open(cls._prefs_file_path, 'w') as prefs_file:
            cls._config_parser.write(prefs_file)

    @classmethod
    def read_prefs_from_file(cls):
        """Reads preferences from file. You shouldn't need to call this
        manually because it gets called on :meth:`Settings.init()` unless you
        want to support users who modify the file while the application is
        running.
        """
        with open(cls._prefs_file_path) as prefs_file:
            cls._config_parser.readfp(prefs_file)

    @classmethod
    def _check_for_init(cls):
        if not cls._READY:
            raise SettingsNotInitializedError()

    class __metaclass__(type):
        """Define custom class properties (getters and setters)
        Code from: http://stackoverflow.com/a/1800999/798235

        .. warning:: May not work in Python 3
        """
        @property
        def SERVER_ADDRESS(cls):
            cls._check_for_init()
            raw_value = cls._config_parser.get('User Defined',
                                               'SERVER_ADDRESS')
            return raw_value.split(';')[0].strip()

        @SERVER_ADDRESS.setter
        def SERVER_ADDRESS(cls, value):
            cls._check_for_init()
            raw_value = cls._config_parser.set('User Defined',
                                               'SERVER_ADDRESS',
                                               value)
            cls.write_prefs_to_file()

        @property
        def WEB_ADDRESS(cls):
            cls._check_for_init()
            raw_value = cls._config_parser.get('User Defined',
                                               'WEB_ADDRESS')
            return raw_value.split(';')[0].strip()

        @WEB_ADDRESS.setter
        def WEB_ADDRESS(cls, value):
            cls._check_for_init()
            raw_value = cls._config_parser.set('User Defined',
                                               'WEB_ADDRESS',
                                               value)
            cls.write_prefs_to_file()

        @property
        def REFRESH_FREQ(cls):
            cls._check_for_init()
            raw_value = cls._config_parser.get('User Defined',
                                               'REFRESH_FREQ')
            return int(raw_value.split(';')[0].strip())

        @REFRESH_FREQ.setter
        def REFRESH_FREQ(cls, value):
            cls._check_for_init()
            raw_value = cls._config_parser.set('User Defined',
                                               'REFRESH_FREQ',
                                               value)
            cls.write_prefs_to_file()

if __name__ == "__main__":
    Settings.init()
    print Settings.SERVER_ADDRESS
    Settings.SERVER_ADDRESS = "http://somewebsite.blah"
    print Settings.SERVER_ADDRESS
    print Settings.WEB_ADDRESS
