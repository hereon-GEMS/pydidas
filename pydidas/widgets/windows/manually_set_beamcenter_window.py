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
Module with the SelectPointsForBeamcenterWindow class which allows to select points
in an image to define the beamcenter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ManuallySetBeamcenterWindow"]


from pathlib import Path

import numpy as np
from qtpy import QtCore, QtWidgets

from ...contexts import DiffractionExperimentContext
from ...core import get_generic_param_collection, Dataset
from ...core.constants import CONFIG_WIDGET_WIDTH, STANDARD_FONT_SIZE
from ...data_io import import_data
from ..controllers import ManuallySetBeamcenterController
from ..dialogues import QuestionBox
from ..framework import PydidasWindow
from ..misc import PointPositionTableWidget, SelectImageFrameWidget
from ..silx_plot import PydidasPlot2D


class ManuallySetBeamcenterWindow(PydidasWindow):
    """
    A window which allows to open a file and select points to determine the beam center.
    """

    show_frame = False
    default_params = get_generic_param_collection(
        "filename",
        "hdf5_key",
        "hdf5_frame",
        "beamcenter_x",
        "beamcenter_y",
        "overlay_color",
    )

    sig_selected_beamcenter = QtCore.Signal(float, float)
    sig_about_to_close = QtCore.Signal()

    def __init__(self, parent=None, **kwargs):
        PydidasWindow.__init__(
            self,
            parent,
            title="Define beamcenter through selected points",
            activate_frame=False,
            **kwargs,
        )
        self._config = self._config | dict(
            select_mode_active=False,
            beamcenter_set=False,
            diffraction_exp=kwargs.get(
                "diffraction_exp", DiffractionExperimentContext()
            ),
        )
        self._markers = {}
        self._image = Dataset(np.zeros((5, 5)))
        self.frame_activated(self.frame_index)

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_label(
            "label_title",
            "Define beamcenter through selected points",
            fontsize=STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 3),
        )
        self.create_empty_widget(
            "left_container",
            fixedWidth=CONFIG_WIDGET_WIDTH,
            minimumHeight=400,
            gridPos=(1, 1, 2, 1),
        )
        self.create_spacer(None, fixedWidth=25, gridPos=(1, 1, 1, 1))
        self.add_any_widget(
            "plot",
            PydidasPlot2D(
                cs_transform=False, diffraction_exp=self._config["diffraction_exp"]
            ),
            minimumWidth=700,
            minimumHeight=700,
            gridPos=(1, 3, 2, 1),
        )
        self.create_param_widget(
            self.get_param("overlay_color"),
            width_total=PointPositionTableWidget.widget_width,
            width_io=90,
            width_text=120,
            width_unit=0,
            gridPos=(1, 2, 1, 1),
        )
        self.add_any_widget(
            "point_table",
            PointPositionTableWidget(self._widgets["plot"]),
            gridPos=(2, 2, 1, 1),
        )
        _button_params = dict(
            fixedWidth=CONFIG_WIDGET_WIDTH,
            fixedHeight=25,
            parent_widget=self._widgets["left_container"],
        )
        _param_config = dict(
            parent_widget=self._widgets["left_container"],
            width_total=CONFIG_WIDGET_WIDTH,
            width_io=100,
            width_text=CONFIG_WIDGET_WIDTH - 130,
            width_unit=30,
        )
        self.create_line(None, parent_widget=self._widgets["left_container"])
        self.create_label(
            "label_title",
            "Input image:",
            fontsize=STANDARD_FONT_SIZE + 1,
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["left_container"],
            underline=True,
        )

        self.add_any_widget(
            "image_selection",
            SelectImageFrameWidget(
                *self.get_params("filename", "hdf5_key", "hdf5_frame"),
                import_reference="SelectPointsForBeamcenterWindow__import",
            ),
            fixedWidth=CONFIG_WIDGET_WIDTH,
            parent_widget=self._widgets["left_container"],
        )
        self.create_line(None, parent_widget=self._widgets["left_container"])
        self.create_spacer(
            None, fixedWidth=25, parent_widget=self._widgets["left_container"]
        )
        self.create_button(
            "but_set_beamcenter",
            "Set point in list as beamcenter",
            **_button_params,
        )
        self.create_button(
            "but_fit_circle",
            "Fit beamcenter with circle",
            **_button_params,
        )
        self.create_button(
            "but_fit_ellipse",
            "Fit beamcenter with ellipse",
            **_button_params,
        )
        self.create_line(None, parent_widget=self._widgets["left_container"])
        self.create_param_widget(self.get_param("beamcenter_x"), **_param_config)
        self.create_param_widget(self.get_param("beamcenter_y"), **_param_config)
        self.create_line(
            "line_final",
            parent_widget=self._widgets["left_container"],
        )
        self.create_button(
            "but_confirm_selection",
            "Confirm selected beamcenter",
            **_button_params,
        )
        self.create_spacer(
            "final_spacer",
            vertical_policy=QtWidgets.QSizePolicy.Expanding,
            parent_widget=self._widgets["left_container"],
        )

    def connect_signals(self):
        """
        Build the frame and create all widgets.
        """
        self._bc_controller = ManuallySetBeamcenterController(
            self, self._widgets["plot"], self._widgets["point_table"]
        )
        self._widgets["image_selection"].sig_new_file_selection.connect(
            self._selected_new_file
        )
        self._widgets["but_set_beamcenter"].clicked.connect(
            self._bc_controller.set_beamcenter_from_point
        )
        self._widgets["but_fit_circle"].clicked.connect(
            self._bc_controller.fit_beamcenter_with_circle
        )
        self._widgets["but_fit_ellipse"].clicked.connect(
            self._bc_controller.fit_beamcenter_with_ellipse
        )
        self._widgets["but_confirm_selection"].clicked.connect(self._confirm_points)
        self.param_widgets["overlay_color"].io_edited.connect(
            self._bc_controller.set_marker_color
        )

    def finalize_ui(self):
        """
        Finalize the user interface.
        """
        self._update_image_if_required()
        self._bc_controller.manual_beamcenter_update(None)
        self._bc_controller.show_plot_items("beamcenter")

    @QtCore.Slot(str, object)
    def _selected_new_file(self, filename, kwargs):
        """
        Open a new file / frame based on the selected file input Parameters.

        Parameters
        ----------
        filename : str
            The filename of the new image file to be opened.
        kwargs : dict
            The dictionary with additional parameters (hdf5 frame and dataset) for
            file opening.
        """
        self._image = import_data(filename, **kwargs)
        _path = Path(filename)
        self._widgets["plot"].plot_pydidas_dataset(self._image, title=_path.name)
        self._widgets["plot"].changeCanvasToDataAction._actionTriggered()

    @QtCore.Slot()
    def _confirm_points(self):
        """
        Confirm the selection of the specified points.
        """
        if not self._bc_controller.beamcenter_is_set:
            _reply = QuestionBox(
                "Beamcenter not set",
                "No beamcenter has been set. Do you want to close the window without "
                "setting a beamcenter?",
            ).exec_()
            if _reply:
                self.close()
            return
        _x = self.get_param_value("beamcenter_x")
        _y = self.get_param_value("beamcenter_y")
        self.sig_selected_beamcenter.emit(_x, _y)
        self.close()

    def _update_image_if_required(self):
        """
        Check the dimensions of the current image with respect to the Detector size.
        """
        _shape = (
            self._config["diffraction_exp"].get_param_value("detector_npixy"),
            self._config["diffraction_exp"].get_param_value("detector_npixx"),
        )
        if _shape == self._image.shape:
            return
        self._image = Dataset(np.zeros(_shape))
        self._widgets["image_selection"].set_param_value_and_widget("filename", ".")
        self._widgets["plot"].plot_pydidas_dataset(self._image)
        self._widgets["plot"].changeCanvasToDataAction._actionTriggered()

    def closeEvent(self, event):
        """
        Handle the close event and also emit a signal.

        Parameters
        ----------
        event : QEvent
            The calling event.
        """
        self.sig_about_to_close.emit()
        super().closeEvent(event)

    def show(self):
        """
        Show the window and check the image shape.
        """
        self._update_image_if_required()
        super().show()
