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
Module with the CompositeCreatorFrameBuilder class which is used to
populate the CompositeCreatorFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["CompositeCreatorFrameBuilder"]

from qtpy import QtWidgets

from ....core import constants
from ....core.constants import CONFIG_WIDGET_WIDTH, EXP_EXP_POLICY, FIX_EXP_POLICY
from ....widgets import ScrollArea, silx_plot
from ....widgets.framework import BaseFrameWithApp
from ....widgets.parameter_config import ParameterEditCanvas
from ...mixins import SilxPlotWindowMixIn


class CompositeCreatorFrameBuilder(BaseFrameWithApp, SilxPlotWindowMixIn):
    """
    Create the layout and add all widgets required for the
    CompositeCreatorFrame.
    """

    def __init__(self, parent=None, **kwargs):
        BaseFrameWithApp.__init__(self, parent, **kwargs)
        SilxPlotWindowMixIn.__init__(self)

    def build_frame(self):
        """
        Create all widgets for the CompositeCreatorFrame and initialize their
        state.
        """
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._widgets["config"] = ParameterEditCanvas(
            self, lineWidth=5, sizePolicy=FIX_EXP_POLICY
        )

        self.create_label(
            "title",
            "Composite image creator",
            fontsize=constants.STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 2),
            parent_widget=self._widgets["config"],
            fixedWidth=CONFIG_WIDGET_WIDTH,
        )
        self.create_spacer(
            "spacer1",
            gridPos=(-1, 0, 1, 2),
            parent_widget=self._widgets["config"],
        )
        self.create_any_widget(
            "config_area",
            ScrollArea,
            widget=self._widgets["config"],
            fixedWidth=CONFIG_WIDGET_WIDTH + 40,
            stretch=(1, 0),
            sizePolicy=FIX_EXP_POLICY,
            gridPos=(-1, 0, 1, 1),
            layout_kwargs={"alignment": None},
        )
        self.create_button(
            "but_clear",
            "Clear all entries",
            gridPos=(-1, 0, 1, 2),
            parent_widget=self._widgets["config"],
            fixedWidth=CONFIG_WIDGET_WIDTH,
            icon=self.style().standardIcon(59),
        )
        self.create_any_widget(
            "plot_window",
            silx_plot.PydidasPlot2D,
            alignment=None,
            stretch=(1, 1),
            gridPos=(0, 3, 1, 1),
            visible=False,
            sizePolicy=EXP_EXP_POLICY,
            cs_transform=False,
        )

        for _key in self.params:
            _options = self.__get_param_widget_config(_key)
            self.create_param_widget(self.params[_key], **_options)

            # add spacers between groups:
            if _key in [
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
            ]:
                self.create_line(
                    f"line_{_key}",
                    parent_widget=self._widgets["config"],
                    fixedWidth=CONFIG_WIDGET_WIDTH,
                )

        for _name in [
            "first_file",
            "last_file",
            "bg_file",
        ]:
            self.param_widgets[_name].set_unique_ref_name(
                f"CompositeCreatorFrame__{_name}"
            )

        self.create_button(
            "but_exec",
            "Generate composite",
            gridPos=(-1, 0, 1, 2),
            parent_widget=self._widgets["config"],
            enabled=False,
            fixedWidth=CONFIG_WIDGET_WIDTH,
            icon=self.style().standardIcon(61),
        )

        self.create_progress_bar(
            "progress",
            parent_widget=self._widgets["config"],
            gridPos=(-1, 0, 1, 2),
            visible=False,
            fixedWidth=CONFIG_WIDGET_WIDTH,
            minimum=0,
            maximum=100,
        )

        self.create_button(
            "but_abort",
            "Abort composite creation",
            gridPos=(-1, 0, 1, 2),
            parent_widget=self._widgets["config"],
            enabled=True,
            visible=False,
            fixedWidth=CONFIG_WIDGET_WIDTH,
            icon=self.style().standardIcon(60),
        )

        self.create_button(
            "but_show",
            "Show composite",
            gridPos=(-1, 0, 1, 2),
            parent_widget=self._widgets["config"],
            enabled=False,
            fixedWidth=CONFIG_WIDGET_WIDTH,
            icon=self.style().standardIcon(13),
        )

        self.create_button(
            "but_save",
            "Export composite image to file",
            parent_widget=self._widgets["config"],
            gridPos=(-1, 0, 1, 2),
            enabled=False,
            fixedWidth=CONFIG_WIDGET_WIDTH,
            icon=self.style().standardIcon(43),
        )

        self.create_spacer(
            "spacer_bottom",
            parent_widget=self._widgets["config"],
            gridPos=(-1, 0, 1, 2),
            policy=QtWidgets.QSizePolicy.Expanding,
            height=300,
        )

        for _key in [
            "n_total",
            "hdf5_dataset_shape",
            "n_files",
            "raw_image_shape",
            "images_per_file",
        ]:
            self.param_widgets[_key].setEnabled(False)
        for _key in [
            "hdf5_key",
            "hdf5_first_image_num",
            "hdf5_last_image_num",
            "last_file",
            "hdf5_stepping",
            "hdf5_dataset_shape",
            "hdf5_stepping",
        ]:
            self.toggle_param_widget_visibility(_key, False)

        self.toggle_param_widget_visibility("hdf5_dataset_shape", False)
        self.toggle_param_widget_visibility("raw_image_shape", False)

    def __get_param_widget_config(self, param_key):
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
        # special formatting for some parameters:
        if param_key in [
            "first_file",
            "last_file",
            "hdf5_key",
            "bg_file",
            "bg_hdf5_key",
            "output_fname",
            "detector_mask_file",
        ]:
            _config = constants.DEFAULT_TWO_LINE_PARAM_CONFIG | {
                "parent_widget": self._widgets["config"]
            }
        else:
            _config = dict(
                width_io=100,
                width_unit=0,
                parent_widget=self._widgets["config"],
                width_text=CONFIG_WIDGET_WIDTH - 100,
                width_total=CONFIG_WIDGET_WIDTH,
            )
        return _config
