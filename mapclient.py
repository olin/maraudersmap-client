#!/usr/bin/python

# Main Marauder's Map Application
# Consists of an icon in the system tray with a menu
# and a preferences window that is accessed through the Preferences... entry

# Program structure:
#  The preferencesWindow is the root node of the program and hides itself by default
#  It is used for infrequent configuration changes
#  The systemTray ties in to all of the external functions required for the map

from PySide import QtCore
from PySide import QtGui

import api

class GeneralPrefs(QtGui.QWidget):
    def __init__(self):
        super(GeneralPrefs, self).__init__()
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(QtGui.QLabel("You will be able to configure basic stuff here."))
        self.setLayout(mainLayout)

class AdvancedPrefs(QtGui.QWidget):
    def __init__(self):
        super(AdvancedPrefs, self).__init__()
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(QtGui.QLabel("You will be able to configure advanced stuff here."))
        self.setLayout(mainLayout)

class LocationUpdatedSignaler(QtCore.QObject):
    '''
    A signal sent by the LocationWorker whenever the location is reported by the server
    '''
    signal = QtCore.Signal()


class UpdateSignaler(QtCore.QObject):
    '''
    A signal that can be sent to the LocationWorker to tell it
    to get the user's new location
    '''
    signal = QtCore.Signal()

class LocationWorker(QtCore.QObject):
    @QtCore.Slot()
    def getLocation(self):  
        print "GettingLocation!"
        print api.getLocation()

