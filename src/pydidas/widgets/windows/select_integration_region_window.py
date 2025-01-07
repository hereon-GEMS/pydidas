# This file is part of pydidas
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with the SelectIntegrationRegionWindow class which allows to select an
integration region for a plugin.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SelectIntegrationRegionWindow"]

from pathlib import Path

import numpy as np
from qtpy import QtCore, QtWidgets

from pydidas.core import Dataset, UserConfigError, get_generic_param_collection
from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH
from pydidas.core.utils import apply_qt_properties
from pydidas.data_io import import_data
from pydidas.widgets.controllers import ManuallySetIntegrationRoiController
from pydidas.widgets.dialogues import QuestionBox
from pydidas.widgets.framework import PydidasWindow
from pydidas.widgets.misc import SelectImageFrameWidget, ShowIntegrationRoiParamsWidget
from pydidas.widgets.scroll_area import ScrollArea
from pydidas.widgets.silx_plot import PydidasPlot2DwithIntegrationRegions


class SelectIntegrationRegionWindow(PydidasWindow):
    """
    A pydidas window which allows to open a file
    """

    default_params = get_generic_param_collection(
        "filename", "hdf5_key", "hdf5_frame", "hdf5_slicing_axis", "overlay_color"
    )
    sig_roi_changed = QtCore.Signal()
    sig_about_to_close = QtCore.Signal()

    def __init__(self, plugin, **kwargs):
        PydidasWindow.__init__(
            self, title="Select integration region", activate_frame=False
        )
        apply_qt_properties(self.layout(), contentsMargins=(10, 10, 10, 10))

        self._plugin = plugin
        self._EXP = plugin._EXP
        self._original_plugin_param_values = plugin.get_param_values_as_dict()
        self.add_params(plugin.params)
        self._config = self._config | {
            "azimuthal_active": False,
            "beamcenter": self._EXP.beamcenter,
            "closing_confirmed": False,
            "det_dist": self._EXP.get_param_value("detector_dist"),
            "only_show_roi": kwargs.get("only_show_roi", False),
            "radial_active": False,
            "rad_unit": self._plugin.get_param_value("rad_unit"),
        }
        self._image = None
        self.frame_activated(self.frame_index)

    def build_frame(self):
        """
        Build the frame and create widgets.
        """
        self.create_label(
            "label_title",
            (
                "Display integration region"
                if self._config["only_show_roi"]
                else "Select integration region"
            ),
            bold=True,
            fontsize_offset=1,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        self.create_empty_widget(
            "left_container",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            minimumHeight=400,
            parent_widget=None,
        )
        self.create_any_widget(
            "scroll_area",
            ScrollArea,
            gridPos=(1, 0, 1, 1),
            resize_to_widget_width=True,
            widget=self._widgets["left_container"],
        )
        self.create_spacer(None, fixedWidth=25, gridPos=(1, 1, 1, 1))
        self.add_any_widget(
            "plot",
            PydidasPlot2DwithIntegrationRegions(cs_transform=True),
            gridPos=(1, 2, 1, 1),
            minimumWidth=700,
            minimumHeight=700,
        )
        self.create_spacer(None, parent_widget=self._widgets["left_container"])
        self.create_label(
            "label_note",
            (
                "Note: The math for calculating the angles is only defined for "
                "detectors with square pixels."
            ),
            bold=True,
            font_metric_height_factor=2,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget=self._widgets["left_container"],
            wordWrap=True,
        )
        self.create_line(None, parent_widget=self._widgets["left_container"])
        self.create_label(
            "label_file",
            "Select input file:",
            fontsize_offset=1,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget=self._widgets["left_container"],
            underline=True,
        )
        self.add_any_widget(
            "file_selector",
            SelectImageFrameWidget(
                *self.params.values(),
                import_reference="SelectIntegrationRegion__import",
            ),
            parent_widget=self._widgets["left_container"],
        )

        self.create_line(None, parent_widget=self._widgets["left_container"])

        self.add_any_widget(
            "roi_selector",
            ShowIntegrationRoiParamsWidget(
                forced_edit_disable=self._config["only_show_roi"],
                plugin=self._plugin,
            ),
            parent_widget=self._widgets["left_container"],
        )
        self.create_button(
            "but_confirm",
            "Confirm integration region",
            parent_widget=self._widgets["left_container"],
        )
        self.create_spacer(None, parent_widget=self._widgets["left_container"])

    def connect_signals(self):
        """
        Connect all signals.
        """
        self._roi_controller = ManuallySetIntegrationRoiController(
            self._widgets["roi_selector"], self._widgets["plot"], plugin=self._plugin
        )
        self._widgets["file_selector"].sig_new_file_selection.connect(self.open_image)
        self._widgets["file_selector"].sig_file_valid.connect(self._toggle_fname_valid)
        self._widgets["but_confirm"].clicked.connect(self._confirm_changes)

    def finalize_ui(self):
        """
        Finalize the UI and update the input widgets.
        """
        _nx = self._EXP.get_param_value("detector_npixx")
        _ny = self._EXP.get_param_value("detector_npixy")
        if _nx == 0 or _ny == 0:
            raise UserConfigError(
                "No detector has been defined in the DiffractionExperiment setup. "
                "Cannot display and edit the integration region."
            )
        self._image = Dataset(np.zeros((_ny, _ny)))
        self._widgets["plot"].plot_pydidas_dataset(self._image, title="")
        self._widgets["plot"].changeCanvasToDataAction._actionTriggered()
        self._roi_controller.show_plot_items("roi")
        if self._config["only_show_roi"]:
            self._config["closing_confirmed"] = True
        self._roi_controller.update_input_widgets()

    @QtCore.Slot(bool)
    def _toggle_fname_valid(self, is_valid):
        """
        Modify widgets visibility and activation based on the file selection.

        Parameters
        ----------
        is_valid : bool
            Flag to process.
        """
        self._widgets["plot"].setEnabled(is_valid)

    @QtCore.Slot(str, object)
    def open_image(self, filename, kwargs):
        """
        Open an image with the given filename and display it in the plot.

        Parameters
        ----------
        filename : Union[str, Path]
            The filename and path.
        kwargs : dict
            Additional parameters to open a specific frame in a file.
        """
        self._image = import_data(filename, **kwargs)
        _path = Path(filename)
        self._widgets["plot"].plot_pydidas_dataset(self._image, title=_path.name)
        self._widgets["plot"].changeCanvasToDataAction._actionTriggered()
        self._roi_controller.reset_selection_mode()
        self._roi_controller.update_input_widgets()
        self._roi_controller.show_plot_items("roi")

    @QtCore.Slot()
    def _confirm_changes(self):
        """
        Confirm all changes made to the plugin and close the window.
        """
        self._config["closing_confirmed"] = True
        self.sig_roi_changed.emit()
        self.close()

    def closeEvent(self, event: QtCore.QEvent):
        """
        Handle the Qt close event and add a question if closing without saving results.

        Parameters
        ----------
        event : QtCore.QEvent
            The closing event.
        """
        if self._config["closing_confirmed"]:
            self.sig_about_to_close.emit()
            event.accept()
            return
        _reply = QuestionBox(
            "Exit confirmation",
            "Do you want to close the Select integration region "
            "window and discard all changes? To accept the changes, please use the "
            "'Confirm integration region' button.",
        ).exec_()
        if not _reply:
            event.ignore()
            return
        self._roi_controller.reset_plugin()
        self.sig_about_to_close.emit()
        event.accept()

    def show(self):
        """
        Overload the generic show to also update the input widgets.
        """
        for _key in self.param_widgets:
            self.update_widget_value(_key, self.get_param_value(_key))
        self._roi_controller.update_input_widgets()
        self._roi_controller.show_plot_items("roi")
        QtWidgets.QWidget.show(self)
