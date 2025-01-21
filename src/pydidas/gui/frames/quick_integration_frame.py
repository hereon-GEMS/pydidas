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
Module with the QuickIntegrationFrame which is allows to perform a quick integration
without fully defining Scan, DiffractionExperiment and Workflow.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["QuickIntegrationFrame"]


from functools import partial
from pathlib import Path
from typing import Union

import numpy as np
from qtpy import QtCore

from pydidas.contexts import DiffractionExperimentContext, DiffractionExperimentIo
from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.core import get_generic_param_collection
from pydidas.core.constants import PYFAI_DETECTOR_MODELS_OF_SHAPES
from pydidas.core.utils import ShowBusyMouse
from pydidas.data_io import import_data
from pydidas.gui.frames.builders import QuickIntegrationFrameBuilder
from pydidas.plugins import PluginCollection, pyFAIintegrationBase
from pydidas.widgets import PydidasFileDialog
from pydidas.widgets.controllers import (
    ManuallySetBeamcenterController,
    ManuallySetIntegrationRoiController,
)
from pydidas.widgets.framework import BaseFrame


COLL = PluginCollection()
EXP = DiffractionExperimentContext()


class QuickIntegrationFrame(BaseFrame):
    """
    The QuickIntegrationFrame allows to perform a quick integration without fully
    defining Scan, DiffractionExperiment and Workflow.
    """

    menu_icon = "pydidas::frame_icon_quick_integration"
    menu_title = "Quick integration"
    menu_entry = "Quick integration"
    default_params = get_generic_param_collection(
        "detector_pxsize",
        "beamcenter_x",
        "beamcenter_y",
        "filename",
        "hdf5_key",
        "hdf5_frame",
        "hdf5_slicing_axis",
        "overlay_color",
        "integration_direction",
        "azi_npoint",
        "rad_npoint",
        "detector_model",
    )
    params_not_to_restore = [
        "integration_direction",
        "azi_npoint",
        "rad_npoint",
        "detector_model",
        "detector_mask_file",
    ]

    def __init__(self, **kwargs: dict):
        BaseFrame.__init__(self, **kwargs)
        self._EXP = DiffractionExperiment(detector_pxsizex=100, detector_pxsizey=100)
        self.add_params(self._EXP.params)
        self.set_default_params()
        self.__import_dialog = PydidasFileDialog()
        self._config["scroll_width"] = 350
        self._config["custom_det_pxsize"] = 100
        self._config["previous_det_pxsize"] = 100
        _generic = pyFAIintegrationBase(diffraction_exp=self._EXP)
        self._plugins = {
            "generic": _generic,
            "Azimuthal integration": COLL.get_plugin_by_name(
                "PyFAIazimuthalIntegration"
            )(_generic.params, diffraction_exp=self._EXP),
            "Radial integration": COLL.get_plugin_by_name("PyFAIradialIntegration")(
                _generic.params, diffraction_exp=self._EXP
            ),
            "2D integration": COLL.get_plugin_by_name("PyFAI2dIntegration")(
                _generic.params, diffraction_exp=self._EXP
            ),
        }
        self._image = None
        self._bc_controller = None
        self._roi_controller = None

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        QuickIntegrationFrameBuilder.populate_frame(self)

    def connect_signals(self):
        """
        Connect all signals.
        """
        self._bc_controller = ManuallySetBeamcenterController(
            self,
            self._widgets["input_plot"],
            self._widgets["input_beamcenter_points"],
            selection_active=False,
        )
        self._roi_controller = ManuallySetIntegrationRoiController(
            self._widgets["roi_selector"],
            self._widgets["input_plot"],
            plugin=self._plugins["generic"],
        )
        self._roi_controller.sig_toggle_selection_mode.connect(
            self._roi_selection_toggled
        )
        self._widgets["file_selector"].sig_new_file_selection.connect(self.open_image)
        self._widgets["file_selector"].sig_file_valid.connect(self._toggle_fname_valid)

        self._widgets["copy_exp_context"].clicked.connect(self._copy_diffraction_exp)
        self._widgets["but_import_exp"].clicked.connect(self._import_diffraction_exp)
        for _label in ["but_select_beamcenter_manually", "but_confirm_beamcenter"]:
            self._widgets[_label].clicked.connect(self._toggle_beamcenter_selection)
        self._widgets["but_set_beamcenter"].clicked.connect(
            self._bc_controller.set_beamcenter_from_point
        )
        self._widgets["but_fit_center_circle"].clicked.connect(
            self._bc_controller.fit_beamcenter_with_circle
        )
        self.param_widgets["detector_pxsize"].io_edited.connect(
            self._update_detector_pxsize
        )
        self.param_widgets["detector_model"].io_edited.connect(
            self._change_detector_model
        )
        self.param_widgets["integration_direction"].io_edited.connect(
            self._changed_plugin_direction
        )
        self._widgets["but_run_integration"].clicked.connect(self._run_integration)

        for _section in ["exp", "integration"]:
            for _type in ["hide", "show"]:
                self._widgets[f"but_{_type}_{_section}_section"].clicked.connect(
                    partial(
                        self._widgets[f"{_section}_section"].setVisible, _type == "show"
                    )
                )
                self._widgets[f"but_{_type}_{_section}_section"].clicked.connect(
                    partial(
                        self._widgets[f"but_show_{_section}_section"].setVisible,
                        _type == "hide",
                    )
                )
        for _param_key in ["xray_energy", "xray_wavelength"]:
            _w = self.param_widgets[_param_key]
            _w.io_edited.disconnect()
            _w.io_edited.connect(partial(self._update_xray_param, _param_key, _w))
        for _param_key in ["beamcenter_x", "beamcenter_y"]:
            self.param_widgets[_param_key].io_edited.connect(self._update_beamcenter)
        self.param_widgets["detector_mask_file"].io_edited.connect(
            self._new_mask_file_selection
        )

    def finalize_ui(self):
        """
        Finalizes the UI and restore the SelectImageFrameWidgets params.
        """
        self._widgets["file_selector"].restore_param_widgets()

    def restore_state(self, state: dict):
        """
        Restore the GUI state.

        Parameters
        ----------
        state : dict
            The frame's state dictionary.
        """
        BaseFrame.restore_state(self, state)
        if self._config["built"]:
            self._widgets["file_selector"].restore_param_widgets()

    @QtCore.Slot(str, dict)
    def open_image(self, filename: Union[str, Path], open_image_kwargs: dict):
        """
        Open an image with the given filename and display it in the plot.

        Parameters
        ----------
        filename : Union[str, Path]
            The filename and path. The QSignal only takes strings but if the method
            is called directly, Paths are also an acceptable input.
        open_image_kwargs : dict
            Additional parameters to open a specific frame in a file.
        """
        self._image = import_data(filename, **open_image_kwargs)
        self._EXP.set_param_value("detector_npixx", self._image.shape[1])
        self._EXP.set_param_value("detector_npixy", self._image.shape[0])
        self._widgets["input_plot"].plot_pydidas_dataset(self._image)
        self._widgets["input_plot"].changeCanvasToDataAction._actionTriggered()
        self._roi_controller.show_plot_items("roi")
        self._toggle_fname_valid(True)
        self._update_detector_model()
        self._widgets["tabs"].setCurrentIndex(0)
        self._bc_controller.manual_beamcenter_update(None)

    @QtCore.Slot(bool)
    def _toggle_fname_valid(self, is_valid: bool):
        """
        Modify widgets visibility and activation based on the file selection.

        Parameters
        ----------
        is_valid : bool
            Flag to process.
        """
        self._widgets["input_plot"].setEnabled(is_valid)
        for _key in [
            "beamcenter_section",
            "integration_header",
            "integration_section",
            "run_integration",
        ]:
            self._widgets[_key].setVisible(is_valid)
        self.toggle_param_widget_visibility("detector_model", is_valid)

    def _update_detector_model(self):
        """
        Update the detector model selection based on the input image shape.
        """
        _shape = self._image.shape
        _det_models = PYFAI_DETECTOR_MODELS_OF_SHAPES.get(_shape, [])
        _model = "Custom detector" if len(_det_models) == 0 else _det_models[0]
        self.params["detector_model"].update_value_and_choices(
            _model, _det_models + ["Custom detector"]
        )
        self.param_widgets["detector_model"].update_choices(
            _det_models + ["Custom detector"]
        )
        self._change_detector_model()

    def set_param_value_and_widget(self, key, value):
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
        if key in self._EXP.params:
            self._EXP.set_param_value(key, value)
            if key in ["xray_energy", "xray_wavelength"]:
                _energy = self.get_param_value("xray_energy")
                _lambda = self.get_param_value("xray_wavelength")
                self.param_widgets["xray_energy"].set_value(_energy)
                self.param_widgets["xray_wavelength"].set_value(_lambda)
            else:
                self.param_widgets[key].set_value(value)
        else:
            BaseFrame.set_param_value_and_widget(self, key, value)

    def _update_xray_param(self, param_key, widget):
        """
        Update a value in both the Parameter and the corresponding widget.

        Parameters
        ----------
        param_key : str
            The reference key.
        widget : pydidas.widgets.parameter_config.BaseParamIoWidget
            The Parameter editing widget.
        """
        self._EXP.set_param_value(param_key, widget.get_value())
        # explicitly call update fo wavelength and energy
        if param_key == "xray_wavelength":
            _w = self.param_widgets["xray_energy"]
            _w.set_value(self._EXP.get_param_value("xray_energy"))
        elif param_key == "xray_energy":
            _w = self.param_widgets["xray_wavelength"]
            _w.set_value(self._EXP.get_param_value("xray_wavelength"))

    @QtCore.Slot(str)
    def _update_detector_pxsize(self, new_pxsize: str):
        """
        Update the detector pixel size.

        Parameters
        ----------
        new_pxsize : str
            The new pixelsize.
        manual : bool, optional
            Flag for manual
        """
        _pxsize = float(new_pxsize)
        _current_pxsize = self._config["previous_det_pxsize"]
        self._EXP.set_param_value("detector_pxsizex", _pxsize)
        self._EXP.set_param_value("detector_pxsizey", _pxsize)
        self.set_param_value_and_widget("detector_pxsize", _pxsize)
        if self.get_param_value("detector_model") == "Custom detector":
            self._config["custom_det_pxsize"] = _pxsize
        _ratio = _pxsize / _current_pxsize
        for _key in ["rad_range_lower", "rad_range_upper"]:
            self._roi_controller.set_param_value_and_widget(
                _key, self._plugins["generic"].get_param_value(_key) * _ratio
            )
        self._update_beamcenter(None)
        self._config["previous_det_pxsize"] = _pxsize

    @QtCore.Slot()
    def _change_detector_model(self):
        """
        Process a manual change of the detector model.
        """
        _det_model = self.get_param_value("detector_model")
        if _det_model == "Custom detector":
            _pxsize = self._config["custom_det_pxsize"]
            self._config["detector_name"] = None
            self.set_param_value("detector_name", "Custom detector")
            _func = self._bc_controller.set_mask_file
        else:
            _det_name = _det_model.split("]")[1].strip()
            self._EXP.set_detector_params_from_name(_det_name)
            _pxsize = self.get_param_value("detector_pxsizex")
            self._config["detector_name"] = _det_name
            _func = self._bc_controller.set_new_detector_with_mask
        if not self.get_param_value("detector_mask_file").is_file():
            _func(self._config["detector_name"])
        self._update_detector_pxsize(_pxsize)

    @QtCore.Slot(str)
    def _new_mask_file_selection(self, mask_filename: str):
        """
        Propagate the new mask to the beamcenter controller.

        Parameters
        ----------
        mask_filename : str
            The name of the new mask file or None to disable mask usage.
        """
        _path = Path(mask_filename)
        if _path.is_file():
            self._bc_controller.set_mask_file(_path)
        elif self._config["detector_name"] is not None:
            self._bc_controller.set_new_detector_with_mask(
                self._config["detector_name"]
            )
        else:
            self._bc_controller.set_mask_file(None)

    @QtCore.Slot(str)
    def _update_beamcenter(self, _):
        """
        Update the DiffractionExperiment's stored PONI from the beamcenter.
        """
        _bx = self.get_param_value("beamcenter_x")
        _by = self.get_param_value("beamcenter_y")
        _dist = self.get_param_value("detector_dist")
        self._EXP.set_beamcenter_from_fit2d_params(_bx, _by, _dist)
        self._bc_controller.manual_beamcenter_update()

    @QtCore.Slot()
    def _toggle_beamcenter_selection(self):
        """
        Toggle the manual beamcenter selection.
        """
        _active = not self._bc_controller.selection_active
        self._bc_controller.toggle_selection_active(_active)
        self._widgets["input_beamcenter_points"].setVisible(_active)
        for _txt in ["confirm_beamcenter", "set_beamcenter", "fit_center_circle"]:
            self._widgets[f"but_{_txt}"].setVisible(_active)
        self._widgets["but_select_beamcenter_manually"].setVisible(not _active)
        self._widgets["label_overlay_color"].setVisible(not _active)
        self._roi_controller.toggle_marker_color_param_visibility(not _active)
        self._widgets["file_selector"].setEnabled(not _active)
        self._roi_controller.toggle_enable(not _active)
        if _active:
            self._bc_controller.show_plot_items("all")
            self._roi_controller.remove_plot_items("roi")
            self._widgets["tabs"].setCurrentIndex(0)
        else:
            self._bc_controller.remove_plot_items("all")
            self._roi_controller.show_plot_items("roi")
            self._update_beamcenter(None)

    @QtCore.Slot(bool)
    def _roi_selection_toggled(self, active: bool):
        """
        Handle toggling of the integration ROI selection.

        Parameters
        ----------
        active : bool
            ROI selection active flag.
        """
        self._widgets["tabs"].setCurrentIndex(0)
        self._widgets["but_import_exp"].setEnabled(not active)
        self._widgets["but_select_beamcenter_manually"].setEnabled(not active)
        for _key in [
            "xray_energy",
            "xray_wavelength",
            "detector_pxsize",
            "detector_dist",
            "detector_mask_file",
            "beamcenter_x",
            "beamcenter_y",
        ]:
            self.param_widgets[_key].setEnabled(not active)

    @QtCore.Slot(str)
    def _changed_plugin_direction(self, direction: str):
        """
        Handle the selection of a new type of plugin.

        Parameters
        ----------
        direction : str
            The integration direction.
        """
        self.toggle_param_widget_visibility(
            "azi_npoint", direction != "Azimuthal integration"
        )
        self.toggle_param_widget_visibility(
            "rad_npoint", direction != "Radial integration"
        )

    def _copy_diffraction_exp(self):
        """
        Copy the DiffractionExperiment configuration from the Workflow context.
        """
        for _key, _param in EXP.params.items():
            self._EXP.set_param_value(_key, _param.value)
            if _key in self.param_widgets:
                self.param_widgets[_key].set_value(_param.value)
        self.set_param_value_and_widget(
            "detector_pxsize", self.get_param_value("detector_pxsizex")
        )
        _cx, _cy = self._EXP.beamcenter
        self.set_param_value_and_widget("beamcenter_x", _cx)
        self.set_param_value_and_widget("beamcenter_y", _cy)
        self._bc_controller.manual_beamcenter_update()

    def _import_diffraction_exp(self):
        """
        Open a dialog to select a filename and load the DiffractionExperiment.

        Note: This method will overwrite all current settings.
        """
        _fname = self.__import_dialog.get_existing_filename(
            caption="Import diffraction experiment configuration",
            formats=DiffractionExperimentIo.get_string_of_formats(),
            qsettings_ref="QuickIntegrationFrame__diffraction_exp_import",
        )
        if _fname is not None:
            self._EXP.import_from_file(_fname)
            for _key, _param in self._EXP.params.items():
                if _key in self.param_widgets:
                    self.param_widgets[_key].set_value(_param.value)
        _cx, _cy = self._EXP.beamcenter
        self.update_widget_value("beamcenter_x", np.round(_cx, 3))
        self.update_widget_value("beamcenter_y", np.round(_cy, 3))

    @QtCore.Slot()
    def _run_integration(self):
        """
        Run the integration in the pyFAI plugin.
        """
        _dir = self.get_param_value("integration_direction")
        _plugin = self._plugins[_dir]
        if _dir != "Azimuthal integration":
            _plugin.set_param_value("azi_npoint", self.get_param_value("azi_npoint"))
        if _dir != "Radial integration":
            _plugin.set_param_value("rad_npoint", self.get_param_value("rad_npoint"))
        with ShowBusyMouse():
            _plugin.pre_execute()
            _results, _ = _plugin.execute(self._image)
            self._widgets["result_plot"].plot_data(_results)
            self._widgets["tabs"].setCurrentIndex(1)