class PreferencesWindow(QtGui.QDialog):
    def __init__(self):
        super(PreferencesWindow, self).__init__()
        self.setup()

    def setup(self):
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.createTabPane())
        self.setLayout(mainLayout)
        
        self.setSize(500,200)

        self.setWindowTitle("Marauder's Map @ Olin Preferences") 

        self.createSystemTray()
        self.setupBackgroundThread()
        self.startRefreshTimer()

    def setSize(self, width, height):
        self.setMinimumWidth(width)        
        self.setMaximumWidth(width)                
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

    def createTabPane(self):
        '''
        Create and return a tab pane with the options
        General, Advanced

        This pane is like the one used in the Mac OS X preferences dialog
        '''
        tabPane = QtGui.QTabWidget()
        tabPane.addTab(GeneralPrefs(), "General")
        tabPane.addTab(AdvancedPrefs(), "Advanced")
        return tabPane

    def createSystemTray(self):
        '''
        
        '''
        self.sysTrayIconDefault = QtGui.QIcon("demoIcon.png")
        self.sysTrayIconClicked = QtGui.QIcon("demoIconWhite.png")        
        self.sysTray = QtGui.QSystemTrayIcon(self, icon=self.sysTrayIconDefault)
        self.sysTray.setToolTip("Marauder's Map")

        self.sysTray.activated.connect(self.sysTrayMenuClicked)
        self.createSystemTrayActions()
        self.sysTrayMenu = self.createSystemTrayMenu()
        self.sysTray.setContextMenu(self.sysTrayMenu)
        self.sysTrayMenu.aboutToHide.connect(self.sysTrayMenuClosed) # XXX: NEVER GETS TRIGGERED ON MAC OS X!?!
        # I expected this to emit on menu close when no action is selected

        self.sysTray.show()

    def createSystemTrayActions(self):
        self.openAction = QtGui.QAction("&Open Map", self, triggered=api.openMap)
        self.refreshAction = QtGui.QAction("&Refresh My Location", self, triggered=self.sysTrayInitiateLocationRefresh)
        self.locationIndicator = QtGui.QAction("Location: Unknown", self, enabled=False)
        self.correctLocationAction = QtGui.QAction("&Correct My Location", self)
        self.otherLocationAction = QtGui.QAction("Other...", self)
        self.offlineAction = QtGui.QAction("&Go Offline", self)
        self.prefsAction = QtGui.QAction("&Preferences...", self, triggered=self.display)
        self.quitAction = QtGui.QAction("&Quit Marauder's Map", self, triggered=self.sysTrayQuitAction)

    def createSystemTrayMenu(self):
        sysTrayMenu = QtGui.QMenu(self)
        sysTrayMenu.addAction(self.openAction)
        
        sysTrayMenu.addSeparator()
        sysTrayMenu.addAction(self.refreshAction)
        sysTrayMenu.addSeparator()
        sysTrayMenu.addAction(self.locationIndicator)
        sysTrayMenu.addAction(self.correctLocationAction)        
        sysTrayMenu.addSeparator()
        sysTrayMenu.addAction(self.offlineAction)
        sysTrayMenu.addAction(self.prefsAction)
        sysTrayMenu.addSeparator()
        sysTrayMenu.addAction(self.quitAction)
        
        return sysTrayMenu
        
    def startRefreshTimer(self):
        self.bgThread.start()        
        self.refreshTimer = QtCore.QTimer(self)
        self.refreshTimer.timeout.connect(self.refreshLocation)
        self.refreshTimer.start(10000)
        print "Timer Started"

    def refreshLocation(self):
        '''
        Sends a signal to the LocationWorker in bgThread
        to get the location
        '''
        print "Refreshing!"
        self.updateSignaler.signal.emit()

    def setupBackgroundThread(self):
        print "Setting up bgThread"
        self.bgThread = QtCore.QThread()
        self.updateSignaler = UpdateSignaler()
        self.locationWorker = LocationWorker()
        self.updateSignaler.signal.connect(self.locationWorker.getLocation)
        self.locationWorker.moveToThread(self.bgThread)

    def display(self):
        '''
        Display the preferences window
        '''
        # TODO: There is an ugly jumping effect where the window starts out below
        #  the active application and moves to the top. I'd like it to appear on top
        self.show()
        self.raise_()

    def closeEvent(self, event):
        '''
        When the close button is pressed on the preferences window,
        hide it; don't close or minimize it.

        Note: Don't call this function manually!
        '''
        self.hide()
        event.ignore()

    # System Tray Actions:
    @QtCore.Slot(QtGui.QSystemTrayIcon.ActivationReason)
    def sysTrayMenuClicked(self, reason):
        '''
        Connected to the 'activated' signal of the system tray.
        Changes the icon to look good when clicked
        '''
        if reason == QtGui.QSystemTrayIcon.ActivationReason.Trigger:
            #Single Click to open menu
            self.sysTray.setIcon(self.sysTrayIconClicked)
        # NOTE: Below commented because unused. Can use later if we want
        #elif reason == QtGui.QSystemTrayIcon.ActivationReason.DoubleClick:
        #    # Double click
        #    pass

    @QtCore.Slot()
    def sysTrayMenuClosed(self):  
        print "Closed Menu"
        # XXX: NEVER GETS TRIGGERED on Mac OsX
        self.sysTray.setIcon(self.sysTrayIconDefault)

    def sysTrayQuitAction(self):
        '''
        Cleans up and quits the application.
        '''
        # On Ubuntu 10.10, a Python fatal error is encountered if the
        # window is not hidden before the application exits
        self.bgThread.quit()
        while not self.bgThread.isFinished():
            continue # Wait until thread done 
        self.hide()
        QtGui.qApp.quit()

    def sysTrayInitiateLocationRefresh(self):
        pass

    # Background actions
    @QtCore.Slot(list)
    def locationSlot(self, flagResponseTuple):
        '''
        Slot that gets data whenever a location refresh
        happens
        '''
        flag, response = flagResponseTuple
        print response

def setupWindow():
    '''
    Create and return the preferences window,
    which owns every other element
    '''
    QtGui.QApplication.setQuitOnLastWindowClosed(False)
    preferencesWindow = PreferencesWindow()
    #preferencesWindow.display()
    return preferencesWindow

def canLaunch():
    '''
    Checks if the application is unable to launch because of missing
    system features.

    Returns CanLaunch_BOOL, Reason_STR
    '''
    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        return False, "Failed to detect presence of system tray"
    else:
        return True, None

if __name__ == '__main__':
    import sys
    
    app = QtGui.QApplication(sys.argv)
    ableToLaunch, reason = canLaunch()
    
    if not ableToLaunch:
        print "ERROR: Unable to launch Marauder's Map!"
        print reason
        sys.exit(1)
    else:
        # Note: we have to retain a reference to the window so that it isn't killed
        preferencesWindow = setupWindow()
        sys.exit(app.exec_())
