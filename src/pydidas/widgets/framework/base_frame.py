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
Module with the BaseFrame, the widget from which all main pydidas frames
should inherit.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["BaseFrame"]


from qtpy import QtCore, QtWidgets

from pydidas.core import (
    ParameterCollection,
    ParameterCollectionMixIn,
    PydidasQsettingsMixin,
)
from pydidas.core.utils import ShowBusyMouse
from pydidas.resources import icons
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas.widgets.parameter_config import ParameterWidgetsMixIn


class BaseFrame(
    QtWidgets.QWidget,
    ParameterCollectionMixIn,
    PydidasQsettingsMixin,
    CreateWidgetsMixIn,
    ParameterWidgetsMixIn,
):
    """
    The BaseFrame is a subclassed QWidget and the base class for all Frames in pydidas.

    By default, a QGridLayout is applied with an alignment of left/top.

    Parameters
    ----------
    **kwargs : dict
        Any additional keyword arguments which might be used by
        subclasses.
    **init_layout : bool, optional
        Flag to initialize the frame layout with a QtWidgets.QGridLayout
        and left / top alignment. If False, no layout will be initialized
        and the subclass is responsible for setting up the layout. The
        default is True.
    """

    show_frame = True
    menu_icon = "qt-std::SP_TitleBarContextHelpButton"
    menu_title = ""
    menu_entry = ""
    params_not_to_restore = []
    status_msg = QtCore.Signal(str)
    sig_closed = QtCore.Signal()
    sig_this_frame_activated = QtCore.Signal()
    default_params = ParameterCollection()

    def __init__(self, **kwargs: dict):
        QtWidgets.QWidget.__init__(self, kwargs.get("parent", None))
        self.setWindowIcon(icons.pydidas_icon_with_bg())
        self.setVisible(False)
        self.setUpdatesEnabled(False)
        CreateWidgetsMixIn.__init__(self)
        PydidasQsettingsMixin.__init__(self)
        ParameterWidgetsMixIn.__init__(self)
        ParameterCollectionMixIn.__init__(self)

        init_layout = kwargs.get("init_layout", True)
        if init_layout:
            _layout = QtWidgets.QGridLayout()
            _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.setLayout(_layout)
        self.frame_index = -1
        self.menu_entry = kwargs.get("menu_entry", self.menu_entry)
        self.menu_title = kwargs.get("title", self.menu_title)
        self.icon = kwargs.get("icon", self.menu_icon)
        self._config = {"built": False}

    @QtCore.Slot(int)
    def frame_activated(self, index: int):
        """
        Received signal that frame has been activated.

        This method is called when this frame becomes activated by the
        central widget. By default, this method will perform no actions.
        If specific frames require any actions, they will need to overwrite
        this method.

        Parameters
        ----------
        index : int
            The index of the activated frame.
        """
        if index == self.frame_index and not self._config["built"]:
            with ShowBusyMouse():
                self.build_frame()
                self.setUpdatesEnabled(True)
                self.connect_signals()
                self.finalize_ui()
                self._config["built"] = True
        if "state" in self._config:
            with ShowBusyMouse():
                _state = self._config.pop("state")
                self.restore_state(_state)
        if index == self.frame_index:
            self.sig_this_frame_activated.emit()

    def build_frame(self):
        """
        Build all widgets of the frame.
        """

    def connect_signals(self):
        """
        Connect all the required signals for the frame.
        """

    def finalize_ui(self):
        """
        finalize the UI initialization.
        """

    def set_status(self, text: str):
        """
        Emit a status message to the main window.

        Parameters
        ----------
        text : str
            The status message to be emitted.
        """
        self.status_msg.emit(text)

    def export_state(self):
        """
        Export the state of the Frame for saving.

        Returns
        -------
        frame_index : int
            The frame index which can be used as key for referencing the state.
        information : dict
            A dictionary with all the information required to export the
            frame's state.
        """
        _params = self.get_param_values_as_dict(filter_types_for_export=True)
        return self.frame_index, {"params": _params}

    def restore_state(self, state: dict):
        """
        Restore the frame's state from stored information.

        The default implementation in the BaseFrame will update all Parameters
        (and associated widgets) and restore the visibility of all widgets. If the
        frame has not yet been built, the state information is only stored internally
        and not yet applied. It will be applied at the next frame activation.

        Parameters
        ----------
        state : dict
            A dictionary with 'params' and 'visibility' keys and the respective
            information for both.
        """
        if not self._config["built"]:
            self._config["state"] = state
            return
        for _key, _val in state["params"].items():
            if _key not in self.params_not_to_restore:
                if _key in self.param_widgets:
                    self.set_param_value_and_widget(_key, _val)
                else:
                    self.set_param_value(_key, _val)

    def closeEvent(self, event: QtCore.QEvent):
        """
        Reimplement the closeEvent to emit a signal about the closing.

        Parameters
        ----------
        event : QtCore.QEvent
            The event which triggered the closeEvent.
        """
        self.sig_closed.emit()
        QtWidgets.QWidget.closeEvent(self, event)
