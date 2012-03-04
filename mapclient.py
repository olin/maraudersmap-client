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

class SystemTray(QtGui.QSystemTrayIcon):
    def __init__(self, parent, icon):
        super(SystemTray, self).__init__(parent, icon=icon)

    '''def activated(self, reason):
        print "Activated", reason
        super(SystemTray, self).activated(reason)
    '''

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
        self.sysTrayIconDefault = QtGui.QIcon("demoIcon.png")
        self.sysTrayIconClicked = QtGui.QIcon("demoIconWhite.png")        
        #self.sysTray = SystemTray(self, self.sysTrayIconDefault)
        self.sysTray = QtGui.QSystemTrayIcon(self, icon=self.sysTrayIconDefault)
        self.sysTray.setToolTip("Marauder's Map")

        self.sysTray.activated.connect(self.sysTrayMenuClicked)

        self.sysTray.show()

    def display(self):
        '''
        Display the preferences window

        # TODO: There is an ugly jumping effect where the window starts out below
        #  the active application and moves to the top. I'd like it to appear on top
        '''
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

    def sysTrayMenuClosed(self):  
        self.sysTray.setIcon(self.sysTrayIconDefault)

def setupWindow():
    '''
    '''
    QtGui.QApplication.setQuitOnLastWindowClosed(False)
    preferencesWindow = PreferencesWindow()
    preferencesWindow.display()
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
    
    ableToLaunch, reason = canLaunch()
    if not ableToLaunch:
        print "ERROR: Unable to launch Marauder's Map!"
        print reason
        sys.exit(1)
    else:
        app = QtGui.QApplication(sys.argv)
        # Note: we have to retain a reference to the window so that it isn't killed
        preferencesWindow = setupWindow() 
        sys.exit(app.exec_())
