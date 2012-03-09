import webbrowser
from getpass import getuser

from configuration import Settings #Global Settings
import api

def open_map():
    webbrowser.open(Settings.WEB_ADDRESS)

def getLocation():
    o = api.getLocation()
    if o[0]:
        return o[1]
    else:
        return False

if __name__ == '__main__':
    open_map()
