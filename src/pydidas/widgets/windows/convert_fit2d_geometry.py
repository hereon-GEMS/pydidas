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
Module with the FeedbackWindow class which allows users to create a quick feedback
form which they can copy and paste to submit feedback.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ConvertFit2dGeometryWindow"]


from qtpy import QtCore, QtWidgets

from pydidas.contexts.diff_exp import (
    DiffractionExperiment,
    DiffractionExperimentContext,
)
from pydidas.core import get_generic_param_collection
from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH
from pydidas.widgets.framework import PydidasWindow


EXP = DiffractionExperimentContext()
_FIT2D_PARAM_KEYS = [
    "detector_dist_fit2d",
    "beamcenter_x",
    "beamcenter_y",
    "detector_tilt_plane",
    "detector_tilt_angle",
]
_PYFAI_PARAM_KEYS = [
    "detector_dist",
    "detector_poni1",
    "detector_poni2",
    "detector_rot1",
    "detector_rot2",
    "detector_rot3",
]


class ConvertFit2dGeometryWindow(PydidasWindow):
    """
    Enter Fit2d geometry parameters and convert them to pyFAI geometry.

    This window allows users to enter Fit2d geometry values and

    Parameters
    ----------
    self : pydidas.gui.DefineScanFrame
        The DefineScanFrame instance.
    """

    show_frame = False
    default_params = get_generic_param_collection(
        *(_FIT2D_PARAM_KEYS + _PYFAI_PARAM_KEYS)
    )

    sig_about_to_close = QtCore.Signal()
    sig_new_geometry = QtCore.Signal(float, float, float, float, float, float)

    def __init__(self, **kwargs: dict):
        PydidasWindow.__init__(self, title="Convert Fit2d geometry to pyFAI", **kwargs)
        self._exp = DiffractionExperiment(*self.get_params(*_PYFAI_PARAM_KEYS))

    def build_frame(self):
        """
        Create all widgets for the frame and place them in the layout.
        """
        _font_width, _font_height = QtWidgets.QApplication.instance().font_metrics

        self.create_label(
            "label_title",
            "Convert Fit2D geometry to pyFAI",
            bold=True,
            fontsize_offset=2,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )

        self.create_label(
            "label_title",
            "Fit2d parameter input:",
            bold=True,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        for _param_key in _FIT2D_PARAM_KEYS:
            self.create_param_widget(self.params[_param_key])
        self.create_button(
            "button_convert_to_pyfai",
            "Convert to pyFAI geometry",
        )
        self.create_line(None)
        self.create_label(
            "label_title",
            "Resulting pyFAI geometry:",
            bold=True,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        for _param_key in _PYFAI_PARAM_KEYS:
            self.create_param_widget(self.params[_param_key])
            self.param_widgets[_param_key].setReadOnly(True)
        self.create_spacer(None)
        self.create_button(
            "button_accept", "Accept and store pyFAI geometry", enabled=False
        )

    def connect_signals(self):
        """
        Connect the signals.
        """
        self._widgets["button_convert_to_pyfai"].clicked.connect(
            self._convert_inputs_to_pyfai
        )
        self._widgets["button_accept"].clicked.connect(self._emit_new_geometry)

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
        Show the window in a clean state.
        """
        self._widgets["button_accept"].setEnabled(False)
        for _key in _FIT2D_PARAM_KEYS:
            self.set_param_value_and_widget(
                _key, 100.0 if _key == "detector_dist_fit2d" else 0
            )
        for _key in _PYFAI_PARAM_KEYS:
            self.set_param_value_and_widget(_key, 0.1 if _key == "detector_dist" else 0)
        super().show()

    @QtCore.Slot()
    def _convert_inputs_to_pyfai(self):
        """
        Convert the inputs from Fit2D to pyFAI geometry.
        """
        self._exp.update_from_diffraction_exp(EXP)
        self._exp.set_beamcenter_from_fit2d_params(
            self.get_param_value("beamcenter_x"),
            self.get_param_value("beamcenter_y"),
            self.get_param_value("detector_dist_fit2d") / 1000,
            tilt=self.get_param_value("detector_tilt_angle"),
            tilt_plane=self.get_param_value("detector_tilt_plane"),
        )
        for _key in _PYFAI_PARAM_KEYS:
            self.update_widget_value(_key, self._exp.get_param_value(_key))
        self._widgets["button_accept"].setEnabled(True)

    @QtCore.Slot()
    def _emit_new_geometry(self):
        """
        Emit the new geometry as a signal.

        This signal is used to update the DiffractionExperimentContext.
        """
        self.sig_new_geometry.emit(
            *tuple(self._exp.get_param_value(_key) for _key in _PYFAI_PARAM_KEYS)
        )
        self.close()
