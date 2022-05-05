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
Module with the GlobalConfigurationFrame which is used for administrating
global settings.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["GlobalConfigurationFrame"]

from functools import partial

from qtpy import QtWidgets, QtCore

from ..core import get_generic_param_collection
from ..core.constants import QSETTINGS_GLOBAL_KEYS
from ..plugins import PluginCollection
from .builders import GlobalConfigurationFrameBuilder


PLUGINS = PluginCollection()


@QtCore.Slot()
def update_plugin_collection():
    """
    Update the plugin collection from the updated QSetting values for the
    plugin directories.
    """
    PLUGINS.clear_collection(True)
    PLUGINS.find_and_register_plugins(*PLUGINS.get_q_settings_plugin_path())


class GlobalConfigurationFrame(GlobalConfigurationFrameBuilder):
    """
    Frame which manages global configuration items.
    """

    default_params = get_generic_param_collection(*QSETTINGS_GLOBAL_KEYS)

    value_changed_signal = QtCore.Signal(str, object)

    def __init__(self, **kwargs):
        parent = kwargs.get("parent", None)
        GlobalConfigurationFrameBuilder.__init__(self, parent)
        self.set_default_params()
        self.build_frame()
        self.connect_signals()
        self.frame_activated(self.frame_index)

    def connect_signals(self):
        """
        Connect the signals for Parameter updates.
        """
        for _param_key in self.params:
            self.param_widgets[_param_key].io_edited.connect(
                partial(self.update_qsetting, _param_key)
            )
        self._widgets["but_reset"].clicked.connect(self.__reset)
        self._widgets["but_plugins"].clicked.connect(update_plugin_collection)

    def update_qsetting(self, param_key, value):
        """
        Update a QSettings value

        Parameters
        ----------
        param_key : str
            The QSettings reference key. A "global/" prefix will be applied
            to it.
        value : object
            The new value.
        """
        self.q_settings.setValue(f"global/{param_key}", value)
        self.value_changed_signal.emit(param_key, value)

    @QtCore.Slot(int)
    def frame_activated(self, index):
        """
        Update the frame.

        The frame_activated slot is called every time a frame is activated.
        The index is the frame_index of the newly activated frame in case any
        cross-options need to be taken.

        Parameters
        ----------
        index : int
            The index of the activated frame.
        """
        if index != self.frame_index:
            return
        for _param_key in self.params:
            _value = self.q_settings_get_global_value(_param_key)
            self.set_param_value_and_widget(_param_key, _value)

    def __reset(self):
        qm = QtWidgets.QMessageBox
        answer = qm.question(
            self, "", "Are you sure to reset all the values?", qm.Yes | qm.No
        )
        if answer == qm.Yes:
            self.restore_all_defaults(True)
            for _param_key in self.params:
                _value = self.get_param_value(_param_key)
                self.update_widget_value(_param_key, _value)
                self.value_changed_signal.emit(_param_key, _value)

    @QtCore.Slot(str, object)
    def external_update(self, param_key, value):
        """
        Perform an update after a Parameter has changed externally.

        Parameters
        ----------
        param_key : str
            The Parameter reference key.
        value : object
            The new value which was set externally.
        """
        value = self._qsettings_convert_value_type(param_key, value)
        self.set_param_value_and_widget(param_key, value)
