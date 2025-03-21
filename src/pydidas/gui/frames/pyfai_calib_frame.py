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
#
# Parts of this file are adapted from the pyFAI.gui.CalibrationWindow
# widget which is distributed under the MIT license.

"""
Module with the PyfaiCalibFrame which is roughly based on the pyfai-calib2 window
to be used within pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PyfaiCalibFrame"]


import argparse
import functools
import os
from typing import Self, Union

import numpy as np
import pyFAI
from pyFAI.app import calib2
from pyFAI.gui.CalibrationContext import CalibrationContext
from pyFAI.gui.CalibrationWindow import MenuItem
from pyFAI.gui.model import MarkerModel
from pyFAI.gui.utils import projecturl
from qtpy import QtCore, QtGui, QtWidgets
from silx.gui.plot.tools import ImageToolBar

from pydidas.contexts import DiffractionExperimentContext, DiffractionExperimentIo
from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.core.constants import FONT_METRIC_HALF_CONFIG_WIDTH, POLICY_FIX_EXP
from pydidas.widgets import PydidasFileDialog, icon_with_inverted_colors
from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin
from pydidas.widgets.framework import BaseFrame
from pydidas.widgets.silx_plot import actions


EXP = DiffractionExperimentContext()


class _List(PydidasWidgetMixin, QtWidgets.QListWidget):
    """
    A list with automatic width scaling.

    The scaling is handled automatically based on the font settings.
    """

    def __init__(self, **kwargs: dict):
        QtWidgets.QListWidget.__init__(self, parent=kwargs.get("parent", None))
        PydidasWidgetMixin.__init__(self, **kwargs)


def _create_calib_tasks() -> list[QtWidgets.QWidget]:
    """
    Create the tasks for the calibration.

    This function will also overload the generic tasks and add an CropHistogramOutlier
    action to the toolbars and change the default file dialog to use the pydidas
    file dialog.

    Returns
    -------
    tasks : list
        The list with the tasks.

    """
    from pyFAI.gui.tasks import (
        ExperimentTask,
        GeometryTask,
        IntegrationTask,
        MaskTask,
        PeakPickingTask,
    )
    from silx.gui.qt import QToolBar

    tasks = [
        ExperimentTask.ExperimentTask(),
        MaskTask.MaskTask(),
        PeakPickingTask.PeakPickingTask(),
        GeometryTask.GeometryTask(),
        IntegrationTask.IntegrationTask(),
    ]
    for _item in ["_imageLoader", "_maskLoader", "_darkLoader", "_flatLoader"]:
        _obj = getattr(tasks[0], _item)
        _action = actions.PydidasLoadImageAction(_obj, ref=f"PyFAI_calib{_item}")
        _obj.addAction(_action)
        _obj.setDefaultAction(_action)
        _obj.setText("...")
    for _task in tasks[0:4]:
        _plot = getattr(_task, f"_{_task.__class__.__name__}__plot")
        _toolbar = _plot.findChildren(ImageToolBar)[0]
        _histo_crop_action = actions.CropHistogramOutliers(
            _plot, parent=_plot, forced_image_legend="image"
        )
        _autoscale_action = actions.AutoscaleToMeanAndThreeSigma(
            _plot, parent=_plot, forced_image_legend="image"
        )
        _widget_action = [
            _action
            for _action in _toolbar.actions()
            if isinstance(_action, QtWidgets.QWidgetAction)
        ][0]
        _toolbar.addAction(_histo_crop_action)
        _toolbar.addAction(_autoscale_action)
        _toolbar.insertAction(_widget_action, _histo_crop_action)
        _toolbar.insertAction(_widget_action, _autoscale_action)
    # explicitly hide the toolbar with the 3D visualization:
    tasks[0]._ExperimentTask__plot.findChildren(QToolBar)[2].setVisible(False)
    tasks[3]._GeometryTask__plot.findChildren(QToolBar)[2].setVisible(False)
    # disable the default ring option in the peak picking task:
    tasks[2]._PeakPickingTask__createNewRingOption.setChecked(False)
    # insert button for exporting to DiffractionExperimentContext:
    _parent = tasks[4]._savePoniButton.parent()
    tasks[4]._update_context_button = QtWidgets.QPushButton(
        "Update pydidas diffraction setup from calibration"
    )
    _parent.layout().addWidget(tasks[4]._update_context_button)
    return tasks


class PyfaiCalibFrame(BaseFrame):
    """
    A pyFAI Calibration frame similar to the "pyfai-calib2", adapted to be
    used within pydidas.

    Note: Because this code is adapted from pyFAI, the names, nomenclature and
    code structure is different from the rest of pydidas.

    Acknowledgements go to the creators of pyFAI for making it freely
    available.
    """

    menu_icon = "path::" + os.path.join(
        os.path.dirname(pyFAI.__file__), "resources", "gui", "images", "icon.png"
    )
    menu_title = "pyFAI calibration"
    menu_entry = "pyFAI calibration"

    def __init__(self, **kwargs: dict) -> Self:
        BaseFrame.__init__(self, **kwargs)
        self._setup_pyfai_context()
        self._tasks = _create_calib_tasks()
        self.__export_dialog = PydidasFileDialog()

    def _setup_pyfai_context(self):
        """
        Set up the context for the pyfai calibration.

        """
        import silx.gui.utils.matplotlib  # noqa F401

        pyFAI.resources.silx_integration()

        _settings = QtCore.QSettings(
            QtCore.QSettings.IniFormat,
            QtCore.QSettings.UserScope,
            "pyfai",
            "pyfai-calib2",
            None,
        )
        CalibrationContext._releaseSingleton()
        _calib_context = CalibrationContext(_settings)
        _calib_context.restoreSettings()
        parser = argparse.ArgumentParser()
        calib2.configure_parser_arguments(parser)
        options, _unknown = parser.parse_known_args()
        calib2.setup_model(_calib_context.getCalibrationModel(), options)
        self._calibration_context = _calib_context
        self._calibration_context.setParent(self)

    def build_frame(self):
        """
        Build the frame with all required widgets.
        """
        self.setUpdatesEnabled(False)
        self.create_label(
            "title",
            "pyFAI calibration",
            fontsize_offset=4,
            bold=True,
            gridPos=(0, 0, 1, 2),
        )
        self.create_any_widget(
            "task_list",
            _List,
            font_metric_width_factor=FONT_METRIC_HALF_CONFIG_WIDTH,
            sizePolicy=POLICY_FIX_EXP,
            gridPos=(1, 0, 1, 1),
        )
        _text = (
            "Online help"
            if projecturl.get_documentation_url("").startswith("http")
            else "Help"
        )
        self.create_button(
            "but_help",
            _text,
            gridPos=(2, 0, 1, 1),
            font_metric_width_factor=FONT_METRIC_HALF_CONFIG_WIDTH,
        )
        self.add_any_widget(
            "task_stack",
            QtWidgets.QStackedWidget(),
            gridPos=(1, 1, 2, 1),
        )
        for task in self._tasks:
            self._widgets["task_stack"].addWidget(task)
        self.setUpdatesEnabled(True)

    def connect_signals(self):
        """
        Connect the required signals to run the pyFAI calibration.
        """
        self._widgets["task_list"].currentRowChanged.connect(
            self._widgets["task_stack"].setCurrentIndex
        )
        self._widgets["but_help"].clicked.connect(self._display_help)
        for task in self._tasks:
            task.nextTaskRequested.connect(self.display_next_task)
            _inverted_icon = icon_with_inverted_colors(task.windowIcon())
            _menu_item = MenuItem(self._widgets["task_list"])
            _menu_item.setText(task.windowTitle())
            _menu_item.setIcon(_inverted_icon)
            task.warningUpdated.connect(
                functools.partial(self._update_task_state, task, _menu_item)
            )
        if len(self._tasks) > 0:
            self._widgets["task_list"].setCurrentRow(0)
            # Hide the nextStep button of the last task
            task.setNextStepVisible(False)
        self._tasks[4]._savePoniButton.clicked.disconnect()
        self._tasks[4]._savePoniButton.clicked.connect(self._export_poni)
        self._tasks[4]._update_context_button.clicked.connect(
            self._update_pydidas_diffraction_exp_context
        )

    def finalize_ui(self):
        """
        Run the UI finalization after creating widgets and connecting signals.
        """
        self.setup_calibration_model()

    def setup_calibration_model(self):
        """
        Setup the calibration model from the context.
        """
        self._model = self._calibration_context.getCalibrationModel()
        if len(self._model.markerModel()) == 0:
            origin = MarkerModel.PixelMarker("Origin", 0, 0)
            self._model.markerModel().add(origin)
        for task in self._tasks:
            task.setModel(self._model)

    @QtCore.Slot()
    def _display_help(self):
        """
        Display the help for the pyFAI calibration.
        """
        _url = projecturl.get_documentation_url("usage/cookbook/calib-gui/index.html")
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(_url))

    @QtCore.Slot(object, object)
    def _update_task_state(self, task: QtWidgets.QWidget, item: MenuItem):
        """
        Update the task state.

        This method re-implements the generic pyFAI method.

        Parameters
        ----------
        task : QtWidgets.QWidget
            The associated task widget.
        item : MenuItem
            The associated menu item.
        """
        item.setWarnings(task.nextStepWarning())

    @QtCore.Slot()
    def display_next_task(self):
        """
        Display the next task in the QStackedWidget.
        """
        _index = self._widgets["task_list"].currentRow() + 1
        if _index < self._widgets["task_list"].count():
            self._widgets["task_list"].setCurrentRow(_index)

    @QtCore.Slot()
    def _export_poni(self):
        """
        Export the poni settings to a file.
        """
        _fname = self.__export_dialog.get_saving_filename(
            caption="Export experiment context file",
            formats=DiffractionExperimentIo.get_string_of_formats(),
            default_extension="yaml",
            dialog=QtWidgets.QFileDialog.getSaveFileName,
            qsettings_ref="PyfaiCalibFrame__export",
            info_string=(
                "<b>Note:</b> Using yaml format allows to export the mask file name as "
                "well. pyFAI's poni format does not include the mask file."
            ),
        )
        if _fname is None:
            return
        _experiment = DiffractionExperiment()
        _det = self._model.experimentSettingsModel().detector()
        _geo = self._model.fittedGeometry()
        _experiment.set_param_value("detector_name", _det.name)
        _experiment.set_param_value("detector_npixx", _det.shape[1])
        _experiment.set_param_value("detector_npixy", _det.shape[0])
        _experiment.set_param_value("detector_pxsizex", 1e6 * _det.pixel2)
        _experiment.set_param_value("detector_pxsizey", 1e6 * _det.pixel1)
        _wavelength = float(np.round(_geo.wavelength().value() * 1e10, 12))
        _experiment.set_param_value("xray_wavelength", _wavelength)

        _mask = self._get_mask_filename()
        if _mask is not None:
            _experiment.set_param_value("detector_mask_file", _mask)
        if _geo.isValid():
            for _key, _value in [
                ["detector_dist", _geo.distance().value()],
                ["detector_poni1", _geo.poni1().value()],
                ["detector_poni2", _geo.poni2().value()],
                ["detector_rot1", _geo.rotation1().value()],
                ["detector_rot2", _geo.rotation2().value()],
                ["detector_rot3", _geo.rotation3().value()],
            ]:
                _experiment.set_param_value(_key, _value)
        DiffractionExperimentIo.export_to_file(
            _fname, diffraction_exp=_experiment, overwrite=True
        )

    def _get_mask_filename(self) -> Union[str, None]:
        """
        Get the filename of the mask file from the fitted model.

        Returns
        -------
        Union[str, None]
            The filename of the mask file. If no mask file has been, returns None.
        """
        _maskfile = self._model.experimentSettingsModel().mask().filename()
        if _maskfile is not None:
            if _maskfile.startswith("fabio:///"):
                _maskfile = _maskfile[9:]
        return _maskfile

    @QtCore.Slot()
    def _update_pydidas_diffraction_exp_context(self):
        """
        Store the fitted geometry in the DiffractionExperimentContext.
        """
        geo = self._model.fittedGeometry()
        det = self._model.experimentSettingsModel().detector()
        EXP.set_param_value(
            "xray_wavelength", float(np.round(geo.wavelength().value() * 1e10, 12))
        )
        EXP.set_param_value("detector_dist", geo.distance().value())
        EXP.set_param_value("detector_poni1", geo.poni1().value())
        EXP.set_param_value("detector_poni2", geo.poni2().value())
        EXP.set_param_value("detector_rot1", geo.rotation1().value())
        EXP.set_param_value("detector_rot2", geo.rotation2().value())
        EXP.set_param_value("detector_rot3", geo.rotation3().value())
        EXP.set_param_value("detector_name", det.name)
        EXP.set_param_value("detector_npixx", det.shape[1])
        EXP.set_param_value("detector_npixy", det.shape[0])
        EXP.set_param_value("detector_pxsizex", 1e6 * det.pixel2)
        EXP.set_param_value("detector_pxsizey", 1e6 * det.pixel1)
        _mask = self._get_mask_filename()
        if _mask is not None:
            EXP.set_param_value("detector_mask_file", _mask)
