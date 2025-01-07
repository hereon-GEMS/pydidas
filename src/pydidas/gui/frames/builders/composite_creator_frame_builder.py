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
Module with the CompositeCreatorFrameBuilder class which is used to
populate the CompositeCreatorFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["CompositeCreatorFrameBuilder"]


from qtpy import QtWidgets

from pydidas.core.constants import (
    FONT_METRIC_PARAM_EDIT_WIDTH,
    POLICY_EXP_EXP,
    POLICY_FIX_EXP,
)
from pydidas.widgets import ScrollArea, silx_plot
from pydidas.widgets.framework import BaseFrame


_KEYS_TO_INSERT_LINES = [
    "n_files",
    "images_per_file",
    "bg_hdf5_frame",
    "detector_mask_val",
    "roi_yhigh",
    "threshold_high",
    "binning",
    "output_fname",
    "n_total",
    "composite_ydir_orientation",
]


class CompositeCreatorFrameBuilder:
    """
    Create the layout and add all widgets required for the CompositeCreatorFrame.
    """

    @classmethod
    def build_frame(cls, frame: BaseFrame):
        """
        Create and initialize all widgets for the CompositeCreatorFrame.

        Parameters
        ----------
        frame : BaseFrame
            The BaseFrame instance in which the widgets shall be added.
        """
        frame.layout().setContentsMargins(10, 0, 0, 0)
        frame.setMinimumHeight(800)
        frame.create_empty_widget(
            "config_canvas",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        frame.create_any_widget(
            "config_area",
            ScrollArea,
            layout_kwargs={"alignment": None},
            stretch=(1, 0),
            sizePolicy=POLICY_FIX_EXP,
            widget=frame._widgets["config_canvas"],
        )
        frame.create_label(
            "title",
            "Composite image creator",
            bold=True,
            fontsize_offset=4,
            parent_widget="config_canvas",
        )
        frame.create_spacer(
            "spacer1",
            parent_widget="config_canvas",
        )
        frame.create_button(
            "but_clear",
            "Clear all entries",
            icon="qt-std::SP_BrowserReload",
            parent_widget="config_canvas",
        )
        frame.create_any_widget(
            "plot_window",
            silx_plot.PydidasPlot2D,
            alignment=None,
            cs_transform=False,
            gridPos=(0, 1, 1, 1),
            minimumWidth=900,
            visible=False,
            stretch=(1, 1),
            sizePolicy=POLICY_EXP_EXP,
        )

        for _key in frame.params:
            _options = cls.__get_param_widget_config(_key)
            frame.create_param_widget(frame.params[_key], **_options)
            # add spacers between groups:
            if _key in _KEYS_TO_INSERT_LINES:
                frame.create_line(f"line_{_key}", parent_widget="config_canvas")
            if _key in ["first_file", "last_file", "bg_file"]:
                frame.param_widgets[_key].set_unique_ref_name(
                    f"CompositeCreatorFrame__{_key}"
                )

        frame.create_button(
            "but_exec",
            "Generate composite",
            enabled=False,
            icon="qt-std::SP_MediaPlay",
            parent_widget="config_canvas",
        )
        frame.create_progress_bar(
            "progress",
            maximum=100,
            minimum=0,
            parent_widget="config_canvas",
            visible=False,
        )
        frame.create_button(
            "but_abort",
            "Abort composite creation",
            enabled=True,
            icon="qt-std::SP_BrowserStop",
            parent_widget="config_canvas",
            visible=False,
        )
        frame.create_button(
            "but_show",
            "Show composite",
            enabled=False,
            icon="qt-std::SP_DesktopIcon",
            parent_widget="config_canvas",
        )
        frame.create_button(
            "but_save",
            "Export composite image to file",
            enabled=False,
            icon="qt-std::SP_DialogSaveButton",
            parent_widget="config_canvas",
        )
        frame.create_spacer(
            "spacer_bottom",
            height=300,
            parent_widget="config_canvas",
            policy=QtWidgets.QSizePolicy.Expanding,
        )
        for _key in [
            "n_total",
            "hdf5_dataset_shape",
            "n_files",
            "raw_image_shape",
            "images_per_file",
        ]:
            frame.param_widgets[_key].setEnabled(False)
        for _key in [
            "hdf5_key",
            "hdf5_slicing_axis",
            "hdf5_first_image_num",
            "hdf5_last_image_num",
            "last_file",
            "hdf5_stepping",
            "hdf5_dataset_shape",
            "hdf5_stepping",
        ]:
            frame.toggle_param_widget_visibility(_key, False)

        frame.toggle_param_widget_visibility("hdf5_dataset_shape", False)
        frame.toggle_param_widget_visibility("raw_image_shape", False)

    @classmethod
    def __get_param_widget_config(cls, param_key):
        """
        Get Formatting options for create_param_widget instances.

        Parameters
        ----------
        param_key : str
            The reference key for Parameter.

        Returns
        -------
        dict
            The keyword dictionary to be passed to the ParamWidget creation.
        """
        return {
            "linebreak": param_key
            in [
                "first_file",
                "last_file",
                "hdf5_key",
                "bg_file",
                "bg_hdf5_key",
                "output_fname",
                "detector_mask_file",
                "composite_image_op",
            ],
            "enabled": param_key
            not in [
                "n_total",
                "hdf5_dataset_shape",
                "n_files",
                "raw_image_shape",
                "images_per_file",
            ],
            "parent_widget": "config_canvas",
        }
