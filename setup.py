"""
This is a setup.py script used to create a mac app

Usage (Mac):
    python setup.py py2app

Usage (Win):
    python setup.py py2exe

Usage (Linux):
    python setup.py sdist
"""

import sys

if sys.platform.startswith('darwin'):
    from setuptools import setup
    APP = ['src/mapclient.py']
    DATA_FILES = ['src/data/qt.conf', # Used to fix mysterious segfault based on advice from http://www.thetoryparty.com/2009/03/03/pyqt4-i-hate-you/
                  'src/data/demoIcon.png',
                  'src/data/demoIconWhite.png']

    # The plist file specifies that there should be no icon in the dock
    # See: http://www.macosxtips.co.uk/index_files/disable-the-dock-icon-for-any-application.php
    OPTIONS = {'argv_emulation': True, 'plist':'src/data/Info.plist'}

    setup(
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
        packages=['mapclient'],
        package_dir={'mapclient': 'src'},
        package_data={'mapclient': ['data/*']}
    )
elif sys.platform.startswith('linux'):
    from distutils.core import setup
    setup(
        name='marauders-map',
        version='2.0a',
        py_modules=['mapclient'],
    )
elif sys.platform.startswith('win'):
    pass

