# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with custom Pydidas DataViews to be used in silx widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Hdf5BrowserWindow"]


from functools import partial
from pathlib import Path
from typing import Union

import h5py
from qtpy import QtCore, QtGui, QtWidgets
from silx.gui import icons as silx_icons
from silx.gui.hdf5 import Hdf5TreeModel, Hdf5TreeView, NexusSortFilterProxyModel

from pydidas.resources.pydidas_icons import pydidas_icon_with_bg
from pydidas.widgets.framework import PydidasWindow
from pydidas_qtcore import PydidasQApplication


class Hdf5BrowserWindow(PydidasWindow):
    """
    A class to browse and display the tree structure of hdf5 files.

    This class is based on the silx Hdf5TreeView and Hdf5TreeModel classes

    Parameters
    ----------
    **kwargs : dict
        Any keyword arguments. Supported kwargs are:

        parent : QtWidgets.QWidget, optional
            The parent widget of the browser.
    """

    def __init__(self, **kwargs):
        self.__qtapp = PydidasQApplication.instance()
        PydidasWindow.__init__(self, title="Hdf5 structure browser", **kwargs)
        self.setWindowIcon(pydidas_icon_with_bg())
        self.__open_file = None

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self._create_treeview()
        self._create_toolbar()
        self.add_any_widget("toolbar", self.__toolbar, gridPos=(0, 0, 1, 1))
        self.add_any_widget("treeview", self._h5_treeview, gridPos=(1, 0, 1, 1))
        self._set_size_and_position()

    def _create_treeview(self):
        """
        Create the tree view for the browser.
        """
        self._h5_treeview = Hdf5TreeView(self)
        self._h5_treeview.setExpandsOnDoubleClick(True)

        _tree_model = Hdf5TreeModel(self._h5_treeview, ownFiles=False)
        self._tree_model_sorted = NexusSortFilterProxyModel(self._h5_treeview)
        self._tree_model_sorted.setSourceModel(_tree_model)
        self._tree_model_sorted.sort(0, QtCore.Qt.AscendingOrder)
        self._tree_model_sorted.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._h5_treeview.setModel(self._tree_model_sorted)

    def _create_toolbar(self):
        """
        Create the toolbar for the tree view
        """
        __default_height = int(1.5 * self.__qtapp.font_height)
        self.__toolbar = QtWidgets.QToolBar(self)
        self.__toolbar.setIconSize(QtCore.QSize(__default_height, __default_height))
        self.__toolbar.setStyleSheet("QToolBar { border: 0px }")

        self._actions = {}
        for _label, _key in [
            ("expand", QtCore.Qt.Key_Plus),
            ("collapse", QtCore.Qt.Key_Minus),
        ]:
            _action = QtWidgets.QAction(self.__toolbar)
            _action.setIcon(silx_icons.getQIcon(f"tree-{_label}-all"))
            _action.setText(f"{_label.capitalize()} all")
            _action.setToolTip(f"{_label.capitalize()} all selected items")
            _action.triggered.connect(
                partial(self.__toggle_selection, _label == "expand")
            )
            _action.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | _key))
            self._actions[_label] = _action
            self.__toolbar.addAction(_action)
            self._h5_treeview.addAction(_action)

        self.__qtapp.sig_new_font_metrics.connect(self._update_toolbar_icons)

    def _set_layout(self):
        """
        Set the layout of the browser.
        """
        _layout = QtWidgets.QVBoxLayout()
        _layout.addWidget(self.__toolbar)
        _layout.addWidget(self._h5_treeview)
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(0)
        self.setLayout(_layout)

    def _set_size_and_position(self):
        """
        Set the size and position of the window
        """
        if self.parent() is None:
            _origin = (50, 50)
        else:
            _origin = (self.parent().x(), self.parent().y())

        _screen_number = self.__qtapp.desktop().screenNumber(self)
        _screen_size = self.__qtapp.desktop().screenGeometry(_screen_number).size()
        _default_size = (
            min(
                int(160 * self.__qtapp.font_char_width),
                _screen_size.width() - _origin[0] - 50,
            ),
            min(
                int(50 * self.__qtapp.font_height),
                _screen_size.height() - _origin[1] - 50,
            ),
        )
        self.move(*_origin)
        self.resize(*_default_size)

    @QtCore.Slot(float, float)
    def _update_toolbar_icons(self, font_width: float, font_height: float):
        """
        Update the toolbar icons based on the font width and height.

        Parameters
        ----------
        font_width : float
        font_height : float
        """
        _icon_size = int(1.5 * font_height)
        self.__toolbar.setIconSize(QtCore.QSize(_icon_size, _icon_size))

    @QtCore.Slot()
    def __toggle_selection(self, expand: bool):
        """
        Expand or collapse all selected items in the tree view.

        Parameters
        ----------
        expand : bool
            If True, expand all selected items. Otherwise, collapse them.
        """
        _selection = self._h5_treeview.selectionModel().selectedIndexes()
        _args = (_selection[0], 10) if expand else (_selection[0],)
        _method_name = "expandRecursively" if expand else "collapse"
        _method = getattr(self._h5_treeview, _method_name)
        _method(*_args)
        if expand:
            QtWidgets.QApplication.restoreOverrideCursor()

    def open_file(self, filename: Union[str, Path]):
        """
        Open a file in the browser
        """
        if self.__open_file is not None:
            self.__open_file.close()
            self.__open_file = None
        self.__open_file = h5py.File(filename, mode="r")
        _h5_model = self._h5_treeview.findHdf5TreeModel()
        _h5_model.clear()
        _h5_model.insertH5pyObject(self.__open_file, filename=filename)
        _root = self._h5_treeview.model().index(0, 0)
        if _root.isValid():
            self._h5_treeview.expandRecursively(_root, 2)
        if self.isMinimized():
            self.showNormal()
        self.show()
        self.raise_()
        self.setFocus()

    def closeEvent(self, event):
        """
        Handle the close event of the widget and assure all files are closed.
        """
        self.__open_file.close()
        self._h5_treeview.findHdf5TreeModel().clear()
        super().closeEvent(event)
