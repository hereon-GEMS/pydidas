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
#
# Parts of this file are adapted based on the pyfai-calib widget which is distributed
# under the license given below:

"""
Module with the PyfaiCalibFrame which is roughly based on the pyfai-calib2 window
to be used within pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PyfaiCalibFrame", "get_pyfai_calib_icon_path"]

import os
import functools

from qtpy import QtWidgets, QtGui, QtCore
import pyFAI
from pyFAI.app import calib2
from pyFAI.gui.model import MarkerModel
from pyFAI.gui.utils import projecturl
from pyFAI.gui.CalibrationWindow import MenuItem
from pyFAI.gui.CalibrationContext import CalibrationContext
from pyFAI.gui.tasks import (
    ExperimentTask,
    MaskTask,
    PeakPickingTask,
    GeometryTask,
    IntegrationTask,
)

from ...core import constants
from ...widgets import BaseFrame
from ...contexts import ExperimentContext


EXP = ExperimentContext()


def create_calib_tasks():
    """
    Create the tasks for the calibration.

    Returns
    -------
    tasks : list
        The list with the tasks.

    """
    tasks = [
        ExperimentTask.ExperimentTask(),
        MaskTask.MaskTask(),
        PeakPickingTask.PeakPickingTask(),
        GeometryTask.GeometryTask(),
        IntegrationTask.IntegrationTask(),
    ]
    return tasks


def get_pyfai_calib_icon_path():
    """
    Get the pyFAI calibration icon.

    Returns
    -------
    str
        The full path and filename for pyFAI calibration icon.
    """
    return os.sep.join(
        [os.path.dirname(pyFAI.__file__), "resources", "gui", "images", "icon.png"]
    )


class PyfaiCalibFrame(BaseFrame):
    """
    A pyFAI Calibration frame similar to the "pyfai-calib2", adapted to be
    used within pydidas.

    Note: Because this code is taking almost 100 % from pyFAI, the names,
    nomenclature and code structure is different from the rest of pydidas.

    Acknowledgements go to the creators of pyFAI for making it freely
    available.
    """

    menu_icon = "path::" + get_pyfai_calib_icon_path()
    menu_title = "pyFAI calibration"
    menu_entry = "pyFAI calibration"

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)
        self._setup_pyfai_context()
        self._tasks = create_calib_tasks()

    def _setup_pyfai_context(self):
        """
        Setup the context for the pyfai calibration.
        """
        _PYFAI_SETTINGS = QtCore.QSettings(
            QtCore.QSettings.IniFormat,
            QtCore.QSettings.UserScope,
            "pyfai",
            "pyfai-calib2",
            None,
        )
        CalibrationContext._releaseSingleton()
        _calib_context = CalibrationContext(_PYFAI_SETTINGS)
        _calib_context.restoreSettings()
        options = calib2.parse_options()
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
            fontsize=constants.STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self.add_any_widget(
            "task_list",
            QtWidgets.QListWidget(),
            fixedWidth=150,
            sizePolicy=constants.FIX_EXP_POLICY,
            gridPos=(1, 0, 1, 1),
        )
        _text = (
            "Online help"
            if projecturl.get_documentation_url("").startswith("http")
            else "Help"
        )
        self.create_button("but_help", _text, gridPos=(2, 0, 1, 1), fixedWidth=150)
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
            _menu_item = MenuItem(self._widgets["task_list"])
            _menu_item.setText(task.windowTitle())
            _menu_item.setIcon(task.windowIcon())
            task.warningUpdated.connect(
                functools.partial(self._update_task_state, task, _menu_item)
            )
        if len(self._tasks) > 0:
            self._widgets["task_list"].setCurrentRow(0)
            # Hide the nextStep button of the last task
            task.setNextStepVisible(False)

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
    def _update_task_state(self, task, item):
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
    def _store_geometry(self):
        """
        Store the fitted geometry in the ExperimentContext.
        """
        geo = self._model.fittedGeometry()
        det = self._model.experimentSettingsModel().detector()
        EXP.set_param_value("xray_wavelength", geo.wavelength().value())
        EXP.set_param_value("detector_dist", geo.distance().value())
        EXP.set_param_value("detector_poni1", geo.poni1().value())
        EXP.set_param_value("detector_poni2", geo.poni2().value())
        EXP.set_param_value("detector_rot1", geo.rotation1().value())
        EXP.set_param_value("detector_rot2", geo.rotation2().value())
        EXP.set_param_value("detector_rot3", geo.rotation3().value())
        EXP.set_param_value("detector_name", det.name)
        EXP.set_param_value("detector_npixx", det.shape[1])
        EXP.set_param_value("detector_npixy", det.shape[0])
        EXP.set_param_value("detector_pxsizex", det.pixel2)
        EXP.set_param_value("detector_pxsizey", det.pixel1)
