# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the DefineDiffractionExpFrame which is used to define or modify the
global experimental settings like detector, geometry and energy.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DefineDiffractionExpFrame"]


from functools import partial
from pathlib import Path
from typing import Union

import numpy as np
from pyFAI.detectors import Detector
from pyFAI.gui.CalibrationContext import CalibrationContext
from pyFAI.gui.dialog.DetectorSelectorDialog import DetectorSelectorDialog
from qtpy import QtCore, QtWidgets

from pydidas.contexts import DiffractionExperimentContext, DiffractionExperimentIo
from pydidas.core import get_generic_param_collection
from pydidas.gui.frames.builders import DefineDiffractionExpFrameBuilder
from pydidas.widgets import PydidasFileDialog
from pydidas.widgets.dialogues import critical_warning
from pydidas.widgets.framework import BaseFrame
from pydidas.widgets.windows import (
    ConvertFit2dGeometryWindow,
    ManuallySetBeamcenterWindow,
)


EXP = DiffractionExperimentContext()

_GEO_INVALID = (
    "The pyFAI geometry is not valid and cannot be copied. This is probably due to "
    "either:\n1. No fit has been performed.\nor\n2. The fit did not succeed."
)

_ENERGY_INVALID = (
    "The X-ray energy / wavelength cannot be set because the pyFAI geometry is not "
    "valid. This is probably due to either:\n1. No fit has been performed.\nor\n"
    "2. The fit did not succeed."
)


