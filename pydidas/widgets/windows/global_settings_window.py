# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the GlobalSettingsWindow class which is a QMainWindow widget
to view and modify the global settings in a seperate Window.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["GlobalSettingsWindow"]

from functools import partial

from qtpy import QtCore, QtWidgets

from ...core import SingletonFactory, get_generic_param_collection
from ...core.constants import CONFIG_WIDGET_WIDTH, QSETTINGS_GLOBAL_KEYS
from ...plugins import PluginCollection
from ..framework import PydidasWindow


PLUGINS = PluginCollection()


class _GlobalSettingsWindow(PydidasWindow):
    """
    The GlobalSettingsWindow is a standalone QMainWindow with the
    GlobalConfigurationFrame as sole content.
    """

    menu_icon = "qta::mdi.application-cog"
    menu_title = "Global configuration"
    menu_entry = "Global configuration"

    value_changed_signal = QtCore.Signal(str, object)

    TEXT_WIDTH = 180
    default_params = get_generic_param_collection(*QSETTINGS_GLOBAL_KEYS)

    def __init__(self, parent=None, **kwargs):
        PydidasWindow.__init__(self, parent, **kwargs)
        self.set_default_params()
        self.setWindowTitle("pydidas system settings")
        self.setFixedWidth(330)

    def build_frame(self):
        """
        Populate the GlobalConfigurationFrame with widgets.
        """
        _options = dict(
            width_text=self.TEXT_WIDTH,
            width_io=80,
            width_unit=40,
            width_total=CONFIG_WIDGET_WIDTH,
        )
        _section_options = dict(fontsize_offset=2, bold=True, gridPos=(-1, 0, 1, 1))

        self.create_label(
            "title",
            "Global settings\n",
            fontsize_offset=4,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self.create_button(
            "but_reset",
            "Restore defaults",
            icon="qt-std::SP_BrowserReload",
            gridPos=(-1, 0, 1, 1),
            alignment=None,
        )
        self.create_label(
            "section_multiprocessing", "Multiprocessing settings", **_section_options
        )
        self.create_param_widget(self.get_param("mp_n_workers"), **_options)
        self.create_param_widget(self.get_param("shared_buffer_max_n"), **_options)
        self.create_spacer("spacer_1")

        self.create_label("section_memory", "Memory settings", **_section_options)
        self.create_param_widget(self.get_param("shared_buffer_size"), **_options)
        self.create_param_widget(self.get_param("max_image_size"), **_options)
        self.create_spacer("spacer_3")

        self.create_label("section_gui", "GUI behaviour", **_section_options)
        self.create_param_widget(self.get_param("plot_update_time"), **_options)

    def connect_signals(self):
        """
        Connect the signals for Parameter updates.
        """
        for _param_key in self.params:
            self.param_widgets[_param_key].io_edited.connect(
                partial(self.update_qsetting, _param_key)
            )
        self._widgets["but_reset"].clicked.connect(self.__reset)

    @QtCore.Slot(object)
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
        self.q_settings_set_key(f"global/{param_key}", value)
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
        super().frame_activated(index)
        if index != self.frame_index:
            return
        for _param_key, _param in self.params.items():
            _value = self.q_settings_get_value(f"global/{_param_key}", _param.dtype)
            self.set_param_value_and_widget(_param_key, _value)

    def __reset(self):
        """
        Reset all Parameters to their default values.
        """
        _qm = QtWidgets.QMessageBox
        answer = QtWidgets.QMessageBox.question(
            self, "", "Are you sure to reset all the values?", _qm.Yes | _qm.No
        )
        if answer == _qm.Yes:
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


GlobalSettingsWindow = SingletonFactory(_GlobalSettingsWindow)
