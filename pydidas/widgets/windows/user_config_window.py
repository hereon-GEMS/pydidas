# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the UserConfigWindow class which is a PydidasWindow widget
to view and modify user-specific settings in a seperate Window.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["UserConfigWindow"]


from functools import partial
from pathlib import Path
from typing import Literal

from numpy import ceil, floor
from qtpy import QtCore, QtGui, QtWidgets
from silx.gui.widgets.ColormapNameComboBox import ColormapNameComboBox

from ...core import SingletonFactory, UserConfigError, get_generic_param_collection
from ...core.constants import (
    ALIGN_TOP_RIGHT,
    FONT_METRIC_PARAM_EDIT_WIDTH,
    GENERIC_STANDARD_WIDGET_WIDTH,
    POLICY_EXP_FIX,
    POLICY_MIN_MIN,
    QSETTINGS_USER_KEYS,
)
from ...plugins import PluginCollection, get_generic_plugin_path
from ..dialogues import AcknowledgeBox, QuestionBox, UserConfigErrorMessageBox
from ..factory import SquareButton
from ..framework import PydidasWindow


PLUGINS = PluginCollection()

_BUTTON_POLICY = QtWidgets.QSizePolicy(*POLICY_MIN_MIN)
_BUTTON_POLICY.setHeightForWidth(True)

_FONT_SIZE_VALIDATOR = QtGui.QDoubleValidator(5, 20, 1)
_FONT_SIZE_VALIDATOR.setNotation(QtGui.QDoubleValidator.StandardNotation)


