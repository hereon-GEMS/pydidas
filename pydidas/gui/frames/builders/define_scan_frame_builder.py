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
Module with the DefineScanFrameBuilder class which is used to populate
the DefineScanFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DefineScanFrameBuilder"]


from ....contexts import ScanContext
from ....core import constants, utils
from ....widgets import ScrollArea
from ....widgets.factory import SquareButton
from ....widgets.framework import BaseFrame
from ....widgets.utilities import get_pyqt_icon_from_str


SCAN_SETTINGS = ScanContext()

SCAN_DIMENSION_EXPLANATION_TEXT = (
    "The scan dimensions must be assigned based on the data acquisition scheme to "
    "match the incrementing image numbers.<br><b>The lowest numbered scan dimension is "
    "the slowest scan dimension and the highest numbered scan dimension is the fastest."
    "</b>"
)


class DefineScanFrameBuilder:
    """
    Create all widgets and initialize their state.
    """

    @classmethod
    def build_frame(cls, frame: BaseFrame):
        """
        Create all widgets for the frame and place them in the layout.

        Parameters
        ----------
        frame : BaseFrame
            The DefineScanFrame instance.
        """
        utils.apply_qt_properties(
            frame.layout(),
            horizontalSpacing=25,
            alignment=constants.ALIGN_TOP_LEFT,
        )
        frame.create_empty_widget(
            "master",
            font_metric_width_factor=69,
            layout_kwargs={"horizontalSpacing": 0},
        )
        frame.create_any_widget(
            "config_area",
            ScrollArea,
            layout_kwargs={"alignment": None},
            widget=frame._widgets["master"],
        )
        frame.create_label(
            "label_title",
            "Scan settings\n",
            fontsize_offset=4,
            bold=True,
            parent_widget="master",
        )
        frame.create_empty_widget(
            "config_header", font_metric_width_factor=25, parent_widget="master"
        )
        frame.create_button(
            "but_load",
            "Import scan settings from file",
            icon="qt-std::SP_DialogOpenButton",
            parent_widget="config_header",
        )
        frame.create_button(
            "but_reset",
            "Reset all scan settings",
            icon="qt-std::SP_BrowserReload",
            parent_widget="config_header",
        )
        frame.create_spacer(
            None,
            fixedHeight=15,
            parent_widget="config_header",
        )
        frame.create_label(
            "dimension_hint_title",
            "Scan dimension explanation",
            bold=True,
            fontsize_offset=1,
            parent_widget="config_header",
        )
        frame.create_label(
            "dimension_hint_text",
            SCAN_DIMENSION_EXPLANATION_TEXT,
            font_metric_height_factor=4,
            font_metric_width_factor=25,
            parent_widget="config_header",
            wordWrap=True,
        )
        frame.create_button(
            "but_more_scan_dim_info",
            "More information about scan dimensions",
            icon="qt-std::SP_MessageBoxInformation",
            parent_widget="config_header",
        )
        frame.create_spacer(None, parent_widget="master")

        _row = frame._widgets["master"].layout().rowCount()
        frame.create_empty_widget(
            "config_global",
            font_metric_width_factor=25,
            gridPos=(_row, 0, 1, 1),
            parent_widget="master",
        )
        frame.create_empty_widget(
            "horizontal_spacer_A",
            font_metric_width_factor=2,
            gridPos=(_row, -1, 1, 1),
            parent_widget="master",
        )
        frame.create_empty_widget(
            "config_A",
            font_metric_width_factor=20,
            gridPos=(_row, -1, 1, 1),
            parent_widget="master",
        )
        frame.create_empty_widget(
            "horizontal_spacer_B",
            font_metric_width_factor=2,
            gridPos=(_row, -1, 1, 1),
            parent_widget="master",
        )
        frame.create_empty_widget(
            "config_B",
            font_metric_width_factor=20,
            gridPos=(_row, -1, 1, 1),
            parent_widget="master",
        )

        frame.create_label(
            "scan_global",
            "\nGlobal scan parameters:",
            bold=True,
            fontsize_offset=1,
            parent_widget="config_global",
        )
        frame.create_param_widget(
            SCAN_SETTINGS.get_param("scan_dim"),
            linebreak=True,
            parent_widget="config_global",
        )
        for _name in ["scan_title", "scan_base_directory", "scan_name_pattern"]:
            frame.create_param_widget(
                SCAN_SETTINGS.get_param(_name),
                linebreak=True,
                parent_widget="config_global",
            )

        for _name in ["scan_base_directory", "scan_name_pattern"]:
            frame.param_widgets[_name].set_unique_ref_name(f"DefineScanFrame__{_name}")

        for _name in [
            "scan_start_index",
            "scan_index_stepping",
            "scan_multiplicity",
            "scan_multi_image_handling",
        ]:
            frame.create_param_widget(
                SCAN_SETTINGS.get_param(_name),
                parent_widget="config_global",
            )

        # populate scan_param_frame widget
        _param_names = ["label", "n_points", "delta", "unit", "offset"]
        for i_dim in range(4):
            _parent = "config_A" if i_dim in [0, 1] else "config_B"
            _row = frame._widgets[_parent].layout().rowCount()
            frame.create_label(
                f"title_{i_dim}",
                f"\nScan dimension {i_dim}:",
                alignment=constants.ALIGN_BOTTOM_LEFT,
                bold=True,
                fontsize_offset=1,
                font_metric_width_factor=15,
                gridPos=(_row, 0, 1, 1),
                parent_widget=_parent,
            )
            frame.create_any_widget(
                f"button_up_{i_dim}",
                SquareButton,
                alignment=constants.ALIGN_BOTTOM_RIGHT,
                gridPos=(_row, 2, 1, 1),
                icon=get_pyqt_icon_from_str("qta::fa.chevron-up"),
                parent_widget=_parent,
            )
            frame.create_any_widget(
                f"button_down_{i_dim}",
                SquareButton,
                alignment=constants.ALIGN_BOTTOM_RIGHT,
                gridPos=(_row, 3, 1, 1),
                icon=get_pyqt_icon_from_str("qta::fa.chevron-down"),
                parent_widget=_parent,
            )
            for basename in _param_names:
                param = SCAN_SETTINGS.get_param(f"scan_dim{i_dim}_{basename}")
                frame.create_param_widget(
                    param,
                    font_metric_width_factor=20,
                    gridPos=(-1, 0, 1, 4),
                    parent_widget=_parent,
                    width_text=0.6,
                    width_io=0.3,
                )
            frame.create_spacer("scan_dim_spacer", parent_widget=_parent)

        frame.create_button(
            "but_save",
            "Export scan settings",
            font_metric_width_factor=25,
            gridPos=(-1, 0, 1, 1),
            icon="qt-std::SP_DialogSaveButton",
            parent_widget="master",
        )
        frame.create_spacer(
            "final_spacer", gridPos=(-1, 0, 1, 1), sizePolicy=constants.POLICY_EXP_EXP
        )
