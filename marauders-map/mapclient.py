#!/usr/bin/python

# Main Marauder's Map Application
# Consists of an icon in the system tray with a menu
# and a preferences window that is accessed through the Preferences... entry

# Program structure:
#  The preferencesWindow is the root node of the program and hides itself by 
#  default. It is used for infrequent configuration changes.
#  The systemTray ties in to all of the external functions required for the map

from PySide import QtCore
from PySide import QtGui
from getpass import getuser
import webbrowser
import urllib

import api
import client_api
from configuration import Settings, Undefined_Value_Error
import signal_strength

class GeneralPrefs(QtGui.QWidget):
    """Tab for general preferences in the :class:`PreferencesWindow`.
        
        """
    
    def __init__(self):
        super(GeneralPrefs, self).__init__()
        main_layout = QtGui.QVBoxLayout()
        self.full_name_box = QtGui.QLineEdit()
        main_layout.addWidget(
                              QtGui.QLabel("Username: ")
                              )
        main_layout.addWidget(
                              QtGui.QLabel(getuser())
                              )
        main_layout.addWidget(
                              QtGui.QLabel("Full Name: ")
                              )
        main_layout.addWidget(
                              self.full_name_box
                              )
        self.setLayout(main_layout)


class AdvancedPrefs(QtGui.QWidget):
    """Tab for advanced preferences in the :class:`PreferencesWindow`.
        
        """
    
    def __init__(self):
        super(AdvancedPrefs, self).__init__()
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.addWidget(
                                   QtGui.QLabel("You will be able to configure advanced stuff here.")
                                   )
        
        self.add_update_freq()
        
        self.setLayout(self.main_layout)
    
    def add_update_freq(self):
        self.freq_divs = [
                          (10,'s'),
                          (1,'m'),
                          (5,'m'),
                          (10,'m'),
                          (30,'m'),
                          (1,'hr')
                          ]
        self.div_precision = 10
        
        freq_label_layout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        
        freq_label_layout.addWidget(
                                    QtGui.QLabel("Update Location Every:")
                                    )
        freq_label_layout.addStretch()
        self.update_hint_label = QtGui.QLabel("")
        freq_label_layout.addWidget(self.update_hint_label)
        
        self.slider = QtGui.QSlider(QtCore.Qt.Orientation.Horizontal)
        
        self.slider.setRange(0, self.div_precision*(len(self.freq_divs)-1))
        self.slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.slider.setTickInterval(self.div_precision)
        
        self.slider.setValue(
                             self._slider_value_from_settings(Settings.REFRESH_FREQ)
                             )
        self.slider.sliderChange = self.update_freq_slider_changed
        self.slider.sliderReleased.connect(self.update_freq_changed)
        
        
        slider_label_layout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        
        # TODO: Figure out how to space labels properly
        for label_tuple in self.freq_divs[:-1]:
            label_text = '%i%s' % label_tuple
            label = QtGui.QLabel(label_text)
            slider_label_layout.addWidget(label)
            slider_label_layout.addStretch()
        label_text = '%i%s' % self.freq_divs[-1]
        label = QtGui.QLabel(label_text)
        slider_label_layout.addWidget(label)
        
        self.main_layout.addLayout(freq_label_layout)
        self.main_layout.addWidget(self.slider)
        self.main_layout.addLayout(slider_label_layout)
    
    
    def update_freq_slider_changed(self, change):
        # XXX: Relies on broken function
        if change is QtGui.QAbstractSlider.SliderChange.SliderValueChange:
            self.update_hint_label.setText(
                                           self._gen_str_from_slider_val(self.slider.value())
                                           )
        
        self.slider.update()
    
    def update_freq_changed(self):
        # XXX: This is totally broken
        # TODO: Convert to appropriate value in seconds
        Settings.REFRESH_FREQ = self._slider_value_to_settings(
                                                               self.slider.value()
                                                               )
        self.update_hint_label.setText("")
    
    def _gen_str_from_slider_val(self, value):
        
        def long_form(value, time_abbr):
            extended = ''
            if time_abbr == 's':
                extended = "second"
            if time_abbr == 'm':
                extended = "minute"
            if time_abbr == 'hr':
                extended = "hour"
            # Pluralize
            if int(value) > 1:
                extended += "s"
            return extended
        
        def secs_to_real_tuple(secs):
            if secs >= 3600:
                hrs = secs/3600
                return (hrs, long_form(hrs, 'hr'))
            elif secs >= 60:
                mins = secs/60
                return (mins, long_form(mins, 'm'))
            else:
                return (secs, long_form(secs, 's'))
        
        real_secs = self._slider_value_to_seconds(value)
        
        return '%i %s' % secs_to_real_tuple(real_secs)
    
    def _time_as_secs(self, time, time_abbr):
        if time_abbr == 's':
            return time
        if time_abbr == 'm':
            return time * 60
        if time_abbr == 'hr':
            return time * 3600
    
    def _slider_value_to_seconds(self, value):
        
        cur_index = min(int(value/float(self.div_precision)),
                        len(self.freq_divs)-1)
        nxt_index = min(int(value/float(self.div_precision)+0.9),
                        len(self.freq_divs)-1)
        cur = self.freq_divs[cur_index]
        nxt = self.freq_divs[nxt_index]
        
        tween_ratio = (value % self.div_precision)/float(self.div_precision)
        sec_diff = self._time_as_secs(*nxt) - self._time_as_secs(*cur)
        real_secs = self._time_as_secs(*cur) + tween_ratio * sec_diff
        
        return real_secs
    
    def _slider_value_to_settings(self, value):
        return self._slider_value_to_seconds(value)
    
    def _slider_value_from_settings(self, secs):
        # TODO: Make this work
        
        for i in range(len(self.freq_divs)-1):
            cur = self.freq_divs[i]
            nxt = self.freq_divs[i+1]
            if self._time_as_secs(*nxt) >= secs:
                sec_diff = self._time_as_secs(*nxt) - self._time_as_secs(*cur)
                tween_ratio = (secs - self._time_as_secs(*cur))/sec_diff
                return self.div_precision * (tween_ratio + i)
        
        return self.div_precision * len(self.freq_divs)