class _UserConfigWindow(PydidasWindow):
    """
    The UserConfigWindow allows to set the user configuration for pydidas.
    """

    menu_icon = "qta::mdi.application-cog"
    menu_title = "User configuration"
    menu_entry = "User configuration"

    value_changed_signal = QtCore.Signal(str, object)

    default_params = get_generic_param_collection(*QSETTINGS_USER_KEYS)

    def __init__(self, parent=None, **kwargs):
        self.__qtapp = QtWidgets.QApplication.instance()
        PydidasWindow.__init__(self, parent, **kwargs)
        self.set_default_params()
        self.setWindowTitle("pydidas user configuration")
        self.setSizePolicy(*POLICY_MIN_MIN)

    def build_frame(self):
        """
        Populate the GlobalConfigurationFrame with widgets.
        """
        self.create_label(
            "title",
            "User configuration\n",
            bold=True,
            fontsize_offset=4,
            gridPos=(0, 0, 1, 1),
        )
        self.create_empty_widget(
            "config_canvas",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        _section_options = dict(
            bold=True,
            fontsize_offset=3,
            gridPos=(-1, 0, 1, 1),
            parent_widget="config_canvas",
        )

        self.create_button(
            "but_reset",
            "Restore defaults",
            alignment=None,
            icon="qt-std::SP_BrowserReload",
            gridPos=(-1, 0, 1, 1),
            parent_widget="config_canvas",
        )
        self.create_spacer(None, parent_widget="config_canvas")

        self.create_label("section_font", "Font settings", **_section_options)
        self.create_empty_widget(
            "fontsize_container",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget="config_canvas",
            toolTip=(
                "Pydidas supports font sizes from 5 pt up to 20 pt. Any entries "
                "outside of this range will be ignored."
            ),
        )
        self.create_label(
            "label_font_size",
            "Standard font size:",
            parent_widget="fontsize_container",
            font_metric_width_factor=0.7 * FONT_METRIC_PARAM_EDIT_WIDTH,
            wordWrap=False,
        )
        self.add_any_widget(
            "but_fontsize_reduce",
            SquareButton(icon="qta::mdi.arrow-bottom-left-thick"),
            gridPos=(0, -1, 1, 1),
            parent_widget="fontsize_container",
        )
        self.create_lineedit(
            "edit_fontsize",
            text=str(QtWidgets.QApplication.instance().font_size),
            parent_widget="fontsize_container",
            gridPos=(0, -1, 1, 1),
            validator=_FONT_SIZE_VALIDATOR,
        )
        self.add_any_widget(
            "but_fontsize_increase",
            SquareButton(icon="qta::mdi.arrow-top-right-thick"),
            gridPos=(0, -1, 1, 1),
            parent_widget="fontsize_container",
        )
        self.create_label(
            "label_font_family",
            "Standard font family:",
            wordWrap=False,
            parent_widget="config_canvas",
        )
        self.add_any_widget(
            "font_family_box",
            QtWidgets.QFontComboBox(),
            alignment=ALIGN_TOP_RIGHT,
            currentText=self.__qtapp.font_family,
            editable=False,
            fontFilter=(
                QtWidgets.QFontComboBox.ScalableFonts
                | QtWidgets.QFontComboBox.MonospacedFonts
            ),
            parent_widget="config_canvas",
            sizePolicy=POLICY_EXP_FIX,
            writingSystem=QtGui.QFontDatabase.Latin,
        )
        self.create_spacer(None, parent_widget="config_canvas")

        self.create_label(
            "section_mosaic", "Composite creator settings", **_section_options
        )
        self.create_param_widget(
            self.get_param("mosaic_border_width"),
            parent_widget="config_canvas",
            width_io=0.18,
            width_text=0.7,
        )
        self.create_param_widget(
            self.get_param("mosaic_border_value"),
            parent_widget="config_canvas",
            width_io=0.25,
            width_text=0.7,
        )
        self.create_spacer("spacer_3", parent_widget="config_canvas")

        self.create_label("section_plotting", "Plot settings", **_section_options)
        self.create_param_widget(
            self.get_param("histogram_outlier_fraction_low"),
            parent_widget="config_canvas",
            width_io=0.25,
            width_text=0.7,
        )
        self.create_param_widget(
            self.get_param("histogram_outlier_fraction_high"),
            parent_widget="config_canvas",
            width_io=0.25,
            width_text=0.7,
        )
        self.create_empty_widget(
            "colormap_editor",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            layout_column_stretches={0: 10, 1: 90},
            parent_widget="config_canvas",
        )
        self.create_label(
            "label_colormap",
            "Default colormap:",
            gridPos=(0, 0, 1, 2),
            parent_widget="colormap_editor",
        )
        self.add_any_widget(
            "cmap_combobox",
            ColormapNameComboBox(),
            parent_widget="colormap_editor",
            gridPos=(1, 1, 1, 1),
        )
        self.create_spacer("spacer_4", parent_widget="config_canvas")

        self.create_label("section_plugins", "Plugins", **_section_options)
        self.create_param_widget(
            self.get_param("plugin_path"), linebreak=True, parent_widget="config_canvas"
        )
        self.param_widgets["plugin_path"].update_size_hint(
            QtCore.QSize(2 * GENERIC_STANDARD_WIDGET_WIDTH, 5)
        )

        self.create_button(
            "but_plugins",
            "Update plugin collection",
            icon="qt-std::SP_BrowserReload",
            parent_widget="config_canvas",
        )
        self.create_button(
            "but_reset_plugins",
            "Restore default plugin collection paths",
            icon="qt-std::SP_DialogOkButton",
            parent_widget="config_canvas",
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
        self._widgets["edit_fontsize"].editingFinished.connect(
            self.process_new_fontsize_setting
        )
        self._widgets["but_fontsize_reduce"].clicked.connect(
            partial(self.change_fontsize, "decrease")
        )
        self._widgets["but_fontsize_increase"].clicked.connect(
            partial(self.change_fontsize, "increase")
        )
        self._widgets["font_family_box"].currentFontChanged.connect(
            self.new_font_family_selected
        )
        self.__qtapp.sig_mpl_font_setting_error.connect(self.mpl_font_not_supported)

    def finalize_ui(self):
        """
        finalize the UI initialization.
        """
        self.setFixedWidth(int(self._widgets["config_canvas"].sizeHint().width() + 20))
        self._widgets["font_family_box"].setFixedWidth(
            int(0.9 * FONT_METRIC_PARAM_EDIT_WIDTH * self.__qtapp.font_char_width)
        )

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

    @QtCore.Slot()
    def change_fontsize(self, change: Literal["increase", "decrease"]):
        """
        Process the button clicks to change the fontsize.

        Parameters
        ----------
        change : Literal["increase", "decrease"]
            The change direction.
        """
        if change == "increase":
            _new_fontsize = min(ceil(self.__qtapp.font_size) + 1, 20)
        elif change == "decrease":
            _new_fontsize = max(floor(self.__qtapp.font_size) - 1, 5)
        self._widgets["edit_fontsize"].setText(str(_new_fontsize))
        self.process_new_fontsize_setting()

    @QtCore.Slot()
    def process_new_fontsize_setting(self):
        """
        Process the user input of the new font size.
        """
        self.__qtapp.font_size = float(self._widgets["edit_fontsize"].text())
        self.setFixedWidth(self._widgets["config_canvas"].sizeHint().width() + 20)
        self._widgets["font_family_box"].setFixedWidth(
            int(0.9 * FONT_METRIC_PARAM_EDIT_WIDTH * self.__qtapp.font_char_width)
        )
        self.adjustSize()

    @QtCore.Slot(QtGui.QFont)
    def new_font_family_selected(self, font: QtGui.QFont):
        """
        Handle the selection of the new font and notify the PydidasQApplication.

        Parameters
        ----------
        font : QtGui.QFont
            The new font.
        """
        self.__qtapp.font_family = font.family()
        self.process_new_fontsize_setting()

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
            self.__qtapp.reset_font_to_standard()
            with QtCore.QSignalBlocker(self._widgets["edit_fontsize"]):
                self._widgets["edit_fontsize"].setText(str(self.__qtapp.font_size))
            with QtCore.QSignalBlocker(self._widgets["font_family_box"]):
                self._widgets["font_family_box"].setCurrentText(
                    self.__qtapp.font_family
                )
            for _param_key in self.params:
                _value = self.get_param_value(_param_key)
                self.update_widget_value(_param_key, _value)
                self.value_changed_signal.emit(_param_key, _value)
            self.process_new_fontsize_setting()

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

    @QtCore.Slot(str)
    def mpl_font_not_supported(self, error: str):
        """
        Handle the signal that matplotlib does not support the chosen font.


        Parameters
        ----------
        error : str
            The error description.
        """
        _ = UserConfigErrorMessageBox(text=error).exec_()


UserConfigWindow = SingletonFactory(_UserConfigWindow)
