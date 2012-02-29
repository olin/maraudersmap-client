from configuration import Settings #Global Settings

import webbrowser

def open_map():
    webbrowser.open(Settings.WEB_ADDRESS)

if __name__ == '__main__':
    open_map()