class GetLocationThread(QtCore.QThread):
    """A task to obtain the nearest location.
        
        Tasks are used by the :class:`PreferencesWindow`, which adds them
        to the global thread pool as necessary. When a task is complete, it
        emits a `location_updated_signal`, which is received by the 
        :class:`PreferencesWindow`.
        
        """
    
    location_updated_signal = QtCore.Signal(list)
    
    def run(self):
        print "Getting location"
        
        signals = signal_strength.get_avg_signals_dict()
        nearest_binds = client_api.get_binds(nearest=signals, limit=1)
        
        if len(nearest_binds) > 0:
            likeliest_bind = nearest_binds[0]
            client_api.Position(username=getuser(), bind=likeliest_bind).post()
            likeliest_place = client_api.get_place(likeliest_bind.place)
            self.location_updated_signal.emit([likeliest_place])
        else:
            print "No nearest binds found"


class NewLocationThread(QtCore.QThread):
    """A task to let the user create a new bind.
        
        It spawns the bind creation view of the marauder's map after getting
        a signal reading.
        
        A task to obtain the nearest location.
        
        Tasks are used by the :class:`PreferencesWindow`, which adds them
        to the global thread pool as necessary. When a task is complete, it
        emits a `location_updated_signal`, which is received by the 
        :class:`PreferencesWindow`.
        
        """
    
    def run(self):
        signals = signal_strength.get_avg_signals_dict()
        
        upload_dict = dict()
        for key, value in signals.iteritems():
            upload_dict['signals[%s]' % key] = value
        
        webbrowser.open("%s?action=place&username=%s&%s" % 
                        (Settings.WEB_ADDRESS, 
                         Settings.USER_NAME,
                         urllib.urlencode(upload_dict))
                        )

