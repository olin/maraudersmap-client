#!/usr/bin/python
 
import sys
from PySide import QtCore
from PySide import QtGui

import actions

class Window(QtGui.QDialog):
    def __init__(self):
        super(Window, self).__init__()
        self.createActions()
        self.makeSysTray()

    def createActions(self):
        #TODO: Figure out how to hide tooltips: http://stackoverflow.com/questions/9471791/suppress-qtgui-qaction-tooltips-in-pyside
        self.openAction = QtGui.QAction("&Open Map", self, triggered=actions.open_map)
        self.refreshAction = QtGui.QAction("&Refresh My Location", self)        
        self.newLocAction = QtGui.QAction("&Create New Location", self)        
        self.locationIndicator = QtGui.QAction("Location: Dining Hall", self, enabled=False)        
        self.offlineAction = QtGui.QAction("&Go Offline", self)        
        self.prefsAction = QtGui.QAction("&Preferences...", self)                
        self.quitAction = QtGui.QAction("&Quit Marauder's Map", self, triggered=QtGui.qApp.quit)

    def makeSysTray(self):
        self.menu = QtGui.QMenu(self)
        self.menu.addAction(self.openAction)
        self.menu.addSeparator()
        self.menu.addAction(self.refreshAction)
        self.menu.addAction(self.newLocAction)
        self.menu.addSeparator()
        self.menu.addAction(self.locationIndicator)
        self.menu.addSeparator()
        self.menu.addAction(self.offlineAction)
        self.menu.addAction(self.prefsAction)
        self.menu.addSeparator()
        self.menu.addAction(self.quitAction)


        self.sysTrayIcon = QtGui.QIcon("demoIcon.png")
        self.sysTray = QtGui.QSystemTrayIcon(self, icon=self.sysTrayIcon)

        self.sysTray.setContextMenu(self.menu)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    
    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        print "Failed to detect presence of system tray, crashing"
        sys.exit(1)

    promptStartup = False
    window = Window()

    #TODO: Use http://www.dallagnese.fr/en/computers-it/recette-python-qt4-qsingleapplication-pyside/
    # To do sigle-instance checking

    #fileMenu = QtGui.QMenuBar.addMenu(QMenuBar.tr("&File"))

    # Create a Label and show it
    label = QtGui.QLabel("Hello World")
    label.show()
    # Enter Qt application main loop

    window.sysTray.show()


    app.exec_()
    sys.exit()

