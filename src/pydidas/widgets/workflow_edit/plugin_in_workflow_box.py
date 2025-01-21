# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with the PluginInWorkflowBox which is a subclassed QFrame and used
to display plugin processing steps in the WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PluginInWorkflowBox"]


from functools import partial

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QFrame

from pydidas.core.constants import ALIGN_CENTER_LEFT, ALIGN_TOP_RIGHT
from pydidas.core.utils import apply_qt_properties
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas.widgets.utilities import get_pyqt_icon_from_str
from pydidas.workflow import WorkflowTree


TREE = WorkflowTree()


class PluginInWorkflowBox(CreateWidgetsMixIn, QFrame):
    """
    Widget to represent a Plugin in the WorkflowTree.

    The widget displays plugin name, title and includes a delete button to remove the
    Plugin or the full branch from the workflow.

    Parameters
    ----------
    plugin_name : str
        The name of the Plugin class.
    widget_id : int
        The widget ID. This is the same as the corresponding node ID.
    **kwargs : dict
        Additional supported keyword arguments are:

        parent : Union[QtWidgets.QWidget, None], optional
            The widget's parent. The default is None.
        label : str, optional
            The node's label. The default is an empty string.
        standard_size : tuple[int, int]
            The standard size in pixel.
    """

    sig_widget_activated = QtCore.Signal(int)
    sig_widget_delete_branch_request = QtCore.Signal(int)
    sig_widget_delete_request = QtCore.Signal(int)
    sig_new_node_parent_request = QtCore.Signal(int, int)
    sig_create_copy_request = QtCore.Signal(int, int)

    def __init__(self, plugin_name: str, widget_id: int, **kwargs: dict):
        QtWidgets.QFrame.__init__(self, kwargs.get("parent", None))
        CreateWidgetsMixIn.__init__(self)
        self.setLayout(QtWidgets.QGridLayout())
        apply_qt_properties(
            self.layout(),
            contentsMargins=(5, 2, 5, 2),
            alignment=ALIGN_CENTER_LEFT,
        )
        self.setAcceptDrops(True)
        self.setObjectName("PluginInWorkflowBox")
        self.setFixedSize(QtCore.QSize(*kwargs.get("standard_size", (220, 50))))
        self.flags = {"active": False, "inconsistent": False}
        self.widget_id = widget_id
        self.setAutoFillBackground(True)

        self.create_label(
            "node_label",
            "",
            fontsize_offset=1,
            bold=True,
            gridPos=(0, 0, 1, 2),
            styleSheet="QLabel{ background-color: rgba(255, 255, 255, 0);}",
            wordWrap=False,
        )
        self.create_label(
            "plugin_name",
            plugin_name,
            fontsize_offset=1,
            gridPos=(2, 0, 1, 3),
            wordWrap=False,
        )
        self.create_label(
            "del_button",
            "",
            pixmap=get_pyqt_icon_from_str("qt-std::SP_TitleBarCloseButton").pixmap(
                QtCore.QSize(16, 16)
            ),
            gridPos=(0, 2, 1, 1),
            fixedWidth=16,
            fixedHeight=16,
            alignment=ALIGN_TOP_RIGHT,
            contextMenuPolicy=QtCore.Qt.CustomContextMenu,
        )
        self._widgets["del_button"].mousePressEvent = self.__show_deletion_context_menu

        self.layout().setRowStretch(1, 1)
        self.layout().setColumnStretch(1, 1)
        self.update_text(widget_id, kwargs.get("label", ""))
        self.__create_menus()
        self.__update_style()

    def update_text(self, node_id: int, label: str = ""):
        """
        Update the text for node label.

        Parameters
        ----------
        node_id : int
            The unique node ID.
        label : str, optional
            The new label for the workflow node.
        """
        _txt = f"node {node_id:d}" + (f": {label}" if len(label) > 0 else "")
        self._widgets["node_label"].setText(_txt)

    def update_plugin(self, plugin_name: str):
        """
        Update the plugin.

        Parameters
        ----------
        plugin_name : str
            The type of the new plugin.
        """
        self._widgets["plugin_name"].setText(plugin_name)
        self.update_text(self.widget_id)

    def __create_menus(self):
        """
        Create custom context menus.

        This method creates two separate context menus for a) moving the node and
        creating node copies and b) for deleting the current node from the tree.
        """
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._menu_item_context = QtWidgets.QMenu(self)
        self.customContextMenuRequested.connect(self._open_context_menu)

        self._menu_move = QtWidgets.QMenu("Move to a new parent", self)
        self._menu_append = QtWidgets.QMenu(
            "Append a plugin copy to specific node", self
        )
        self._menu_item_context.addMenu(self._menu_move)
        self._menu_item_context.addMenu(self._menu_append)

        self._delete_node_context = QtWidgets.QMenu(self)

        self._del_actions = {
            "delete": QtWidgets.QAction("Delete this node", self),
            "delete_branch": QtWidgets.QAction("Delete this branch", self),
        }
        self._del_actions["delete"].triggered.connect(
            partial(self.sig_widget_delete_request.emit, self.widget_id)
        )
        self._del_actions["delete"].triggered.connect(self.deleteLater)
        self._del_actions["delete_branch"].triggered.connect(
            partial(self.sig_widget_delete_branch_request.emit, self.widget_id)
        )
        self._del_actions["delete_branch"].triggered.connect(self.deleteLater)
        self._delete_node_context.addAction(self._del_actions["delete"])
        self._delete_node_context.addAction(self._del_actions["delete_branch"])

    def __show_deletion_context_menu(self, event: QtGui.QMouseEvent):
        """
        Show the node deletion context menu.

        Parameters
        ----------
        event : QtGui.QMouseEvent
            The mouse press event.
        """
        self._delete_node_context.exec(event.globalPosition().toPoint())

    def __update_style(self):
        """
        Update the widget's style based on the stored flags.
        """
        _border = 3 if self.flags["active"] else 1
        if self.flags["inconsistent"]:
            _bg_color = "rgb(255, 225, 225)"
        elif self.flags["active"]:
            _bg_color = "rgb(225, 225, 255)"
        else:
            _bg_color = "rgb(200, 200, 200)"
        self.setStyleSheet(
            "QFrame#PluginInWorkflowBox{ border-radius: 4px; "
            "border-style: solid;"
            "border-color: rgb(60, 60, 60);"
            f"border-width: {_border}px;"
            f"background: {_bg_color};"
            "}"
        )

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """
        Extend the generic mousePressEvent by an activation signal.

        Parameters
        ----------
        event : QtCore.QEvent
            The original event.
        """
        event.accept()
        if not self.flags["active"]:
            self.sig_widget_activated.emit(self.widget_id)

    def delete(self):
        """
        Send the delete request to the WorkflowTreeEditManager.
        """
        self.sig_widget_delete_request.emit(self.widget_id)

    @QtCore.Slot(int)
    def new_widget_selected(self, selection: bool):
        """
        Select or deselect the widget.

        Parameters
        ----------
        selection : bool
            Flag whether the widget has been selected (True) or deselected
            (False).
        """
        self.flags["active"] = self.widget_id == selection
        self.__update_style()

    @QtCore.Slot(list)
    def receive_inconsistent_signal(self, widget_ids: list[int]):
        """
        Handle the node inconsistent signal set the stylesheets.

        Parameters
        ----------
        *widget_ids : list[int]
            The widget node IDs which are inconsistent.
        """
        if self.widget_id in widget_ids and not self.flags["inconsistent"]:
            self.flags["inconsistent"] = True
            self.__update_style()

    @QtCore.Slot(list)
    def receive_consistent_signal(self, widget_ids: list[int]):
        """
        Handle the node consistent signal set the stylesheets.

        Parameters
        ----------
        widget_ids : list[int]
            The widget node ID.
        """
        if self.widget_id in widget_ids and self.flags["inconsistent"]:
            self.flags["inconsistent"] = False
            self.__update_style()

    def mouseMoveEvent(self, event: QtCore.QEvent):
        """
        Implement a mouse move event to drag the plugins to a new position in the
        WorkflowTree.
        """
        if event.buttons() == QtCore.Qt.LeftButton:
            _drag = QtGui.QDrag(self)
            _mime = QtCore.QMimeData()
            _drag.setMimeData(_mime)

            _pixmap = QtGui.QPixmap(self.size())
            self.render(_pixmap)
            _drag.setPixmap(_pixmap)
            _drag.exec_(QtCore.Qt.MoveAction)

    def dragEnterEvent(self, event: QtCore.QEvent):
        """
        Enable dragging of this widget.

        Parameters
        ----------
        event : QtCore.QEvent
            The drag event.
        """
        event.accept()

    def dropEvent(self, event: QtCore.QEvent):
        """
        Allow dropping the widget on other WorkflowNode widgets.

        Parameters
        ----------
        event : QtCore.QEvent
            The drop event.
        """
        _source_widget = event.source()
        event.accept()
        self.sig_new_node_parent_request.emit(_source_widget.widget_id, self.widget_id)

    @QtCore.Slot(QtCore.QPoint)
    def _open_context_menu(self, point: QtCore.QPoint):
        """
        Open the context menu after updating the menu entries based on the
        current WorkflowTree.
        """
        self.__update_menus()
        self._menu_item_context.exec(self.mapToGlobal(point))

    def __update_menus(self):
        """
        Update the menus to move and to append a copy based on the nodes in the Tree.
        """
        self._menu_move.clear()
        self._menu_append.clear()
        self._menu_move_actions = {}
        self._menu_append_actions = {}
        for _id in TREE.node_ids:
            if _id == self.widget_id:
                continue

            _plugin = TREE.nodes[_id].plugin
            _label = _plugin.get_param_value("label")
            _plugin_type = _plugin.plugin_name
            _name = (
                f"{_id}: {_label} [{_plugin_type}]"
                if len(_label) > 0
                else f"{_id} [{_plugin_type}]"
            )
            self._menu_move_actions[_id] = QtWidgets.QAction(_name)
            self._menu_move.addAction(self._menu_move_actions[_id])
            self._menu_move_actions[_id].triggered.connect(
                partial(self._emit_new_parent_signal, _id)
            )
            self._menu_append_actions[_id] = QtWidgets.QAction(_name)
            self._menu_append.addAction(self._menu_append_actions[_id])
            self._menu_append_actions[_id].triggered.connect(
                partial(self._emit_create_copy_signal, _id)
            )

    @QtCore.Slot(int)
    def _emit_new_parent_signal(self, new_parent_id: int):
        """
        Emit the signal to move the node to a new parent.

        Parameters
        ----------
        new_parent_id: int
            The id of the new parent node.
        """
        self.sig_new_node_parent_request.emit(self.widget_id, new_parent_id)

    @QtCore.Slot(int)
    def _emit_create_copy_signal(self, new_parent_id: int):
        """
        Emit the signal to move the node to a new parent.

        Parameters
        ----------
        new_parent_id: int
            The id of the new parent node.
        """
        self.sig_create_copy_request.emit(self.widget_id, new_parent_id)
