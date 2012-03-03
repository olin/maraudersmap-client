#!/usr/bin/python
 
import sys
from PySide import QtCore
from PySide import QtGui

import actions

class Killer(QtCore.QObject):
    speak = QtCore.Signal(str)

class LocationReporter(QtCore.QObject):
    reporter = QtCore.Signal(list)

class UpdateSignaler(QtCore.QObject):
    signal = QtCore.Signal()

class Window(QtGui.QDialog):
    def __init__(self):
        super(Window, self).__init__()
        self.aThread = MyThread(self)
        self.aThread.started.connect(self.started)
        self.aThread.finished.connect(self.finished)
        self.aThread.terminated.connect(self.terminated)
       
        self.killer = Killer()
        self.killer.speak.connect(self.aThread.deathSlot)

                
        self.createActions()
        self.makeSysTray()
        self.correctLocationAction.setEnabled(False)

        self.updateSignaler = UpdateSignaler()
        self.updateSignaler.signal.connect(self.aThread.updateSlot)

    @QtCore.Slot(list)
    def locationSlot(self, locations):
        if locations:
            subMenu = QtGui.QMenu("Popup Submenu", self)
            for loc in locations:
                subMenu.addAction(loc)
            subMenu.addSeparator()            
            subMenu.addAction(self.otherLocationAction)
            self.correctLocationAction.setMenu(subMenu)            
            bestLocation = locations[0]
            self.locationIndicator.setText(bestLocation)
            self.correctLocationAction.setEnabled(True)
        else:
            self.locationIndicator.setText("Unable to Connect to Server")
            self.correctLocationAction.setEnabled(False)

    def createActions(self):
        #TODO: Figure out how to hide tooltips: http://stackoverflow.com/questions/9471791/suppress-qtgui-qaction-tooltips-in-pyside
        self.openAction = QtGui.QAction("&Open Map", self, triggered=actions.open_map)
        self.refreshAction = QtGui.QAction("&Refresh My Location", self, triggered=self.refreshLocation)        
        self.locationIndicator = QtGui.QAction("Location: Unknown", self, enabled=False)        
        
        self.correctLocationAction = QtGui.QAction("&Correct My Location", self)
        self.otherLocationAction = QtGui.QAction("Other...", self)
        
        self.offlineAction = QtGui.QAction("&Go Offline", self)        
        self.prefsAction = QtGui.QAction("&Preferences...", self)                
        self.quitAction = QtGui.QAction("&Quit Marauder's Map", self, triggered=self.quit)

    def refreshLocation(self):
        '''
        locations = actions.refresh_location()
        if locations:
            subMenu = QtGui.QMenu("Popup Submenu", self)
            for loc in locations:
                subMenu.addAction(loc)
            subMenu.addSeparator()            
            subMenu.addAction(self.otherLocationAction)
            self.correctLocationAction.setMenu(subMenu)            
            bestLocation = locations[0]
            self.locationIndicator.setText(bestLocation)
            self.correctLocationAction.setEnabled(True)
        else:
            self.locationIndicator.setText("Unable to Connect to Server")
            self.correctLocationAction.setEnabled(False)
        '''
        self.updateSignaler.signal.emit()


    def makeSysTray(self):
        self.menu = QtGui.QMenu(self)
        self.menu.addAction(self.openAction)
        self.menu.addSeparator()
        self.menu.addAction(self.refreshAction)
        self.menu.addSeparator()
        self.menu.addAction(self.locationIndicator)
        self.menu.addAction(self.correctLocationAction)        
        self.menu.addSeparator()
        self.menu.addAction(self.offlineAction)
        self.menu.addAction(self.prefsAction)
        self.menu.addSeparator()
        self.menu.addAction(self.quitAction)


        self.sysTrayIcon = QtGui.QIcon("demoIcon.png")
        self.sysTray = QtGui.QSystemTrayIcon(self, icon=self.sysTrayIcon)

        self.sysTray.setContextMenu(self.menu)

    def started(self):
        print "YAYYYY"
    
    def finished(self):
        print "Finished!"

    def terminated(self):
        print "Terminated!"

    def quit(self):
        if self.aThread.isRunning():
            self.exiting = True
            self.killer.speak.emit("Die!") 
            self.aThread.wait()
            #while self.aThread.isRunning():
            #    print "Trying to stop!"
        QtGui.qApp.quit()
        

class MyThread (QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.working = False

        self.locationReporter = LocationReporter()
        self.locationReporter.reporter.connect(parent.locationSlot)


    @QtCore.Slot(str)
    def deathSlot(self,aStr):
        # Slot to kill the thread
        print aStr
        self.exiting = True
        while self.working:
            pass
        self.terminate()

    @QtCore.Slot()
    def updateSlot(self):
        # Slot to get message to update location
        if not self.working:
            self.locationReporter.reporter.emit(actions.refresh_location())

    def run(self):
        self.runs = True
        self.exiting = False
        while not self.exiting:
            print "Hi, I'm a thread"
            self.working = True
            print "Working"
            self.locationReporter.reporter.emit(actions.refresh_location())
            print "Done Working"
            self.working = False 
            self.sleep(5) # Seconds
        return 

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    
    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        print "Failed to detect presence of system tray, crashing"
        sys.exit(1)

    promptStartup = False
    
    window = Window()

    #TODO: Use http://www.dallagnese.fr/en/computers-it/recette-python-qt4-qsingleapplication-pyside/
    # To do sigle-instance checking

    # Create a Label and show it
    #label = QtGui.QLabel("Hello World")
    #label.show()

    window.sysTray.show()

    window.aThread.start()

    # Enter Qt application main loop
    sys.exit(app.exec_())

