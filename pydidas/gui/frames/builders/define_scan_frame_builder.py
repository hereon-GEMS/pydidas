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
Module with the DefineScanFrameBuilder class which is used to populate
the DefineScanFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["DefineScanFrameBuilder"]

from ....core import constants, utils
from ....contexts import ScanContext
from ....widgets import BaseFrame
from ....widgets.utilities import get_pyqt_icon_from_str


SCAN_SETTINGS = ScanContext()


class DefineScanFrameBuilder(BaseFrame):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    self : pydidas.gui.DefineScanFrame
        The DefineScanFrame instance.
    """

    TEXT_WIDTH = 200
    PARAM_INPUT_WIDTH = 90

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)

    def build_frame(self):
        """
        Create all widgets for the frame and place them in the layout.
        """
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
            fixedWidth=constants.CONFIG_WIDGET_WIDTH,
        )
        # self.create_button(
        #     "but_import",
        #     "Open scan parameter import dialogue",
        #     gridPos=(-1, 0, 1, 1),
        #     alignment=None,
        #     icon=self.style().standardIcon(42),
        #     fixedWidth=constants.CONFIG_WIDGET_WIDTH,
        # )
        self.create_button(
            "but_reset",
            "Reset all scan settings",
            icon=self.style().standardIcon(59),
            fixedWidth=constants.CONFIG_WIDGET_WIDTH,
        )

        _param_edit_row = self.next_row()
        self.create_empty_widget(
            "global_param_frame",
            gridPos=(_param_edit_row, 0, 1, 1),
            fixedWidth=constants.CONFIG_WIDGET_WIDTH,
            layout_kwargs=dict(
                contentsMargins=(0, 0, 0, 0),
            ),
            sizePolicy=constants.EXP_FIX_POLICY,
            alignment=constants.QT_DEFAULT_ALIGNMENT,
        )

        self.create_empty_widget(
            "scan_param_frame",
            gridPos=(_param_edit_row, 1, 1, 1),
            layout_kwargs=dict(horizontalSpacing=5, contentsMargins=(0, 0, 0, 0)),
            alignment=constants.QT_DEFAULT_ALIGNMENT,
        )
        self.create_spacer(
            "right_spacer",
            gridPos=(_param_edit_row, 2, 1, 1),
            stretch=1,
            sizePolicy=constants.EXP_EXP_POLICY,
        )

        # populate global_param_frame
        self.create_label(
            "scan_global",
            "\nGlobal scan parameters:",
            fontsize=constants.STANDARD_FONT_SIZE + 1,
            bold=True,
            parent_widget=self._widgets["global_param_frame"],
        )

        self.create_param_widget(
            SCAN_SETTINGS.get_param("scan_dim"),
            parent_widget=self._widgets["global_param_frame"],
            **constants.DEFAULT_TWO_LINE_PARAM_CONFIG.copy(),
        )
        for _name in ["scan_title", "scan_base_directory", "scan_name_pattern"]:
            self.create_param_widget(
                SCAN_SETTINGS.get_param(_name),
                parent_widget=self._widgets["global_param_frame"],
                **constants.DEFAULT_TWO_LINE_PARAM_CONFIG.copy(),
            )

        for _name in ["scan_base_directory", "scan_name_pattern"]:
            self.param_widgets[_name].set_unique_ref_name(f"DefineScanFrame__{_name}")

        for _name in [
            "scan_start_index",
            "scan_index_stepping",
            "scan_multiplicity",
            "scan_multi_image_handling",
        ]:
            self.create_param_widget(
                SCAN_SETTINGS.get_param(_name),
                width_total=constants.CONFIG_WIDGET_WIDTH,
                width_text=self.TEXT_WIDTH,
                width_io=self.PARAM_INPUT_WIDTH,
                width_unit=0,
                parent_widget=self._widgets["global_param_frame"],
            )

        # populate scan_param_frame widget
        _param_names = ["label", "n_points", "delta", "unit", "offset"]
        for i_dim in range(4):
            self.create_label(
                f"title_{i_dim}",
                f"\nScan dimension {i_dim}:",
                fontsize=constants.STANDARD_FONT_SIZE + 1,
                bold=True,
                fixedWidth=constants.CONFIG_WIDGET_WIDTH - 50,
                alignment=constants.QT_BOTTOM_LEFT_ALIGNMENT,
                gridPos=(6 * (i_dim % 2), 4 * (i_dim // 2), 1, 1),
                parent_widget=self._widgets["scan_param_frame"],
            )
            self.create_button(
                f"button_up_{i_dim}",
                "",
                icon=get_pyqt_icon_from_str("qta::fa.chevron-up"),
                fixedWidth=20,
                fixedHeight=20,
                alignment=constants.QT_BOTTOM_RIGHT_ALIGNMENT,
                gridPos=(6 * (i_dim % 2), 4 * (i_dim // 2) + 1, 1, 1),
                parent_widget=self._widgets["scan_param_frame"],
            )
            self.create_button(
                f"button_down_{i_dim}",
                "",
                icon=get_pyqt_icon_from_str("qta::fa.chevron-down"),
                fixedWidth=20,
                fixedHeight=20,
                alignment=constants.QT_BOTTOM_RIGHT_ALIGNMENT,
                gridPos=(6 * (i_dim % 2), 4 * (i_dim // 2) + 2, 1, 1),
                parent_widget=self._widgets["scan_param_frame"],
            )
            for i_item, basename in enumerate(_param_names):
                param = SCAN_SETTINGS.get_param(f"scan_dim{i_dim}_{basename}")
                self.create_param_widget(
                    param,
                    gridPos=(1 + i_item + 6 * (i_dim % 2), 4 * (i_dim // 2), 1, 3),
                    width_text=self.TEXT_WIDTH + 5,
                    width_unit=0,
                    width_io=self.PARAM_INPUT_WIDTH,
                    width_total=constants.CONFIG_WIDGET_WIDTH,
                    parent_widget=self._widgets["scan_param_frame"],
                )
            self.create_spacer(
                "scan_dim_spacer",
                gridPos=(0, 3, 12, 1),
                fixedWidth=20,
                parent_widget=self._widgets["scan_param_frame"],
            )

        self.create_button(
            "but_save",
            "Export scan settings",
            gridPos=(-1, 0, 1, 1),
            fixedWidth=constants.CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["global_param_frame"],
            icon=self.style().standardIcon(43),
        )
        self.create_spacer(
            "final_spacer", gridPos=(-1, 0, 1, 1), sizePolicy=constants.EXP_EXP_POLICY
        )
