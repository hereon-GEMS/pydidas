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
Module with the SetupScanFrameBuilder class which is used to populate
the SetupScanFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SetupScanFrameBuilder"]

from ....core import constants, utils
from ....experiment import SetupScan
from ....widgets import BaseFrame, ScrollArea, utilities, parameter_config


SCAN_SETTINGS = SetupScan()


class SetupScanFrameBuilder(BaseFrame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    self : pydidas.gui.SetupScanFrame
        The SetupScanFrame instance.
    """

    TEXT_WIDTH = 200
    PARAM_INPUT_WIDTH = 120

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)

    def build_frame(self):
        """
        Create all widgets for the frame and place them in the layout.
        """
        _width_total = self.TEXT_WIDTH + self.PARAM_INPUT_WIDTH + 10
        utils.apply_qt_properties(
            self.layout(),
            horizontalSpacing=25,
            alignment=constants.QT_DEFAULT_ALIGNMENT,
        )
        self.create_label(
            "label_title",
            "Scan settings\n",
            fontsize=constants.STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self.create_button(
            "but_load",
            "Import scan settings from file",
            icon=self.style().standardIcon(42),
            fixedWidth=_width_total,
        )
        # self.create_button(
        #     "but_import",
        #     "Open scan parameter import dialogue",
        #     gridPos=(-1, 0, 1, 1),
        #     alignment=None,
        #     icon=self.style().standardIcon(42),
        #     fixedWidth=_width_total,
        # )
        self.create_button(
            "but_reset",
            "Reset all scan settings",
            icon=self.style().standardIcon(59),
            fixedWidth=_width_total,
        )

        _param_edit_row = self.next_row()
        self.create_empty_widget(
            "scan_param_frame",
            gridPos=(_param_edit_row, 0, 1, 1),
            layout_kwargs=dict(horizontalSpacing=25),
            alignment=constants.QT_DEFAULT_ALIGNMENT,
        )
        self.create_empty_widget(
            "input_plugin_param_frame",
            gridPos=(_param_edit_row, 1, 1, 1),
            fixedWidth=constants.PLUGIN_PARAM_WIDGET_WIDTH + 25,
            layout_kwargs=dict(
                contentsMargins=(0, 0, 0, 0),
            ),
            sizePolicy=constants.EXP_FIX_POLICY,
            alignment=constants.QT_DEFAULT_ALIGNMENT,
        )
        self.create_spacer(
            "right_spacer",
            gridPos=(_param_edit_row, 2, 1, 1),
            stretch=1,
            sizePolicy=constants.EXP_EXP_POLICY,
        )

        self.create_label(
            "scan_global",
            "\nGlobal scan parameters:",
            fontsize=constants.STANDARD_FONT_SIZE + 1,
            bold=True,
            parent_widget=self._widgets["scan_param_frame"],
        )

        self.create_param_widget(
            SCAN_SETTINGS.get_param("scan_dim"),
            width_text=self.TEXT_WIDTH,
            width_io=self.PARAM_INPUT_WIDTH,
            width_total=_width_total,
            width_unit=0,
            parent_widget=self._widgets["scan_param_frame"],
        )
        self.create_param_widget(
            SCAN_SETTINGS.get_param("scan_title"),
            width_text=self.TEXT_WIDTH,
            width_io=_width_total - 20,
            linebreak=True,
            width_total=_width_total,
            width_unit=0,
            parent_widget=self._widgets["scan_param_frame"],
        )
        # populate scan_param_frame widget
        _prefixes = ["scan_label_", "n_points_", "delta_", "unit_", "offset_"]
        for i_dim in range(4):
            self.create_label(
                f"title_{i_dim + 1}",
                f"\nScan dimension {i_dim+1}:",
                fontsize=constants.STANDARD_FONT_SIZE + 1,
                bold=True,
                fixedWidth=_width_total,
                gridPos=(3 + 6 * (i_dim % 2), i_dim // 2, 1, 1),
                parent_widget=self._widgets["scan_param_frame"],
            )
            for i_item, basename in enumerate(_prefixes):
                param = SCAN_SETTINGS.get_param(f"{basename}{i_dim+1}")
                self.create_param_widget(
                    param,
                    gridPos=(4 + i_item + 6 * (i_dim % 2), i_dim // 2, 1, 1),
                    width_text=self.TEXT_WIDTH + 5,
                    width_unit=0,
                    width_io=self.PARAM_INPUT_WIDTH,
                    width_total=_width_total,
                    parent_widget=self._widgets["scan_param_frame"],
                )

        self.create_button(
            "but_save",
            "Export scan settings",
            gridPos=(-1, 0, 1, 1),
            fixedWidth=_width_total,
            parent_widget=self._widgets["scan_param_frame"],
            icon=self.style().standardIcon(43),
        )
        self.create_spacer(
            "final_spacer", gridPos=(-1, 0, 1, 1), sizePolicy=constants.EXP_EXP_POLICY
        )

        self.create_label(
            "label_input_plugin",
            "Select input plugin:",
            fontsize=constants.STANDARD_FONT_SIZE + 1,
            bold=True,
            parent_widget=self._widgets["input_plugin_param_frame"],
        )
        self.create_combo_box(
            "input_plugin",
            fixedWidth=constants.PLUGIN_PARAM_WIDGET_WIDTH,
            parent_widget=self._widgets["input_plugin_param_frame"],
        )
        self.create_button(
            "button_open_plugin_info",
            "Show InputPlugin details",
            icon=utilities.get_pyqt_icon_from_str_reference("qt-std::9"),
            fixedWidth=int(2 / 3 * constants.PLUGIN_PARAM_WIDGET_WIDTH),
            alignment=constants.QT_TOP_RIGHT_ALIGNMENT,
            parent_widget=self._widgets["input_plugin_param_frame"],
        )
        self.create_spacer("final_spacer", gridPos=(2, 1, 1, 1), fixedWidth=25)
        self._widgets["plugin_edit"] = parameter_config.ConfigurePluginWidget()
        self.create_any_widget(
            "plugin_edit_area",
            ScrollArea,
            widget=self._widgets["plugin_edit"],
            fixedWidth=constants.PLUGIN_PARAM_WIDGET_WIDTH + 25,
            sizePolicy=constants.FIX_EXP_POLICY,
            parent_widget=self._widgets["input_plugin_param_frame"],
            gridPos=(-1, 0, 1, 2),
        )
