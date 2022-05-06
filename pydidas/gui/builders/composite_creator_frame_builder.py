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
Module with the CompositeCreatorFrameBuilder class which is used to
populate the CompositeCreatorFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["CompositeCreatorFrameBuilder"]

from qtpy import QtWidgets, QtCore
from silx.gui.plot import PlotWindow

from ...core.constants import (
    CONFIG_WIDGET_WIDTH,
    FIX_EXP_POLICY,
    EXP_EXP_POLICY,
)
from ...widgets import ScrollArea, BaseFrameWithApp
from ...widgets.parameter_config import ParameterEditFrame
from ..mixins import SilxPlotWindowMixIn


class CompositeCreatorFrameBuilder(BaseFrameWithApp, SilxPlotWindowMixIn):
    """
    Create the layout and add all widgets required for the
    CompositeCreatorFrame.
    """

    def __init__(self, parent=None):
        BaseFrameWithApp.__init__(self, parent)
        SilxPlotWindowMixIn.__init__(self)

    def build_frame(self):
        """
        Create all widgets for the CompositeCreatorFrame and initialize their
        state.
        """
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._widgets["config"] = ParameterEditFrame(
            self, lineWidth=5, sizePolicy=FIX_EXP_POLICY
        )

        self.create_label(
            "title",
            "Composite image creator",
            fontsize=14,
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
        )
        self.add_any_widget(
            "plot_window",
            PlotWindow(
                parent=self,
                resetzoom=True,
                autoScale=False,
                logScale=False,
                grid=False,
                curveStyle=False,
                colormap=True,
                aspectRatio=True,
                yInverted=True,
                copy=True,
                save=True,
                print_=True,
                control=False,
                position=True,
                roi=False,
                mask=True,
            ),
            alignment=None,
            stretch=(1, 1),
            gridPos=(0, 3, 1, 1),
            visible=False,
            sizePolicy=EXP_EXP_POLICY,
        )

        for _key in self.params:
            _options = self.__get_param_widget_config(_key)
            self.create_param_widget(self.params[_key], **_options)

            # add spacers between groups:
            if _key in [
                "n_files",
                "images_per_file",
                "bg_hdf5_frame",
                "use_global_det_mask",
                "roi_yhigh",
                "threshold_high",
                "binning",
                "output_fname",
                "n_total",
                "composite_dir",
            ]:
                self.create_line(
                    f"line_{_key}",
                    parent_widget=self._widgets["config"],
                    fixedWidth=CONFIG_WIDGET_WIDTH,
                )
        self.create_button(
            "but_exec",
            "Generate composite",
            gridPos=(-1, 0, 1, 2),
            parent_widget=self._widgets["config"],
            enabled=False,
            fixedWidth=CONFIG_WIDGET_WIDTH,
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
        )

        self.create_button(
            "but_show",
            "Show composite",
            gridPos=(-1, 0, 1, 2),
            parent_widget=self._widgets["config"],
            enabled=False,
            fixedWidth=CONFIG_WIDGET_WIDTH,
        )

        self.create_button(
            "but_save",
            "Save composite image",
            parent_widget=self._widgets["config"],
            gridPos=(-1, 0, 1, 2),
            enabled=False,
            fixedWidth=CONFIG_WIDGET_WIDTH,
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
        _config_next_row = self._widgets["config"].next_row
        # special formatting for some parameters:
        if param_key in [
            "first_file",
            "last_file",
            "hdf5_key",
            "bg_file",
            "bg_hdf5_key",
            "output_fname",
        ]:
            _config = dict(
                linebreak=True,
                halign_text=QtCore.Qt.AlignLeft,
                valign_text=QtCore.Qt.AlignBottom,
                width_total=CONFIG_WIDGET_WIDTH,
                width_io=CONFIG_WIDGET_WIDTH - 50,
                width_text=CONFIG_WIDGET_WIDTH - 20,
                width_unit=0,
                parent_widget=self._widgets["config"],
                row=_config_next_row(),
            )
        else:
            _config = dict(
                width_io=100,
                width_unit=0,
                parent_widget=self._widgets["config"],
                width_text=CONFIG_WIDGET_WIDTH - 100,
                width_total=CONFIG_WIDGET_WIDTH,
            )
        return _config
