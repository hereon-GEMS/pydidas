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
Module with the UserConfigWindow class which is a QMainWindow widget
to view and modify user-specific settings in a seperate Window.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["UserConfigWindow"]


from functools import partial
from pathlib import Path

from qtpy import QtCore, QtWidgets
from silx.gui.widgets.ColormapNameComboBox import ColormapNameComboBox

from ...core import SingletonFactory, UserConfigError, get_generic_param_collection
from ...core.constants import (
    CONFIG_WIDGET_WIDTH,
    QSETTINGS_USER_KEYS,
    QT_TOP_RIGHT_ALIGNMENT,
    STANDARD_FONT_SIZE,
)
from ...plugins import PluginCollection, get_generic_plugin_path
from ...widgets.dialogues import AcknowledgeBox, QuestionBox
from .pydidas_window import PydidasWindow


PLUGINS = PluginCollection()


class _UserConfigWindow(PydidasWindow):
    """
    The UserConfigWindow is a standalone QMainWindow with the
    GlobalConfigurationFrame as sole content.
    """

    menu_icon = "qta::mdi.application-cog"
    menu_title = "User configuration"
    menu_entry = "User configuration"

    value_changed_signal = QtCore.Signal(str, object)

    TEXT_WIDTH = 180
    default_params = get_generic_param_collection(*QSETTINGS_USER_KEYS)

    def __init__(self, parent=None, **kwargs):
        PydidasWindow.__init__(self, parent, **kwargs)
        self.set_default_params()
        self.setWindowTitle("pydidas user configuration")
        self.setFixedWidth(330)

    def build_frame(self):
        """
        Populate the GlobalConfigurationFrame with widgets.
        """
        _twoline_options = dict(
            width_text=self.TEXT_WIDTH,
            linebreak=True,
            width_io=CONFIG_WIDGET_WIDTH - 20,
            width_total=CONFIG_WIDGET_WIDTH,
            halign_text=QtCore.Qt.AlignLeft,
            valign_text=QtCore.Qt.AlignBottom,
            width_unit=0,
        )
        _options = dict(
            width_text=self.TEXT_WIDTH,
            width_io=80,
            width_unit=40,
            width_total=CONFIG_WIDGET_WIDTH,
        )
        _section_options = dict(
            fontsize=STANDARD_FONT_SIZE + 3, bold=True, gridPos=(-1, 0, 1, 1)
        )

        self.create_label(
            "title",
            "User configuration\n",
            fontsize=STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self.create_button(
            "but_reset",
            "Restore defaults",
            icon=self.style().standardIcon(59),
            gridPos=(-1, 0, 1, 1),
            alignment=None,
        )

        self.create_label(
            "section_mosaic", "Composite creator settings", **_section_options
        )
        self.create_param_widget(self.get_param("mosaic_border_width"), **_options)
        self.create_param_widget(self.get_param("mosaic_border_value"), **_options)
        self.create_spacer("spacer_3")

        self.create_label("section_plotting", "Plot settings", **_section_options)
        self.create_param_widget(
            self.get_param("histogram_outlier_fraction_low"),
            **(_twoline_options | {"width_io": 80, "width_text": CONFIG_WIDGET_WIDTH}),
        )
        self.create_param_widget(
            self.get_param("histogram_outlier_fraction_high"),
            **(_twoline_options | {"width_io": 80, "width_text": CONFIG_WIDGET_WIDTH}),
        )
        self.create_empty_widget("colormap_editor", fixedWidth=CONFIG_WIDGET_WIDTH)
        self.create_label(
            "label_colormap",
            "Default colormap:",
            gridPos=(0, 0, 1, 2),
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["colormap_editor"],
        )
        self.add_any_widget(
            "cmap_combobox",
            ColormapNameComboBox(),
            parent_widget=self._widgets["colormap_editor"],
            fixedWidth=(CONFIG_WIDGET_WIDTH - 20),
            gridPos=(1, 1, 1, 1),
            layout_kwargs={"alignment": QT_TOP_RIGHT_ALIGNMENT},
        )
        self.create_spacer("spacer_4")

        self.create_label("section_plugins", "Plugins", **_section_options)
        self.create_param_widget(self.get_param("plugin_path"), **_twoline_options)
        self.create_button("but_plugins", "Update plugin collection", icon="qt-std::59")
        self.create_button(
            "but_reset_plugins",
            "Restore default plugin collection paths",
            icon="qt-std::39",
        )

    def connect_signals(self):
        """
        Connect the signals for Parameter updates.
        """
        for _param_key in self.params:
            self.param_widgets[_param_key].io_edited.connect(
                partial(self.update_qsetting, _param_key)
            )
        self._widgets["but_reset"].clicked.connect(self.__reset)
        self._widgets["but_plugins"].clicked.connect(self.update_plugin_collection)
        self._widgets["but_reset_plugins"].clicked.connect(self.reset_plugins)
        self._widgets["cmap_combobox"].currentTextChanged.connect(self.update_cmap)

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
        self.q_settings_set_key(f"user/{param_key}", value)
        self.value_changed_signal.emit(param_key, value)

    @QtCore.Slot()
    def update_plugin_collection(self):
        """
        Update the plugin collection from the updated QSetting values for the
        plugin directories.
        """
        _paths = PLUGINS.get_q_settings_plugin_paths()
        if _paths == [Path()]:
            self.set_param_value_and_widget(
                "plugin_path", str(get_generic_plugin_path()[0])
            )
            raise UserConfigError(
                "Warning! No plugin paths have been selected. Resetting paths to the "
                "default path value."
            )
        PLUGINS.clear_collection(True)
        PLUGINS.find_and_register_plugins(*PLUGINS.get_q_settings_plugin_paths())

    @QtCore.Slot()
    def reset_plugins(self):
        """
        Reset the plugin paths to the default.
        """
        _reply = QuestionBox(
            "Reset PluginCollection paths",
            "Do you want to reset the PluginCollection paths and lose all changes?",
        ).exec_()
        if _reply:
            self.set_param_value_and_widget(
                "plugin_path", str(get_generic_plugin_path()[0])
            )
            PLUGINS.clear_collection(True)
            PLUGINS.find_and_register_plugins(*PLUGINS.get_q_settings_plugin_paths())

    @QtCore.Slot(str)
    def update_cmap(self, cmap_name):
        """
        Update the default colormap.

        Parameters
        ----------
        cmap_name : str
            The name of the new colormap.
        """
        _ack = self.q_settings_get_value("user/cmap_acknowledge")
        if _ack is None:
            _set_ack = AcknowledgeBox(
                text=(
                    "Changing the default colormap will only become active after "
                    "restarting pydidas."
                )
            ).exec_()
            if _set_ack:
                self.q_settings_set_key("user/cmap_acknowledge", True)
        self.q_settings_set_key("user/cmap_name", cmap_name)

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
            _value = self.q_settings_get_value(f"user/{_param_key}", _param.dtype)
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


UserConfigWindow = SingletonFactory(_UserConfigWindow)
