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
Module with the UserConfigWindow class which is a PydidasWindow widget
to view and modify user-specific settings in a separate Window.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["UserConfigWindow"]


from functools import partial
from typing import Union

from numpy import ceil, floor
from qtpy import QtCore, QtGui, QtWidgets
from silx.gui.widgets.ColormapNameComboBox import ColormapNameComboBox

from pydidas.core import SingletonFactory, get_generic_param_collection
from pydidas.core.constants import (
    ALIGN_TOP_RIGHT,
    FONT_METRIC_PARAM_EDIT_WIDTH,
    GENERIC_PLUGIN_PATH,
    GENERIC_STANDARD_WIDGET_WIDTH,
    POLICY_EXP_FIX,
    POLICY_MIN_MIN,
    QSETTINGS_USER_KEYS,
    QT_REG_EXP_RGB_VALIDATOR,
)
from pydidas.core.generic_params.generic_params_settings import GENERIC_PARAMS_SETTINGS
from pydidas.core.utils import update_palette
from pydidas.plugins import PluginCollection
from pydidas.widgets.dialogues import PydidasExceptionMessageBox, QuestionBox
from pydidas.widgets.factory import SquareButton
from pydidas.widgets.framework import PydidasWindow
from pydidas_qtcore import PydidasQApplication


PLUGINS = PluginCollection()

_BUTTON_POLICY = QtWidgets.QSizePolicy(*POLICY_MIN_MIN)
_BUTTON_POLICY.setHeightForWidth(True)

_FONT_SIZE_VALIDATOR = QtGui.QDoubleValidator(5, 20, 1)
_FONT_SIZE_VALIDATOR.setNotation(QtGui.QDoubleValidator.StandardNotation)


