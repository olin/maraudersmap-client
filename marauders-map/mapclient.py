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
from configuration import Settings

DEBUG_DONT_CHECK = True

class GeneralPrefs(QtGui.QWidget):
    """Tab for general preferences in the :class:`PreferencesWindow`.

    """

    def __init__(self):
        super(GeneralPrefs, self).__init__()
        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(
            QtGui.QLabel("You will be able to configure basic stuff here.")
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


class LocationWorker(QtCore.QObject):
    """A worker object that runs in the background.

    It does nothing unless it gets a signal from
    the :class:`PreferencesWindow`

    """

    # TODO: Implement some kind of queue of tasks to prevent freezing/long
    # shutdown time
    # A signal sent by the LocationWorker whenever the location is reported
    # by the server
    location_updated_signal = QtCore.Signal(list)

    def __init__(self):
        super(LocationWorker, self).__init__()
        self.can_work = True

    @QtCore.Slot()
    def get_location(self):
        if self.can_work:
            print "Getting location"
            response_tuple = api.get_location()
            self.location_updated_signal.emit(response_tuple)
            flag, response = response_tuple
            if flag:
                locations = response
                print locations
                api.weak_post_location(locations[0].encoded_name)
        else:
            print "Location getting/posting disabled"

    @QtCore.Slot(api.Location)
    def post_location(self, loc):
        """Post a user-defined location to the server and update the user's
        position on the map.

        :param loc: Location to post
        :type loc: :class:`api.Location`

        .. note:: This should only be invoked directly by a user
            specifying the correct location

        """
        if self.can_work:  # This mechanism doesn't work properly
            print "Posting User-Specified Location:", loc.readable_name
            api.do_train(loc.encoded_name, loc.coordinate)
            api.weak_post_location(loc.encoded_name)

    @QtCore.Slot()
    def stop_working(self):
        # Called when user goes offline (or program about to shut down?)
        self.can_work = False


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
        * **post_signal** (PySide.QtCore.Signal(:class:`api.Location`)) --
            When emitted (see :py:meth:`PySide.QtCore.Signal.emit`) with a
            :class:`api.Location` instance, tells the :class:`LocationWorker`
            to bind the current signal strength to the passed-in location and
            to update the user's location on the map
            (:meth:`LocationWorker.post_location`)

    """

    update_signal = QtCore.Signal()
    offline_signal = QtCore.Signal()
    post_signal = QtCore.Signal(api.Location)

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

        if not DEBUG_DONT_CHECK:
            self.setup_background_thread()
            self.start_refresh_timer()

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
        self.open_action = QtGui.QAction(
            "&Open Map",
            self,
            triggered=api.open_map
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
            enabled=False
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

    def start_refresh_timer(self):
        self.bg_thread.start()
        self.refreshTimer = QtCore.QTimer(self)
        self.refreshTimer.timeout.connect(self.refresh_location)
        self.refreshTimer.start(10000)

    def refresh_location(self):
        '''
        Sends a signal to the LocationWorker in bg_thread
        to get the location
        '''
        self.sys_tray.showMessage("Updating", "Determining Location...")
        self.update_signal.emit()

    def post_location(self, loc):
        '''
        Sends a signal to the LocationWorker in bg_thread
        to post a specified location
        '''
        self.post_signal.emit(loc)
        self.location_indicator.setText(loc.get_readable_name())

    def setup_background_thread(self):
        self.bg_thread = QtCore.QThread()
        self.location_worker = LocationWorker()
        self.location_worker.location_updated_signal.connect(self.locationSlot)
        self.update_signal.connect(self.location_worker.get_location)
        self.post_signal.connect(self.location_worker.post_location)
        self.offline_signal.connect(self.location_worker.stop_working)
        self.location_worker.moveToThread(self.bg_thread)

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
        '''
        if reason == QtGui.QSystemTrayIcon.ActivationReason.Trigger:
            #Single Click to open menu
            self.sys_tray.setIcon(self.sys_tray_icon_clicked)
        # NOTE: Below commented because unused. Can use later if we want
        #elif reason == QtGui.QSystemTrayIcon.ActivationReason.DoubleClick:
        #    # Double click
        #    pass

    @QtCore.Slot()
    def sys_tray_menu_closed(self):
        print "Closed Menu"
        # XXX: NEVER GETS TRIGGERED on Mac OsX
        self.sys_tray.setIcon(self.sys_tray_icon_default)

    def sys_tray_quit_action(self):
        '''
        Cleans up and quits the application.
        '''

        self.offline_signal.emit()
        if not DEBUG_DONT_CHECK:
            self.bg_thread.quit()
            while not self.bg_thread.isFinished():
                continue # Wait until thread done
            # On Ubuntu 10.10 (at least), a Python fatal error is encountered if the
            # window is not hidden before the application exits
        self.hide()
        QtGui.qApp.quit()

    def sys_tray_initiate_location_refresh(self):
        self.refresh_location()

    def sys_tray_go_offline(self):
        self.offline_signal.emit()

    # Background actions
    @QtCore.Slot(tuple)
    def locationSlot(self, flagResponseTuple):
        '''
        Slot that gets data whenever a location refresh
        happens
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

def setup_window():
    """Create and return the Preferences window,
    which owns every other element.

    :returns: instance of :class:`PreferencesWindow`

    .. warning:: The window must have a pointer to it, or it will get garbage collected and
        the application won't run

    """
    QtGui.QApplication.setQuitOnLastWindowClosed(False)
    preferences_window = PreferencesWindow()
    #preferencesWindow.display()
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

    app = QtGui.QApplication(sys.argv)
    able_to_launch, reason = can_launch()

    if not able_to_launch:
        print "ERROR: Unable to launch Marauder's Map!"
        print reason
        sys.exit(1)
    else:
        # Note: we have to retain a reference to the window so that it isn't killed
        preferences_window = setup_window()
        sys.exit(app.exec_())
