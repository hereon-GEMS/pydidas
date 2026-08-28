# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
Module with the PyQtGraphImageViewer which allows to display images in a
customized PyQtGraph image view with additional controls for image processing
and display.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PyQtGraphImageViewer"]


from typing import Any

import numpy as np
import pyqtgraph
from qtpy import QtCore, QtWidgets

from pydidas.core.constants import POLICY_EXP_EXP, POLICY_EXP_FIX, POLICY_FIX_EXP
from pydidas.resources.pydidas_icons import create_pydidas_icon
from pydidas.widgets import WidgetWithParameterCollection
from pydidas.widgets.pyqtgraph_plot._control_panel import _ControlPanel
from pydidas.widgets.pyqtgraph_plot._image_view import _ImageView


class PyQtGraphImageViewer(WidgetWithParameterCollection):
    """
    The PyQtGraphImageViewer is a widget to display images from the camera and
    allows to control the image display and processing parameters.

    It contains an image view, a control panel for image processing parameters,
    and a button to toggle the visibility of the control panel.
    """

    def __init__(self, **kwargs: Any) -> None:
        pyqtgraph.setConfigOptions(imageAxisOrder="row-major")
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self._config_visible = True
        self.create_any_widget(
            "imageview",
            _ImageView,
            gridPos=(0, 0, 1, 1),
            sizePolicy=POLICY_EXP_EXP,
        )
        self.create_button(
            "button_toggle_control_panel",
            "Hide control panel",
            gridPos=(2, 0, 1, 1),
            icon="pydidas::menu-left.svg",
            sizePolicy=POLICY_EXP_FIX,
        )
        self.create_any_widget(
            "control_panel",
            _ControlPanel,
            font_metric_width_factor=_ControlPanel.PARAM_METRIC_WIDTH_WIDE + 4,
            gridPos=(0, 1, 3 + int(kwargs.get("support_test_image", False)), 1),
            sizePolicy=POLICY_FIX_EXP,
        )
        self.layout().setColumnStretch(0, 1)  # type: ignore[attr-defined]
        self.layout().setRowStretch(0, 1)  # type: ignore[attr-defined]
        self.create_label("label_image_data", "", gridPos=(1, 0, 1, 1))
        if kwargs.get("support_test_image", False):
            self.create_button(
                "generate_image",
                "Generate Image",
                gridPos=(3, 0, 1, 1),
                clicked=self.generate_image,
            )
        self.connect_signals()

    def connect_signals(self) -> None:
        """Connect signals and slots between the control panel and the image view."""
        _ctrl_panel = self._widgets["control_panel"]
        _image_view = self._widgets["imageview"]
        for _ctrl_panel_signal, _slot in [
            ("sig_new_image_op", _image_view.set_image_operation),
            ("sig_new_threshold", _image_view.set_threshold),
            ("sig_new_roi_boundary", _image_view.set_image_roi_param),
            ("sig_new_zoom_boundary", _image_view.set_image_zoom_param),
            ("sig_reset_thresholds", _image_view.threshold_reset),
            ("sig_new_circle_radius", _image_view.set_circle_radius),
            ("sig_marker_lock_state", _image_view.set_marker_pos_lock),
            ("sig_marker_pos", _image_view.set_marker_position),
            ("sig_use_scale", _image_view.set_scale),
        ]:
            getattr(_ctrl_panel, _ctrl_panel_signal).connect(_slot)
        for _image_view_signal, _slot in [
            ("sig_pixel_description", self._process_image_pos_data),
            ("sig_new_zoom_bounds", _ctrl_panel.external_zoom_update),
            ("sig_new_histogram_levels", _ctrl_panel.external_cmap_threshold_update),
            ("sig_image_statistics", _ctrl_panel.process_image_statistics),
            ("sig_reset_zoom", _ctrl_panel.external_zoom_reset),
            ("sig_new_marker_position", _ctrl_panel.external_marker_pos_update),
        ]:
            getattr(_image_view, _image_view_signal).connect(_slot)
        self._widgets["button_toggle_control_panel"].clicked.connect(
            self.toggle_control_panel
        )

    @QtCore.Slot(np.ndarray)
    def set_image(self, image: np.ndarray) -> None:
        """
        Show the given image in the image view.

        Parameters
        ----------
        image : np.ndarray
            The image to be displayed.
        """
        self._widgets["imageview"].show_image(image)

    # Create an alias for set_image
    show_image = set_image

    def generate_image(self) -> None:
        """Generate and display a random test image."""
        data = (
            (np.random.random((500, 500)) + np.sin(np.arange(500) / 4 / np.pi)[:, None])
            * np.linspace(0.2, 1, num=500)[None, :]
        ) * np.logspace(0, 1, num=500)[:, None]
        self.set_image(data)

    @QtCore.Slot()
    def toggle_control_panel(self) -> None:
        """
        Toggle the visibility of the control panel.
        """
        _button = self._widgets["button_toggle_control_panel"]
        self._config_visible = not self._config_visible
        self._widgets["control_panel"].setVisible(self._config_visible)
        _button.setText(
            "Hide control panel" if self._config_visible else "Show control panel"
        )
        _icon_fname = "menu-left.svg" if self._config_visible else "menu-right.svg"
        _button.setIcon(create_pydidas_icon(_icon_fname))

    def deleteLater(self) -> None:
        """Close the widget and disconnect all signals."""
        for _widget in self.findChildren(QtWidgets.QWidget):  # type: ignore[arg-type]
            _widget.deleteLater()
        super().deleteLater()

    @QtCore.Slot(str)
    def _process_image_pos_data(self, data: str) -> None:
        """
        Process new image position data from the image view.

        Parameters
        ----------
        data : str
            The image position data in string format.
        """
        self._widgets["label_image_data"].setText(data)