class _UserConfigWindow(PydidasWindow):
    """
    The UserConfigWindow allows to set the user configuration for pydidas.
    """

    menu_icon = "mdi::application-cog-outline"
    menu_title = "User configuration"
    menu_entry = "User configuration"

    value_changed_signal = QtCore.Signal(str, object)

    default_params = get_generic_param_collection(*QSETTINGS_USER_KEYS)

    def __init__(self, **kwargs: dict):
        self.__qtapp = PydidasQApplication.instance()
        PydidasWindow.__init__(self, **kwargs)
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
            SquareButton(icon="mdi::arrow-bottom-left-thick"),
            gridPos=(0, -1, 1, 1),
            parent_widget="fontsize_container",
        )
        self.create_lineedit(
            "edit_fontsize",
            text=str(PydidasQApplication.instance().font_size),
            parent_widget="fontsize_container",
            gridPos=(0, -1, 1, 1),
            validator=_FONT_SIZE_VALIDATOR,
        )
        self.add_any_widget(
            "but_fontsize_increase",
            SquareButton(icon="mdi::arrow-top-right-thick"),
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

        self.create_label("section_updates", "Update settings", **_section_options)
        self.create_param_widget(
            self.get_param("auto_check_for_updates"),
            parent_widget="config_canvas",
            width_io=0.25,
            width_text=0.7,
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
            self.get_param("max_number_curves"),
            parent_widget="config_canvas",
            width_io=0.25,
            width_text=0.7,
        )
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
        self.create_empty_widget(
            "cmap_nan_color_container",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget="config_canvas",
            toolTip=GENERIC_PARAMS_SETTINGS["cmap_nan_color"]["tooltip"],
        )
        self.create_param_widget(
            self.get_param("cmap_nan_color"),
            gridPos=(0, 0, 1, 2),
            parent_widget="cmap_nan_color_container",
            width_io=0.25,
            width_text=0.75,
        )
        self.param_widgets["cmap_nan_color"].setValidator(QT_REG_EXP_RGB_VALIDATOR)
        self.create_label(
            "cmap_nan_display_label",
            "Currently selected invalid data color:",
            font_metric_width_factor=0.75 * FONT_METRIC_PARAM_EDIT_WIDTH,
            gridPos=(1, 0, 1, 1),
            parent_widget="cmap_nan_color_container",
        )
        self.create_label(
            "cmap_nan_display_current",
            "",
            autoFillBackground=True,
            font_metric_width_factor=0.25 * FONT_METRIC_PARAM_EDIT_WIDTH,
            gridPos=(1, 1, 1, 1),
            parent_widget="cmap_nan_color_container",
        )
        self.create_button(
            "but_select_cmap_nan_color",
            "Pick a new color for invalid data / no data / NaN",
            parent_widget="cmap_nan_color_container",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )

        self.create_spacer("spacer_4", parent_widget="config_canvas")
        self.create_label("section_plugins", "Plugins", **_section_options)
        self.create_label(
            "label_default_plugin_title",
            "Generic plugin location (not editable):",
            parent_widget="config_canvas",
        )
        self.create_empty_widget(
            "generic_plugin_box",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            layout_column_stretches={0: 10, 1: 90},
            parent_widget="config_canvas",
        )
        self.create_lineedit(
            "label_default_plugin",
            readOnly=True,
            gridPos=(0, 1, 1, 1),
            parent_widget="generic_plugin_box",
            text=str(GENERIC_PLUGIN_PATH).replace("\\", "/"),
        )
        update_palette(self._widgets["label_default_plugin"], base="#F0F0F0")
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

    def connect_signals(self):
        """
        Connect the signals for Parameter updates.
        """
        for _param_key in self.params:
            if _param_key.startswith("cmap"):
                continue
            self.param_widgets[_param_key].io_edited.connect(
                partial(self.update_qsetting, _param_key)
            )
        self._widgets["but_plugins"].clicked.connect(self.update_plugin_collection)
        self._widgets["but_reset"].clicked.connect(self.__reset)
        self._widgets["cmap_combobox"].currentTextChanged.connect(self.update_cmap)
        self._widgets["edit_fontsize"].editingFinished.connect(
            self.process_new_fontsize_setting
        )
        self._widgets["but_fontsize_reduce"].clicked.connect(
            partial(self.change_fontsize, -1)
        )
        self._widgets["but_fontsize_increase"].clicked.connect(
            partial(self.change_fontsize, 1)
        )
        self._widgets["font_family_box"].currentFontChanged.connect(
            self.new_font_family_selected
        )
        self.param_widgets["cmap_nan_color"].editingFinished.connect(
            partial(self._update_cmap_nan_value, None)
        )
        self._widgets["but_select_cmap_nan_color"].clicked.connect(
            self.select_new_nan_color
        )
        self.__qtapp.sig_mpl_font_setting_error.connect(self.mpl_font_not_supported)

    def finalize_ui(self):
        """
        finalize the UI initialization.
        """
        self._config["cmap_nan_palette"] = QtGui.QPalette()
        self._update_cmap_nan_current_color(self.q_settings_get("user/cmap_nan_color"))
        self.setFixedWidth(int(self._widgets["config_canvas"].sizeHint().width() + 20))
        self._widgets["font_family_box"].setFixedWidth(
            int(0.9 * FONT_METRIC_PARAM_EDIT_WIDTH * self.__qtapp.font_char_width)
        )
        _default_cmap = self.q_settings_get("user/cmap_name", default="Gray")
        with QtCore.QSignalBlocker(self._widgets["cmap_combobox"]):
            self._widgets["cmap_combobox"].setCurrentText(_default_cmap)

    @QtCore.Slot(object)
    def update_qsetting(self, param_key: str, value: object):
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
        self.q_settings_set(f"user/{param_key}", value)
        self.value_changed_signal.emit(param_key, value)

    @QtCore.Slot(QtGui.QColor)
    def _update_cmap_nan_value(self, new_value: Union[None, QtGui.QColor]):
        """
        Update the stored value for the colormap NaN.

        Parameters
        ----------
        new_value : Union[None, str]
            The new value. If None, the Parameter input value will be used.
        """
        if new_value is None:
            new_value = self.get_param_value("cmap_nan_color").upper()
            self.update_widget_value("cmap_nan_color", new_value)
        elif isinstance(new_value, QtGui.QColor):
            new_value = new_value.name().upper()
        self.update_qsetting("cmap_nan_color", new_value)
        self._update_cmap_nan_current_color(new_value)
        self.update_widget_value("cmap_nan_color", new_value)

    def _update_cmap_nan_current_color(self, new_color: Union[QtGui.QColor, str]):
        """
        Update the label's current NaN color display with the new value.

        Parameters
        ----------
        new_color : Union[QtGui.QColor, str]
            The new window color.
        """
        if isinstance(new_color, str):
            new_color = QtGui.QColor(new_color)
        self._config["cmap_nan_palette"].setColor(QtGui.QPalette.Window, new_color)
        self._widgets["cmap_nan_display_current"].setPalette(
            self._config["cmap_nan_palette"]
        )

    @QtCore.Slot()
    def select_new_nan_color(self):
        """
        Select a new NaN color using a QColorDialog.
        """
        if self._config.get("nan_colordialog") is None:
            self._config["nan_colordialog"] = QtWidgets.QColorDialog(self)
            self._config["nan_colordialog"].colorSelected.connect(
                self._update_cmap_nan_value
            )
        _current = QtGui.QColor(self.q_settings_get("user/cmap_nan_color"))
        self._config["nan_colordialog"].setCurrentColor(_current)
        self._config["nan_colordialog"].show()

    @QtCore.Slot()
    def update_plugin_collection(self):
        """
        Update the plugin collection from the updated QSetting values for the
        plugin directories.
        """
        _reply = QuestionBox(
            "Update plugin paths",
            (
                "Do you want to update the custom plugin paths? This will clear the "
                "current workflow tree and all un-saved changed will be lost."
            ),
        ).exec_()
        if _reply:
            PLUGINS.clear_collection(True)
            PLUGINS.find_and_register_plugins(*PLUGINS.get_q_settings_plugin_paths())

    @QtCore.Slot(str)
    def update_cmap(self, cmap_name: str):
        """
        Update the default colormap.

        Parameters
        ----------
        cmap_name : str
            The name of the new colormap.
        """
        self.update_qsetting("cmap_name", cmap_name)

    @QtCore.Slot()
    def change_fontsize(self, change: int):
        """
        Process the button clicks to change the fontsize.

        Parameters
        ----------
        change : Literal["increase", "decrease"]
            The change direction.
        """
        if change == 1:
            _new_fontsize = min(ceil(self.__qtapp.font_size) + 1, 20)
        elif change == -1:
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
    def frame_activated(self, index: int):
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
            _value = self.q_settings_get(f"user/{_param_key}", _param.dtype)
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
                self.q_settings_set(f"user/{_param_key}", _value)
            self.process_new_fontsize_setting()
            self._update_cmap_nan_current_color(
                self.q_settings_get("user/cmap_nan_color")
            )

    @QtCore.Slot(str, object)
    def external_update(self, param_key: str, value: object):
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
        _ = PydidasExceptionMessageBox(text=error, title="Warning").exec_()


UserConfigWindow = SingletonFactory(_UserConfigWindow)