class DefineDiffractionExpFrame(BaseFrame):
    """
    The DefineDiffractionExpFrame is the main frame for reading, editing and
    saving the DiffractionExperimentContext in the GUI.
    """

    menu_icon = "pydidas::frame_icon_define_diffraction_exp"
    menu_title = "Define diffraction setup"
    menu_entry = "Workflow processing/Define diffraction setup"

    def __init__(self, **kwargs: dict):
        BaseFrame.__init__(self, **kwargs)
        self.params = EXP.params
        self._bc_params = get_generic_param_collection("beamcenter_x", "beamcenter_y")
        self._io_dialog = PydidasFileDialog()
        self._select_beamcenter_window = None
        self._fit2d_window = None

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        DefineDiffractionExpFrameBuilder.build_frame(self)

    def connect_signals(self):
        """
        Connect all signals and slots in the frame.
        """
        self._widgets["but_load_from_file"].clicked.connect(self.import_from_file)
        self._widgets["but_copy_from_pyfai"].clicked.connect(self.copy_all_from_pyfai)
        self._widgets["but_select_detector"].clicked.connect(self.select_detector)
        self._widgets["but_select_beamcenter_manually"].clicked.connect(
            self.select_beamcenter_manually
        )
        self._widgets["but_convert_fit2d"].clicked.connect(self.convert_from_fit2d)

        self._widgets["but_save_to_file"].clicked.connect(self.export_to_file)
        for _param_key in self.params.keys():
            param = self.get_param(_param_key)
            # disconnect directly setting the parameters and route
            # through update_param method to catch wavelength/energy
            _w = self.param_widgets[param.refkey]
            _w.io_edited.disconnect()
            _w.io_edited.connect(partial(self.update_param, _param_key, _w))
        EXP.sig_params_changed.connect(self._update_beamcenter)

    def set_param_value_and_widget(self, key: str, value: object):
        """
        Update a Parameter value both in the widget and ParameterCollection.

        This method overloads the generic set_param_value_and_widget method to
        process the linked energy / wavelength parameters.

        Parameters
        ----------
        key : str
            The Parameter reference key.
        value : object
            The new Parameter value. The datatype is determined by the
            Parameter.
        """
        EXP.set_param_value(key, value)
        if key in ["xray_energy", "xray_wavelength"]:
            _energy = self.get_param_value("xray_energy")
            _lambda = self.get_param_value("xray_wavelength")
            self.param_widgets["xray_energy"].set_value(_energy)
            self.param_widgets["xray_wavelength"].set_value(_lambda)
        else:
            self.param_widgets[key].set_value(value)

    @QtCore.Slot(str)
    def update_param(self, param_key: str, widget: QtWidgets.QWidget, value_str: str):
        """
        Update a value in both the Parameter and the corresponding widget.

        Parameters
        ----------
        param_key : str
            The reference key.
        widget : pydidas.widgets.parameter_config.BaseParamIoWidget
            The Parameter editing widget.
        value_str : str
            The string representation of the value.
        """
        EXP.set_param_value(param_key, widget.get_value())
        # explicitly call update fo wavelength and energy
        if param_key == "xray_wavelength":
            _w = self.param_widgets["xray_energy"]
            _w.set_value(EXP.get_param_value("xray_energy"))
        elif param_key == "xray_energy":
            _w = self.param_widgets["xray_wavelength"]
            _w.set_value(EXP.get_param_value("xray_wavelength"))

    def select_detector(self):
        """
        Open a dialog to select a detector.
        """
        dialog = DetectorSelectorDialog()
        dialog.exec_()
        _det = dialog.selectedDetector()
        self.update_detector_params(_det, show_warning=False)

    def copy_all_from_pyfai(self):
        """
        Copy all settings (i.e. detector, energy and geometry) from pyFAI.
        """
        self.copy_detector_from_pyFAI()
        self.copy_energy_from_pyFAI(show_warning=False)
        self.copy_geometry_from_pyFAI()

    def copy_detector_from_pyFAI(self, show_warning: bool = True):
        """
        Copy the detector from the pyFAI CalibrationContext instance.

        Parameters
        ----------
        show_warning : bool, optional
            Flag to show a warning if the detector cannot be found or simply
            to ignore. True will show the warning. The default is True.
        """
        context = CalibrationContext.instance()
        model = context.getCalibrationModel()
        _det = model.experimentSettingsModel().detector()
        _maskfile = model.experimentSettingsModel().mask().filename()
        self.update_detector_params(_det, maskfile=_maskfile, show_warning=show_warning)

    def update_detector_params(
        self,
        det: Detector,
        maskfile: Union[None, str, Path] = None,
        show_warning: bool = True,
    ):
        """
        Update the pydidas detector Parameters based on the selected pyFAI detector.

        Parameters
        ----------
        det : pyFAI.detectors.Detector
            The detector instance.
        maskfile : Union [None, str, Path], optional
            The path of the mask file, if it has been defined in the pyFAI calibration.
            The default is None.
        show_warning : bool, optional
            Flag to show a warning if the detector cannot be found or simply
            to ignore. True will show the warning. The default is True.
        """
        if det is not None:
            self.set_param_value_and_widget("detector_name", det.name)
            self.set_param_value_and_widget("detector_npixx", det.shape[1])
            self.set_param_value_and_widget("detector_npixy", det.shape[0])
            self.set_param_value_and_widget("detector_pxsizex", 1e6 * det.pixel2)
            self.set_param_value_and_widget("detector_pxsizey", 1e6 * det.pixel1)
            if maskfile is not None:
                if maskfile.startswith("fabio:///"):
                    maskfile = maskfile[9:]
                self.set_param_value_and_widget("detector_mask_file", maskfile)
        elif show_warning:
            critical_warning(
                "No pyFAI Detector",
                "No detector selected in pyFAI. Cannot copy information.",
            )

    def copy_geometry_from_pyFAI(self, show_warning: bool = True):
        """
        Copy the geometry from the pyFAI CalibrationContext instance.

        Parameters
        ----------
        show_warning : bool, optional
            Flag to show a warning if the geometry cannot be found or simply
            to ignore. True will show the warning. The default is True.
        """
        model = CalibrationContext.instance().getCalibrationModel()
        _geo = model.fittedGeometry()
        if _geo.isValid():
            for key, value in [
                ["detector_dist", _geo.distance().value()],
                ["detector_poni1", _geo.poni1().value()],
                ["detector_poni2", _geo.poni2().value()],
                ["detector_rot1", _geo.rotation1().value()],
                ["detector_rot2", _geo.rotation2().value()],
                ["detector_rot3", _geo.rotation3().value()],
            ]:
                self.set_param_value_and_widget(key, float(np.round(value, 12)))
        elif show_warning:
            critical_warning("pyFAI geometry invalid", _GEO_INVALID)

    def copy_energy_from_pyFAI(self, show_warning: bool = True):
        """
        Copy the pyFAI energy and store it in the DiffractionExperimentContext.

        Parameters
        ----------
        show_warning : TYPE, optional
            Flag to show a warning if the energy/wavelength cannot be found
            or simply to ignore the missing value. True will show the warning.
            The default is True.
        """
        model = CalibrationContext.instance().getCalibrationModel()
        _geo = model.fittedGeometry()
        if _geo.isValid():
            _wavelength = float(np.round(_geo.wavelength().value() * 1e10, 12))
            self.set_param_value_and_widget("xray_wavelength", _wavelength)
        elif show_warning:
            critical_warning("pyFAI geometry invalid", _ENERGY_INVALID)

    @QtCore.Slot()
    def select_beamcenter_manually(self):
        """
        Select the beamcenter manually.
        """
        if self._select_beamcenter_window is None:
            self._select_beamcenter_window = ManuallySetBeamcenterWindow()
            self._select_beamcenter_window.sig_selected_beamcenter.connect(
                self._beamcenter_selected
            )
            self._select_beamcenter_window.sig_about_to_close.connect(
                self._child_window_closed
            )
        self._select_beamcenter_window.update_detector_description(
            self.get_param_value("detector_name"),
            self.get_param_value("detector_mask_file"),
        )
        self._select_beamcenter_window.show()
        self.setEnabled(False)

    @QtCore.Slot(float, float)
    def _beamcenter_selected(self, center_x: float, center_y: float):
        """
        Set the selected beamcenter in the DiffractionExperiment

        Parameters
        ----------
        center_x : float
            The beamcenter x value in pixels
        center_y : float
            The beancenter y value in pixels.
        """
        _px_size_x = self.get_param_value("detector_pxsizex")
        _px_size_y = self.get_param_value("detector_pxsizey")

        self.set_param_value_and_widget("detector_poni1", 1e-6 * _px_size_y * center_y)
        self.set_param_value_and_widget("detector_poni2", 1e-6 * _px_size_x * center_x)
        for _index in [1, 2, 3]:
            self.set_param_value_and_widget(f"detector_rot{_index}", 0)

    @QtCore.Slot()
    def _child_window_closed(self):
        """
        Handle the signal that the beamcenter window is to be closed.
        """
        self.setEnabled(True)

    @QtCore.Slot()
    def _update_beamcenter(self):
        """
        Update the displayed beamcenter position.
        """
        _bx, _by = np.round(EXP.beamcenter, 3)
        self._bc_params.set_value("beamcenter_x", _bx)
        self._bc_params.set_value("beamcenter_y", _by)
        self.update_widget_value("beamcenter_x", _bx)
        self.update_widget_value("beamcenter_y", _by)

    def import_from_file(self):
        """
        Open a dialog to select a filename and load DiffractionExperimentContext from
        the selected file.

        Note: This method will overwrite all current settings.
        """
        _fname = self._io_dialog.get_existing_filename(
            caption="Import experiment context file",
            formats=DiffractionExperimentIo.get_string_of_formats(),
            qsettings_ref="DefineDiffractionExpFrame__import",
        )
        if _fname is not None:
            EXP.import_from_file(_fname)
            for param in EXP.params.values():
                self.param_widgets[param.refkey].set_value(param.value)

    def export_to_file(self):
        """
        Open a dialog to select a filename and write all currrent settings
        for the DiffractionExperimentContext to file.
        """
        _fname = self._io_dialog.get_saving_filename(
            caption="Export experiment context file",
            formats=DiffractionExperimentIo.get_string_of_formats(),
            default_extension="yaml",
            dialog=QtWidgets.QFileDialog.getSaveFileName,
            qsettings_ref="DefineDiffractionExpFrame__export",
        )
        if _fname is not None:
            EXP.export_to_file(_fname, overwrite=True)

    def frame_activated(self, index: int):
        """
        Add a check whether the DiffractionExperimentContext has changed from some
        other source (e.g. pyFAI calibration) and update widgets accordingly.

        Parameters
        ----------
        index : int
            The active frame index.
        """
        super().frame_activated(index)
        if index == self.frame_index:
            if hash(self.params) != self._config["exp_hash"]:
                for _key, _param in EXP.params.items():
                    self.update_widget_value(_key, _param.value)
                self._config["exp_hash"] = hash(self.params)
        else:
            self._config["exp_hash"] = hash(self.params)

    @QtCore.Slot()
    def convert_from_fit2d(self):
        """
        Convert a Fit2d geometry to pyFAI's PONI geometry.
        """
        if self._fit2d_window is None:
            self._fit2d_window = ConvertFit2dGeometryWindow()
            self._fit2d_window.sig_about_to_close.connect(self._child_window_closed)
            self._fit2d_window.sig_new_geometry.connect(
                self._process_new_geometry_from_fit2
            )
        self._fit2d_window.show()
        self.setEnabled(False)

    @QtCore.Slot(float, float, float, float, float, float)
    def _process_new_geometry_from_fit2(
        self,
        det_dist: float,
        poni1: float,
        poni2: float,
        rot1: float,
        rot2: float,
        rot3: float,
    ):
        """
        Process the new parameters in the pyFAI geometry from the Fit2d geometry.

        Parameters
        ----------
        det_dist : float
            The new detector distance.
        poni1 : float
            The new PONI1 value.
        poni2 : float
            The new PONI2 value.
        rot1 : float
            The new detector rotation #1.
        rot2 : float
            The new detector rotation #2.
        rot3 : float
            The new detector rotation #3.
        """
        self.set_param_value_and_widget("detector_dist", det_dist)
        self.set_param_value_and_widget("detector_poni1", poni1)
        self.set_param_value_and_widget("detector_poni2", poni2)
        self.set_param_value_and_widget("detector_rot1", rot1)
        self.set_param_value_and_widget("detector_rot2", rot2)
        self.set_param_value_and_widget("detector_rot3", rot3)
