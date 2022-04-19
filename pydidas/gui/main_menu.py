# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the MainMenu class which is a subclassed QMainWindow and which
manages the pydidas GUI menu.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['MainMenu']

import os
import sys
from functools import partial

import yaml
from qtpy import QtWidgets, QtGui, QtCore

from pydidas.core import FrameConfigError
from pydidas.core.utils import get_doc_home_qurl
from pydidas.experiment import ScanSetup, ExperimentalSetup
from pydidas.workflow import WorkflowTree
from pydidas.widgets import (CentralWidgetStack, excepthook)
from pydidas.widgets.dialogues import QuestionBox
from pydidas.gui import utils
from pydidas.gui.windows import (
    GlobalConfigWindow, ExportEigerPixelmaskWindow, AverageImagesWindow)


SCAN = ScanSetup()
EXP = ExperimentalSetup()
TREE = WorkflowTree()


class MainMenu(QtWidgets.QMainWindow):
    """
    Inherits from :py:class:`qtpy.QtWidgets.QMainWindow`.

    The MainWindowWindow is a bare QMainWindow with a menu.

    Parameters
    ----------
    parent : QtWidgets.QWidget, optional
        The widget's parent. The default is None.
    geometry : Union[tuple, list, None], optional
        The geometry as a 4-tuple or list. The entries are the top left
        corner coordinates (x0, y0) and width and height. If None, the
        default values will be used. The default is None.
    """
    STATE_FILENAME = 'pydidas_gui_state.yaml'

    def __init__(self, parent=None, geometry=None):
        super().__init__(parent)
        utils.configure_qtapp_namespace()
        utils.update_qtapp_font_size()
        utils.apply_tooltip_event_filter()
        sys.excepthook = excepthook

        self._child_windows = {}
        self._actions = {}
        self._menus = {}

        self._setup_mainwindow_widget(geometry)
        self._add_global_config_window()
        self._create_menu()

    def _setup_mainwindow_widget(self, geometry):
        """
        Setup the user interface.

        Parameters
        ----------
        geometry : Union[tuple, list, None], optional
            The geometry as a 4-tuple or list. The entries are the top left
            corner coordinates (x0, y0) and width and height. If None, the
            default values will be used. The default is None.
        """
        if isinstance(geometry, (tuple, list)) and len(geometry) == 4:
            self.setGeometry(*geometry)
        else:
            self.setGeometry(40, 60, 1400, 1000)
        self.setCentralWidget(CentralWidgetStack())
        self.statusBar().showMessage('pydidas started')
        self.setWindowTitle('pydidas GUI (alpha)')
        self.setWindowIcon(utils.get_pydidas_icon())
        self.setFocus(QtCore.Qt.OtherFocusReason)

    def _add_global_config_window(self):
        """
        Add the required widgets and signals for the global configuration
        window and create it.
        """
        self._child_windows['global_config'] = GlobalConfigWindow(self)

    def _create_menu(self):
        """
        Create the application's main menu.
        """
        self._create_menu_actions()
        self._connect_menu_actions()
        self._add_actions_to_menu()

    def _create_menu_actions(self):
        """
        Create all required actions for the menu entries and store them in the
        internal _actions dictionary.
        """
        store_state_action = QtWidgets.QAction(
            '&Store GUI state', self)
        store_state_action.setStatusTip(
            'Store the current state of the graphical user interface including'
            ' all frame Parameters and App configurations. This action allows '
            'users to store their state in the machines configuration for '
            'loading it again at a later date.')
        self._actions['store_state'] = store_state_action

        export_state_action = QtWidgets.QAction(
            '&Export GUI state', self)
        export_state_action.setStatusTip(
            'Export the current state of the graphical user interface '
            'to a user-defined file. This includes all frame Parameters and '
            'App configurations.')
        self._actions['export_state'] = export_state_action

        restore_state_action = QtWidgets.QAction(
            '&Restore GUI state', self)
        restore_state_action.setStatusTip(
            'Restore the state of the graphical user interface from a '
            'previously created snapshot.')
        self._actions['restore_state'] = restore_state_action

        import_state_action = QtWidgets.QAction(
            '&Import GUI state', self)
        import_state_action.setStatusTip(
            'Import the state of the graphical user interface from a '
            'user-defined file.')
        self._actions['import_state'] = import_state_action

        exit_action = QtWidgets.QAction(QtGui.QIcon('exit.png'), 'E&xit', self)
        exit_action.setStatusTip('Exit application')
        self._actions['exit'] = exit_action

        self._actions['open_settings'] = QtWidgets.QAction('&Settings', self)
        self._actions['export_eiger_pixel_mask'] = (
            QtWidgets.QAction('&Export Eiger Pixelmask', self))
        self._actions['average_images'] = (
            QtWidgets.QAction('&Average images', self))

        self._actions['open_documentation_browser'] = QtWidgets.QAction(
            'Open documentation in default web browser', self)

    def _connect_menu_actions(self):
        """
        Connect all menu actions to their respective slots.
        """
        self._actions['store_state'].triggered.connect(
            self._action_store_state)
        self._actions['export_state'].triggered.connect(
            self._action_export_state)
        self._actions['restore_state'].triggered.connect(
            self._action_restore_state)
        self._actions['import_state'].triggered.connect(
            self._action_import_state)
        self._actions['exit'].triggered.connect(self.close)
        self._actions['open_settings'].triggered.connect(
            partial(self.show_window, 'global_config'))
        self._actions['export_eiger_pixel_mask'].triggered.connect(
            self._action_export_eiger_pixel_mask)
        self._actions['average_images'].triggered.connect(
            self._action_average_images)
        self._actions['open_documentation_browser'].triggered.connect(
            self._action_open_doc_in_browser)

    def _add_actions_to_menu(self):
        """
        Add the defined actions to the menu bar.
        """
        _menu = self.menuBar()

        _state_menu = QtWidgets.QMenu('&GUI state', self)
        _state_menu.addAction(self._actions['store_state'])
        _state_menu.addAction(self._actions['export_state'])
        _state_menu.addSeparator()
        _state_menu.addAction(self._actions['restore_state'])
        _state_menu.addAction(self._actions['import_state'])

        _file_menu = _menu.addMenu('&File')
        _file_menu.addMenu(_state_menu)
        _file_menu.addAction(self._actions['exit'])
        _menu.addMenu(_file_menu)

        _extras_menu = _menu.addMenu('&Extras')
        _extras_menu.addAction(self._actions['open_settings'])
        _extras_menu.addAction(self._actions['export_eiger_pixel_mask'])
        _extras_menu.addAction(self._actions['average_images'])
        _menu.addMenu(_extras_menu)

        _help_menu = _menu.addMenu('&Help')
        _help_menu.addAction(self._actions['open_documentation_browser'])
        _menu.addMenu(_help_menu)

        self._menus['file'] = _file_menu
        self._menus['state'] = _state_menu
        self._menus['extras'] = _extras_menu
        self._menus['help'] = _help_menu

    @QtCore.Slot()
    def _action_store_state(self):
        """
        Store the current GUI state in a generic file.
        """
        _reply = QuestionBox('Store GUI state',
                             'Do you want to store the current GUI state '
                             '(and overwrite any previous states)?').exec_()
        if _reply:
            self.export_gui_state()

    @QtCore.Slot()
    def _action_export_state(self):
        """
        Store the current GUI state in a user-defined file.
        """
        fname =  QtWidgets.QFileDialog.getSaveFileName(
            self, 'Name of file for export', None, 'YAML (*.yaml *.yml)')[0]
        if fname != '':
            self.export_gui_state(fname)

    @QtCore.Slot()
    def _action_restore_state(self):
        """
        Restore the GUI state from a generic file.
        """
        _reply = QuestionBox(
            'Restore GUI state',
            'Do you want to restore the GUI state? This will reset any changes'
            ' you made and you might lose work.').exec_()
        if _reply:
            self.restore_gui_state()

    @QtCore.Slot()
    def _action_import_state(self):
        """
        Restore the GUI state from a user-defined file.
        """
        fname =  QtWidgets.QFileDialog.getOpenFileName(
            self, 'Name of file', None, 'YAML (*.yaml *.yml)')[0]
        if fname != '':
            self.restore_gui_state(fname)

    @QtCore.Slot()
    def _action_export_eiger_pixel_mask(self):
        """
        Open dialogues to export an Eiger pixelmask.
        """
        self._child_windows['tmp'] = ExportEigerPixelmaskWindow()
        self._child_windows['tmp'].show()

    @QtCore.Slot()
    def _action_average_images(self):
        """
        Open dialogue to average multiple frames and store them in a new file.
        """
        self._child_windows['tmp'] = AverageImagesWindow()
        self._child_windows['tmp'].show()

    @QtCore.Slot()
    def _action_open_doc_in_browser(self):
        """
        Open the link to the documentation in the system web browser.
        """
        _ = QtGui.QDesktopServices.openUrl(get_doc_home_qurl())

    @QtCore.Slot(str)
    def update_status(self, text):
        """
        Get a text message and show it in the global status widget.

        This slot can be used by any QObject to send an update which will be
        added to the global list of status messages.

        Parameters
        ----------
        text : str
            The status message.
        """
        self.statusBar().showMessage(text)
        if text[-1] != '\n':
            text += '\n'
        self.__info_widget.add_status(text)

    @QtCore.Slot(str)
    def show_window(self, name):
        """
        Show a separate window.

        Parameters
        ----------
        name : str
            The name key of the window to be shown.
        """
        self._child_windows[name].show()

    def deleteLater(self):
        """
        Add deleteLater entries for the associated windows.
        """
        for _window in self._child_windows.values():
            try:
                _window.deleteLater()
            except RuntimeError:
                pass
        self.centralWidget().deleteLater()
        super().deleteLater()

    def export_gui_state(self, filename=None):
        """
        This function

        Parameters
        ----------
        filename : Union[None, str]
            The full file system path of the configuration file. If None, a
            generic file will be created by pydidas. The default is None.
        """
        if filename is None:
            _config_path = QtCore.QStandardPaths.standardLocations(
                QtCore.QStandardPaths.ConfigLocation)[0]
            filename = os.path.join(_config_path, self.STATE_FILENAME)
        _state = self.__get_window_states()
        for _index, _widget in enumerate(self.centralWidget().widgets):
            _frameindex, _widget_state = _widget.export_state()
            assert _index == _frameindex
            _state[f'frame_{_index:02d}'] = _widget_state
        _state['scan_setup'] = SCAN.get_param_values_as_dict(
            filter_types_for_export=True)
        _state['exp_setup'] = EXP.get_param_values_as_dict(
            filter_types_for_export=True)
        _state['workflow_tree'] = TREE.export_to_string()
        with open(filename, 'w') as _file:
            yaml.dump(_state, _file, Dumper=yaml.SafeDumper)

    def __get_window_states(self):
        """
        Get the states of the main window and all child windows for exporting.

        Returns
        -------
        _window_states : dict
            The dictionary with the required information to store and restore
            window states.
        """
        _window_states = {}
        for _key, _window in self._child_windows.items():
            if _key != 'tmp':
                _window_states[_key] = _window.export_window_state()
        _window_states['main'] = self.__export_mainwindow_state()
        return _window_states

    def __export_mainwindow_state(self):
        """
        Export the main window's state.

        Returns
        -------
        dict
            The state of the main window required to restore the look.
        """
        return {'geometry': self.geometry().getRect(),
                'frame_index': self.centralWidget().currentIndex()}

    def restore_gui_state(self, filename=None):
        """
        Restore the window states from saved information.

        If the filename is not specified, the internally used file for storing
        the state will be opened.

        Parameters
        ----------
        filename : Union[None, str], optional
            The filename to be used to restore the state. Pydidas will use the
            internal default if the filename is None. The default is None.
        """
        if filename is None:
            filename = self._get_standard_state_filename()
        with open(filename, 'r') as _file:
            _state = yaml.load(_file, Loader=yaml.SafeLoader)
        self._restore_global_objects(_state)
        self._restore_window_states(_state)
        self._restore_frame_states(_state)

    def _get_standard_state_filename(self):
        """
        Get the standard filename for the stored state.

        This method will search all stored config paths and return the first
        match.

        Returns
        -------
        _fname : str
            The file name and path to the config file.
        """
        _paths = QtCore.QStandardPaths.standardLocations(
            QtCore.QStandardPaths.ConfigLocation)
        for _path in _paths:
            _fname = os.path.join(_path, self.STATE_FILENAME)
            if os.path.isfile(_fname) and os.access(_fname, os.R_OK):
                return _fname
        raise FileNotFoundError('No state config file found.')

    def _restore_global_objects(self, state):
        """
        Get the states of pydidas' global objects (ScanSetup,
        ExperimentalSetup, WorkflowTree)

        Parameters
        ----------
        state : dict
            The restored global states which includes the states for the
            global objects.
        """
        TREE.restore_from_string(state['workflow_tree'])
        for _key, _val in state['scan_setup'].items():
            SCAN.set_param_value(_key, _val)
        for _key, _val in state['exp_setup'].items():
            EXP.set_param_value(_key, _val)


    def _restore_window_states(self, state):
        """
        Get the states of the main window and all child windows for exporting.

        Returns
        -------
        state : dict
            The dictionary with the required information to store and restore
            window states.
        """
        for _key, _window in self._child_windows.items():
            if _key != 'tmp':
                _window.restore_window_state(state[_key])
        self.__restore_mainwindow_state(state['main'])

    def __restore_mainwindow_state(self, state):
        """
        Restore the main window's state from saved information.

        Parameters
        ----------
        state : dict
            The stored state of the main window.
        """
        self.setGeometry(*state['geometry'])
        _frame_index = state['frame_index']
        if _frame_index >= 0:
            self.centralWidget().setCurrentIndex(_frame_index)

    def _restore_frame_states(self, state):
        """
        Restore the states of all the frames in the CentralWidgetStack.

        Parameters
        ----------
        state : dict
            The state information for all frames.
        """
        _frame_info = [f'frame_{_index:02d}' in state.keys() for _index, _
                       in enumerate(self.centralWidget().widgets)]
        if False in _frame_info:
            raise FrameConfigError('The state is not defined for all frames.')
        for _index, _frame in enumerate(self.centralWidget().widgets):
            _frame.restore_state(state[f'frame_{_index:02d}'])

    def closeEvent(self, event):
        """
        Handle the Qt closeEvent.

        This method adds calls to the child windows to close themselves.

        Parameters
        ----------
        event : QtCore.QEvent
            The closing event.
        """
        for window in self._child_windows:
            self._child_windows[window].deleteLater()
            self._child_windows[window].close()
        event.accept()