class PreferencesWindow(QtGui.QDialog):
    """The preferences window is the owner of everything else in the program.
        It should not be instantiated more than once.
        
        :class attributes:
        * **update_signal** (PySide.QtCore.Signal) -- When emitted
        (see :py:meth:`PySide.QtCore.Signal.emit`), tells the
        LocationWorker to get the user's new location
        (:meth:`LocationWorker.get_location`)
        * **offline_signal** (PySide.QtCore.Signal) -- When emitted
        (see :py:meth:`PySide.QtCore.Signal.emit`), tells the
        LocationWorker to stop sending stuff to the server
        (:meth:`LocationWorker.stop_working`)
        
        """
    
    update_signal = QtCore.Signal()
    offline_signal = QtCore.Signal()
    
    def __init__(self):
        super(PreferencesWindow, self).__init__()
        self.setup()
    
    def setup(self):
        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.create_tab_pane())
        self.setLayout(main_layout)
        
        self.set_size(500,200)
        
        self.setWindowTitle("Marauder's Map @ Olin Preferences")
        
        self.create_system_tray()
        
        self.is_online = True
        
        self.refresh_thread = None
        self.creation_thread = None
        
        # Refresh location the first time. Thereafter, the location will be
        # refreshed after an interval specified in the Settings 
        # (if the user is online)
        self.refresh_location()
    
    def set_size(self, width, height):
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
    
    def create_tab_pane(self):
        '''
            Create and return a tab pane with the options
            General, Advanced
            
            This pane is like the one used in the Mac OS X preferences dialog
            '''
        tab_pane = QtGui.QTabWidget()
        tab_pane.addTab(GeneralPrefs(), "General")
        tab_pane.addTab(AdvancedPrefs(), "Advanced")
        return tab_pane
    
    def create_system_tray(self):
        '''
            
            '''
        self.sys_tray_icon_default = QtGui.QIcon("demoIcon.png")
        self.sys_tray_icon_clicked = QtGui.QIcon("demoIconWhite.png")
        self.sys_tray = QtGui.QSystemTrayIcon(self, icon=self.sys_tray_icon_default)
        self.sys_tray.setToolTip("Marauder's Map")
        
        self.sys_tray.activated.connect(self.sys_tray_menu_clicked)
        self.create_system_tray_actions()
        self.sys_tray_menu = self.create_system_tray_menu()
        self.sys_tray.setContextMenu(self.sys_tray_menu)
        
        # XXX: NEVER GETS TRIGGERED ON MAC OS X!?!
        self.sys_tray_menu.aboutToHide.connect(self.sys_tray_menu_closed)
        # I expected this to emit on menu close when no action is selected
        
        self.sys_tray.show()
    
    def create_system_tray_actions(self):
        """Create the actions for the system tray:
            open_action
            refresh_action
            location_indicator
            correct_location_action
            other_location_action
            offline_action
            prefs_action
            quit_action
            """
        self.open_action = QtGui.QAction(
                                         "&Open Map",
                                         self,
                                         triggered = self.open_webapp
                                         )
        self.refresh_action = QtGui.QAction(
                                            "&Refresh My Location",
                                            self,
                                            triggered=self.sys_tray_initiate_location_refresh
                                            )
        self.location_indicator = QtGui.QAction(
                                                "Location: Unknown",
                                                self,
                                                enabled=False
                                                )
        self.correct_location_action = QtGui.QAction(
                                                     "&Correct My Location",
                                                     self,
                                                     enabled=True,
                                                     triggered=self.new_location
                                                     )
        self.other_location_action = QtGui.QAction(
                                                   "Other...",
                                                   self
                                                   )
        self.offline_action = QtGui.QAction(
                                            "&Go Offline",
                                            self,
                                            triggered=self.sys_tray_go_offline
                                            )
        self.prefs_action = QtGui.QAction(
                                          "&Preferences...",
                                          self,
                                          triggered=self.display
                                          )
        self.quit_action = QtGui.QAction(
                                         "&Quit Marauder's Map",
                                         self,
                                         triggered=self.sys_tray_quit_action
                                         )
    
    def open_webapp(self):
        webbrowser.open(Settings.WEB_ADDRESS)
    
    def create_system_tray_menu(self):
        sys_tray_menu = QtGui.QMenu(self)
        sys_tray_menu.addAction(self.open_action)
        
        sys_tray_menu.addSeparator()
        sys_tray_menu.addAction(self.refresh_action)
        sys_tray_menu.addSeparator()
        sys_tray_menu.addAction(self.location_indicator)
        sys_tray_menu.addAction(self.correct_location_action)
        sys_tray_menu.addSeparator()
        sys_tray_menu.addAction(self.offline_action)
        sys_tray_menu.addAction(self.prefs_action)
        sys_tray_menu.addSeparator()
        sys_tray_menu.addAction(self.quit_action)
        
        return sys_tray_menu
    
    def refresh_location(self):
        '''
            Creates a thread to refresh the location.
            '''
        
        #self.sys_tray.showMessage("Updating", "Determining Location...")
        
        should_create_new_thread = False
        
        if self.refresh_thread:
            # Thread exists
            if self.refresh_thread.isFinished():
                print "Thread Finished"
                del self.refresh_thread
                self.refresh_thread = None
                should_create_new_thread = True
        else:
            should_create_new_thread = True
        
        if should_create_new_thread and self.is_online:
            self.refresh_thread = GetLocationThread()
            self.refresh_thread.location_updated_signal.connect(self.location_slot)
            self.refresh_thread.start()
            # TODO: Match freq to settings
            QtCore.QTimer.singleShot(10000, self.refresh_location)
        else:
            # Only wait a bit before rechecking 
            # if the thread is still running
            QtCore.QTimer.singleShot(200, self.refresh_location)
    
    
    def new_location(self):
        '''
            Creates a thread to allow new bind creation.
            '''
        
        if self.creation_thread:
            if self.creation_thread.isFinished():
                print "Thread Finished"
                del self.creation_thread
                self.creation_thread = None
            else:
                # Only wait a bit before rechecking 
                # if the thread is still running
                QtCore.QTimer.singleShot(200, self.new_location)
        else:
            self.sys_tray.showMessage("Gathering Data...", 
                                      "Set your location once a browser is launched.")
            self.creation_thread = NewLocationThread()
            self.creation_thread.start()
            
            self.location_indicator.setText("Location: Being Set")
    
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
            
            .. note:: Don't call this function manually!
            This function overrides the default QT close behavior
            '''
        
        self.hide()
        event.ignore()
    
    # System Tray Actions:
    @QtCore.Slot(QtGui.QSystemTrayIcon.ActivationReason)
    def sys_tray_menu_clicked(self, reason):
        '''
            Connected to the 'activated' signal of the system tray.
            Changes the icon to look good when clicked
            
            .. warning:: Deactivated because there is no way to go back
            
            '''
    #if reason == QtGui.QSystemTrayIcon.ActivationReason.Trigger:
    #    Single Click to open menu
    #    self.sys_tray.setIcon(self.sys_tray_icon_clicked)
    # NOTE: Below commented because unused. Can use later if we want
    #elif reason == QtGui.QSystemTrayIcon.ActivationReason.DoubleClick:
    #    # Double click
    #    pass
    
    @QtCore.Slot()
    def sys_tray_menu_closed(self):
        print "Closed Menu"
    # XXX: NEVER GETS TRIGGERED on Mac OsX
    # self.sys_tray.setIcon(self.sys_tray_icon_default)
    
    def sys_tray_quit_action(self):
        '''
            Cleans up and quits the application.
            '''
        
        #self.offline_signal.emit()
        #self.bg_thread.quit()
        #while not self.bg_thread.isFinished():
        #continue # Wait until thread done
        
        # On Ubuntu 10.10 (at least), a Python fatal error is encountered if 
        # the window is not hidden before the application exits
        
        self.is_online = False
        if self.refresh_thread: 
            self.sys_tray.showMessage("Cleaning Up...", 
                                      "Closing background threads; please wait.")
            while self.refresh_thread.isRunning():
                pass
        if self.creation_thread: 
            self.sys_tray.showMessage("Cleaning Up...",  
                                      "Closing background threads; please wait.")
            while self.creation_thread.isRunning():
                pass
        
        self.hide()
        QtGui.qApp.quit()
    
    def sys_tray_initiate_location_refresh(self):
        self.refresh_location()
    
    def sys_tray_go_offline(self):
        if self.is_online:
            if self.refresh_thread.isRunning():
                self.sys_tray.showMessage("Finishing Up", 
                                          "Going offline once this operation is complete...")
            self.offline_action.setText("Go Online")
        else:
            self.offline_action.setText("Go Offline")
        self.is_online = not self.is_online
    
    # Background actions
    @QtCore.Slot(list)
    def location_slot(self, locations):
        '''
            Slot that gets data whenever a location refresh
            happens
            '''
        if len(locations) > 0:
            print "I'm at %s" % locations[0]
            self.location_indicator.setText("Location: %s" % locations[0].alias)
        else:
            print "No locations found"
        
        '''
            flag, response = flagResponseTuple
            if flag:
            pot_locs = response
            sub_menu = QtGui.QMenu("Correct Location Submenu", self)
            for potLoc in pot_locs:
            def correct_location(realLoc):
            def postFunction():
            self.post_location(realLoc)
            return postFunction
            
            subAction = QtGui.QAction(potLoc.readable_name, self, triggered=correct_location(potLoc))
            sub_menu.addAction(subAction)
            sub_menu.addSeparator()
            sub_menu.addAction(self.otherLocationAction)
            self.correct_location_action.setMenu(sub_menu)
            self.correct_location_action.setEnabled(True)
            
            self.most_likely_loc = pot_locs[0]
            self.location_indicator.setText(self.most_likely_loc.readable_name)
            
            self.sys_tray.showMessage("Location: %s" % self.most_likely_loc.readable_name, "Click here to fix the location.")
            
            else:
            self.location_indicator.setText("Unable to Connect to Server")
            self.correct_location_action.setEnabled(False)
            '''


def setup_window():
    """Create and return the Preferences window,
        which owns every other element.
        
        :returns: instance of :class:`PreferencesWindow`
        
        .. warning:: The window must have a pointer to it, or it will get garbage collected and
        the application won't run
        
        """
    QtGui.QApplication.setQuitOnLastWindowClosed(False)
    preferences_window = PreferencesWindow()
    return preferences_window

def can_launch():
    """Checks if the application is unable to launch because of missing
        system features.
        
        Returns CanLaunch_BOOL, Reason_STR
        """
    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        return False, "Failed to detect presence of system tray"
    else:
        return True, None

if __name__ == '__main__':
    import sys
    
    Settings.init()
    
    is_first_launch = False
    
    try:
        # See if username exists in Settings file
        username = Settings.USER_NAME
    except Undefined_Value_Error:
        # Set username to system username
        username = getuser()
        Settings.USER_NAME = username
        is_first_launch = True
    
    try:
        # Register username if it doesn't exist on the server
        username = getuser()
        
        client_api.get_user(username)
    
    except client_api.Unable_To_Connect_Error:
        print "Unable to connect to marauder's map server"
    except KeyError:
        print "User not found on server. Posting."
        print "Making User"
        user = client_api.User(username=Settings.USER_NAME, 
                               alias="Unknown")
        user.put()
    
    
    
    app = QtGui.QApplication(sys.argv)
    able_to_launch, reason = can_launch()
    
    if not able_to_launch:
        print "ERROR: Unable to launch Marauder's Map!"
        print reason
        sys.exit(1)
    else:
        # Note: we have to retain a reference to the window so that it isn't killed
        preferences_window = setup_window()     
        if is_first_launch:
            preferences_window.display()
        sys.exit(app.exec_())