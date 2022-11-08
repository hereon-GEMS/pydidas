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
Module with the MainWindow class which extends the MainMenu with a toolbar on the left
to select the different frames.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["MainWindow"]

import os
from functools import partial

from qtpy import QtWidgets, QtCore

from ..core import PydidasGuiError
from ..widgets import InfoWidget
from . import utils
from .main_menu import MainMenu


class MainWindow(MainMenu):
    """
    Inherits from :py:class:`qtpy.QtWidgets.QMainWindow`.

    The MainWindow is used to organize frames and for managing the menu
    and global application parameters.

    Parameters
    ----------
    parent : QtWidgets.QWidget, optional
        The widget's parent. The default is None.
    geometry : Union[tuple, list, None], optional
        The geometry as a 4-tuple or list. The entries are the top left
        corner coordinates (x0, y0) and width and height. If None, the
        default values will be used. The default is None.
    """

    def __init__(self, parent=None, geometry=None):
        MainMenu.__init__(self, parent, geometry)

        self._toolbar_metadata = {}
        self._frames_to_add = []

        self._toolbars = {}
        self._toolbar_actions = {}
        self.__configuration = {"toolbars_created": False}
        self.__create_logging_info_box()

    def __create_logging_info_box(self):
        """
        Create the InfoWidget for logging and status messages.
        """
        self.__info_widget = InfoWidget()
        _dock_widget = QtWidgets.QDockWidget("Logging && information")
        _dock_widget.setWidget(self.__info_widget)
        _dock_widget.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable
            | QtWidgets.QDockWidget.DockWidgetFloatable
        )
        _dock_widget.setBaseSize(500, 50)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, _dock_widget)

    def show(self):
        """
        Insert a create_toolbar_menu method call into the show method if the
        toolbars have not been created at the time of the show call.
        """
        self.create_frame_instances()
        if not self.__configuration["toolbars_created"]:
            self.create_toolbar_menu()
        QtWidgets.QMainWindow.show(self)
        self.centralWidget().currentChanged.emit(0)
        self.centralWidget().sig_mouse_entered.connect(self._reset_toolbar_menu)

    def create_frame_instances(self):
        """
        Create the instances for all registered frames.

        Raises
        ------
        PydidasGuiError
            If a similar menu entry has already been registered.

        """
        while len(self._frames_to_add) > 0:
            _class = self._frames_to_add.pop(0)
            _frame = _class(parent=self.centralWidget())
            _frame.status_msg.connect(self.update_status)
            self.centralWidget().register_frame(_frame)

    def create_toolbar_menu(self):
        """
        Create the toolbar menu to select between different widgets in the
        centralWidget.
        """
        self._toolbar_metadata = self.centralWidget().frame_toolbar_metadata

        self._create_toolbar_menu_entries()
        self._create_toolbars()
        self._create_toolbar_actions()

        for _toolbar_name, _toolbar in self._toolbars.items():
            if _toolbar_name != "":
                self.addToolBarBreak(QtCore.Qt.LeftToolBarArea)
            self.addToolBar(QtCore.Qt.LeftToolBarArea, _toolbar)
            # only make the root toolbar visible to start with:
            _toolbar.setVisible(_toolbar_name == "")
        self.select_item(self.centralWidget().currentWidget().menu_entry)
        self.__configuration["toolbars_created"] = True

    def _create_toolbar_menu_entries(self):
        """
        Create the required toolbar menu entries to populate the menu.
        """
        _menu_entries = []
        for _key in self.centralWidget().frame_toolbar_entries:
            _items = _key.split("/")
            _entries = ["/".join(_items[: _i + 1]) for _i in range(len(_items))]
            for _entry in _entries:
                if _entry not in _menu_entries:
                    _menu_entries.append(_entry)
                if _entry not in self._toolbar_metadata:
                    self._toolbar_metadata[_entry] = utils.create_generic_toolbar_entry(
                        _entry
                    )
        self.__configuration["menu_entries"] = _menu_entries

    def _create_toolbars(self):
        """
        Create the toolbar widgets for the toolbar menu.
        """
        self._toolbars = {}
        for _tb in utils.find_toolbar_bases(self.__configuration["menu_entries"]):
            tb_title = _tb if _tb else "Main toolbar"
            self._toolbars[_tb] = QtWidgets.QToolBar(tb_title, self)
            self._toolbars[_tb].setStyleSheet("QToolBar{spacing:20px;}")
            self._toolbars[_tb].setIconSize(QtCore.QSize(45, 45))
            self._toolbars[_tb].setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            self._toolbars[_tb].setFixedWidth(90)
            self._toolbars[_tb].setMovable(False)
            self._toolbars[_tb].toggleViewAction().setEnabled(False)

    def _create_toolbar_actions(self):
        """
        Create the toolbar actions to swtich between frames.
        """
        for item in self.__configuration["menu_entries"]:
            _icon = self._toolbar_metadata[item]["icon"]
            _label = self._toolbar_metadata[item]["label"]
            _action = QtWidgets.QAction(_icon, _label, self)
            _action.setCheckable(True)
            _action.triggered.connect(partial(self.select_item, item))
            self._toolbar_actions[item] = _action
            itembase = os.path.dirname(item)
            self._toolbars[itembase].addAction(_action)

    def register_frame(self, frame):
        """
        Register a frame class with the MainWindow and add it to the
        PydidasFrameStack.

        This method takes a :py:class:`BaseFrame <pydidas.widgets.BaseFrame>`
        and creates an instance which is registeres with the
        PydidasFrameStack. It also stores the required metadata to create
        a actionbar link to open the frame.

        Parameters
        ----------
        frame : type[pydidas.widgets.BaseFrame]
            The class of the Frame. This must be a subclass of BaseFrame.
            If a string is passed, an empty frame class with the metadata
            given by title, menu_entry and icon is created.
        """
        _stack = self.centralWidget()
        _entry_exists = frame.menu_entry in _stack.get_all_widget_names()
        _class_exists = frame in [_frame.__class__ for _frame in _stack.frames]
        if _entry_exists and _class_exists:
            return
        if _entry_exists or _class_exists:
            raise PydidasGuiError(
                f"Could not register frame '{frame.menu_title}' (class {frame}) "
                "because the menu entry and frame class do not match an already "
                "registered Frame."
            )
        self._frames_to_add.append(frame)

    @QtCore.Slot(str)
    def select_item(self, label):
        """
        Select an item from the left toolbar and select the corresponding
        frame in the centralWidget.

        Parameters
        ----------
        label : str
            The label of the selected item.
        """
        self.setUpdatesEnabled(False)
        for _name, _toolbar in self._toolbars.items():
            _toolbar.setVisible(_name in self._toolbar_metadata[label]["menu_tree"])
        for _name, _action in self._toolbar_actions.items():
            _action.setChecked(
                _name in self._toolbar_metadata[label]["menu_tree"] or _name == label
            )
        if label in self.centralWidget().frame_indices:
            self.centralWidget().activate_widget_by_name(label)
        self.setUpdatesEnabled(True)

    @QtCore.Slot()
    def _reset_toolbar_menu(self):
        """
        Reset the toolbar menu to highlight the current Frame.
        """
        _label = self.centralWidget().active_widget_name
        for _name, _toolbar in self._toolbars.items():
            _toolbar.setVisible(_name in self._toolbar_metadata[_label]["menu_tree"])
        for _name, _action in self._toolbar_actions.items():
            _action.setChecked(
                _name in self._toolbar_metadata[_label]["menu_tree"] or _name == _label
            )

    def restore_gui_state(self, state="saved", filename=None):
        """
        Restore the window states from saved information.

        This method also updates the left toolbar entry according to the restored
        frame.

        Parameters
        ----------
        state: str, optional
            The state to be restored. Can be "saved" to restore the last saved state,
            "exit" to restore the state on exit or "manual" to manually give a filename.
        filename : Union[None, str], optional
            The filename to be used to restore the state. This kwarg will only be used
            if the state kwarg is set to "manual".
        """
        MainMenu.restore_gui_state(self, state, filename)
        self.select_item(self.centralWidget().currentWidget().menu_entry)

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
        if text[-1] != "\n":
            text += "\n"
        self.__info_widget.add_status(text)
