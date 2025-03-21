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
Module with the DirectorySpyFrame which allows to run the full
directory spy app and visualize the results.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DirectorySpyFrame"]


import time
from typing import Self

from qtpy import QtCore
from qtpy.QtWidgets import QApplication

from pydidas.apps import DirectorySpyApp
from pydidas.contexts import ScanContext
from pydidas.core import ParameterCollection
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import get_extension, pydidas_logger
from pydidas.gui.frames.builders.directory_spy_frame_builder import (
    DirectorySpyFrameBuilder,
)
from pydidas.multiprocessing import AppRunner
from pydidas.widgets.framework import BaseFrameWithApp
from pydidas.workflow import WorkflowResults, WorkflowTree


SCAN = ScanContext()
RESULTS = WorkflowResults()
TREE = WorkflowTree()
logger = pydidas_logger()


class DirectorySpyFrame(BaseFrameWithApp):
    """
    The DirectorySpyFrame is used to get automatic updates from a directory
    and display the latest data.
    """

    menu_icon = "mdi::magnify-scan"
    menu_title = "Directory spy"
    menu_entry = "Directory spy"
    default_params = ParameterCollection()

    def __init__(self, **kwargs: dict) -> Self:
        BaseFrameWithApp.__init__(self, **kwargs)
        _global_plot_update_time = self.q_settings_get(
            "global/plot_update_time", dtype=float
        )
        self._config.update(
            {
                "data_use_timeline": False,
                "plot_active": True,
                "plot_last_update": 0,
                "plot_update_time": _global_plot_update_time,
                "frame_active": True,
            }
        )
        self._app = DirectorySpyApp()
        self.set_default_params()
        self.add_params(self._app.params)

    def connect_signals(self):
        """
        Connect all required Qt slots and signals.
        """
        self.param_widgets["scan_for_all"].io_edited.connect(
            self.__update_file_widget_visibility
        )
        self.param_widgets["filename_pattern"].io_edited.connect(
            self.__update_file_widget_visibility
        )
        self.param_widgets["use_detector_mask"].io_edited.connect(
            self.__update_det_mask_visibility
        )
        self.param_widgets["use_bg_file"].io_edited.connect(
            self.__update_bg_widget_visibility
        )
        self.param_widgets["bg_file"].io_edited.connect(
            self.__update_bg_widget_visibility
        )
        self._widgets["but_once"].clicked.connect(self.__scan_once)
        self._widgets["but_show"].clicked.connect(self.__force_show)
        self._widgets["but_exec"].clicked.connect(self.__execute)
        self._widgets["but_stop"].clicked.connect(self.__stop_execution)
        self.__update_det_mask_visibility()
        self.__update_bg_widget_visibility()

    def build_frame(self):
        """
        Populate the frame with widgets.
        """
        DirectorySpyFrameBuilder.build_frame(self)

    @QtCore.Slot()
    def __update_file_widget_visibility(self):
        """
        Update the visibility of the widgets for the selection of files based
        on the 'scan_for_all' Parameter.
        """
        _vis = self.get_param_value("scan_for_all")
        _hdf5_pattern = (
            get_extension(self.get_param_value("filename_pattern", dtype=str))
            in HDF5_EXTENSIONS
        )
        self.toggle_param_widget_visibility("filename_pattern", not _vis)
        self.toggle_param_widget_visibility("hdf5_key", _vis or _hdf5_pattern)

    @QtCore.Slot()
    def __update_det_mask_visibility(self):
        """
        Update the visibility of the detector mask Parameters.
        """
        _vis = self.get_param_value("use_detector_mask")
        self.toggle_param_widget_visibility("detector_mask_file", _vis)
        self.toggle_param_widget_visibility("detector_mask_val", _vis)

    @QtCore.Slot()
    def __update_bg_widget_visibility(self):
        """
        Update the visibility of the background-file related widgets.
        """
        _vis = self.get_param_value("use_bg_file")
        self.toggle_param_widget_visibility("bg_file", _vis)
        _hdf5_bgfile = get_extension(self.get_param_value("bg_file")) in HDF5_EXTENSIONS
        self.toggle_param_widget_visibility("bg_hdf5_key", _vis and _hdf5_bgfile)
        self.toggle_param_widget_visibility("bg_hdf5_frame", _vis and _hdf5_bgfile)

    @QtCore.Slot()
    def __scan_once(self):
        """
        Scan once for the latest file.
        """
        self._config["plot_active"] = True
        self._app.prepare_run()
        self._app.multiprocessing_carryon()
        _, _fname = self._app.multiprocessing_func()
        self._app.multiprocessing_store_results(-1, _fname)
        self.__update_plot()

    @QtCore.Slot()
    def __force_show(self):
        """
        Force an update of the plot.
        """
        _active = self._config["plot_active"]
        self._config["plot_active"] = True
        self.__update_plot()
        self._config["plot_active"] = _active

    @QtCore.Slot()
    def __execute(self):
        """
        Execute the DirectorySpyApp.
        """
        self._config["plot_active"] = True
        self._run_app()

    def _run_app(self):
        """
        Parallel implementation of the execution method.
        """
        logger.debug("Starting workflow")
        self._app.multiprocessing_pre_run()
        self._config["last_update"] = time.time()
        self.__set_proc_widget_enabled_for_running(True)
        logger.debug("Starting AppRunner")
        self._runner = AppRunner(self._app, n_workers=1)
        self._runner.sig_final_app_state.connect(self._set_app)
        self._runner.sig_progress.connect(self._apprunner_update_progress)
        self._runner.sig_results.connect(self.__check_for_plot_update)
        self._runner.finished.connect(self._apprunner_finished)
        logger.debug("Running AppRunner")
        self._runner.start()

    @QtCore.Slot()
    def __stop_execution(self):
        """
        Abort the execution of the AppRunner.
        """
        if self._runner is not None:
            self._runner.send_stop_signal()
        self.set_status("Stopped scanning for new image files.")
        self.__set_proc_widget_enabled_for_running(False)

    @QtCore.Slot()
    def _apprunner_finished(self):
        """
        Clean up after AppRunner is done.
        """
        logger.debug("Telling AppRunner to exit.")
        self._runner.exit()
        self._runner.deleteLater()
        QApplication.instance().sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
        logger.debug("AppRunner successfully shut down.")
        self.set_status("Stopped scanning for new images.")
        self.__set_proc_widget_enabled_for_running(False)
        self.__update_plot()

    @QtCore.Slot()
    def __check_for_plot_update(self):
        """
        Check that whether the plot should be updated.
        """
        _dt = time.time() - self._config["plot_last_update"]
        if _dt > self._config["plot_update_time"] and self._config["frame_active"]:
            self._config["plot_last_update"] = time.time()
            self.__update_plot()

    def __update_plot(self):
        """
        Update the plot.

        This method will get the latest image from the DirectorySpyApp and
        update the plot.
        """
        if (not self._config["plot_active"]) or self._app.image is None:
            return
        _fname = self._app.filename
        _title = _fname + self._app.image_metadata
        self._widgets["plot"].setGraphTitle(_title)
        self._widgets["plot"].addImage(self._app.image, replace=True, copy=False)
        self._widgets["plot"].setGraphYLabel("pixel")
        self._widgets["plot"].setGraphXLabel("pixel")

    @QtCore.Slot(int)
    def frame_activated(self, index: int):
        """
        Received a signal that a new frame has been selected.

        This method checks whether the selected frame is the current class
        and if yes, it will call some updates.

        Parameters
        ----------
        index : int
            The index of the newly activated frame.
        """
        super().frame_activated(index)
        if index == self.frame_index:
            self.__update_det_mask_visibility()
            self.__update_bg_widget_visibility()
            self.__check_for_plot_update()
        self._config["frame_active"] = index == self.frame_index

    def __set_proc_widget_enabled_for_running(self, running: bool):
        """
        Set the visibility of all widgets which need to be updated for/after
        procesing

        Parameters
        ----------
        running : bool
            Flag whether the AppRunner is running and widgets shall be shown
            accordingly or not.
        """
        self._widgets["but_once"].setEnabled(not running)
        self._widgets["but_exec"].setEnabled(not running)
        self._widgets["but_stop"].setEnabled(running)
