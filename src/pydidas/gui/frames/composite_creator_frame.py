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
Module with the CompositeCreatorFrame which allows to combine images to
mosaics.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["CompositeCreatorFrame"]


import os
import time
from collections.abc import Iterable
from functools import partial
from pathlib import Path
from typing import Literal, Union

import numpy as np
from qtpy import QtCore, QtWidgets

from pydidas.apps import CompositeCreatorApp
from pydidas.core import Parameter, UserConfigError, get_generic_parameter
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import (
    LOGGING_LEVEL,
    get_extension,
    get_hdf5_populated_dataset_keys,
    pydidas_logger,
)
from pydidas.data_io import IoManager
from pydidas.gui.frames.builders import CompositeCreatorFrameBuilder
from pydidas.gui.mixins import SilxPlotWindowMixIn
from pydidas.multiprocessing import AppRunner
from pydidas.widgets import dialogues
from pydidas.widgets.framework import BaseFrameWithApp


logger = pydidas_logger(LOGGING_LEVEL)


class CompositeCreatorFrame(BaseFrameWithApp, SilxPlotWindowMixIn):
    """
    Frame with Parameter setup for the CompositeCreatorApp and result
    visualization.
    """

    menu_icon = "mdi::view-comfy"
    menu_title = "Composite image creator"
    menu_entry = "Composite image creator"

    def __init__(self, **kwargs: dict):
        BaseFrameWithApp.__init__(self, **kwargs)
        SilxPlotWindowMixIn.__init__(self)

        self._app = CompositeCreatorApp()
        self._filelist = self._app._filelist
        self._image_metadata = self._app._image_metadata
        self._app._config.update(self._config)
        self._config = self._app._config
        self._config["input_configured"] = False
        self._config["bg_configured"] = False
        self._config["frame_active"] = False
        self._update_timer = 0
        self._create_param_collection()

    def _create_param_collection(self):
        """
        Create the local ParameterCollection which is an updated
        CompositeCreatorApp collection.
        """
        for param in self._app.params.values():
            self.add_param(param)
            if param.refkey == "hdf5_key":
                self.add_param(get_generic_parameter("hdf5_dataset_shape"))
            if param.refkey == "file_stepping":
                self.add_param(get_generic_parameter("n_files"))
            if param.refkey == "hdf5_stepping":
                self.add_param(get_generic_parameter("raw_image_shape"))
                self.add_param(get_generic_parameter("images_per_file"))
            if param.refkey == "binning":
                self.add_param(
                    Parameter(
                        "n_total",
                        int,
                        0,
                        name="Total number of images",
                        tooltip="The total number of images.",
                    )
                )

    def build_frame(self):
        """
        Populate the frame with widgets.
        """
        CompositeCreatorFrameBuilder.build_frame(self)

    def connect_signals(self):
        """
        Connect the required signals between widgets and methods.
        """
        self._widgets["but_clear"].clicked.connect(
            partial(self.__clear_entries, "all", True)
        )
        self._widgets["but_exec"].clicked.connect(self._run_app)
        self._widgets["but_save"].clicked.connect(self.__save_composite)
        self._widgets["but_show"].clicked.connect(self.__show_composite)
        self._widgets["but_abort"].clicked.connect(self.__abort_comp_creation)

        for _key in ["last_file", "file_stepping"]:
            self.param_widgets[_key].io_edited.connect(self.__update_file_selection)
        for _key in [
            "hdf5_slicing_axis",
            "hdf5_first_image_num",
            "hdf5_last_image_num",
            "hdf5_stepping",
        ]:
            self.param_widgets[_key].io_edited.connect(self.__update_n_image)

        self.param_widgets["use_roi"].io_edited.connect(self.__toggle_roi_selection)
        self.param_widgets["first_file"].io_edited.connect(self.__selected_first_file)
        self.param_widgets["hdf5_key"].io_edited.connect(self.__selected_hdf5_key)
        self.param_widgets["use_bg_file"].io_edited.connect(
            self.__toggle_bg_file_selection
        )
        self.param_widgets["bg_file"].io_edited.connect(self.__selected_bg_file)
        self.param_widgets["bg_hdf5_key"].io_edited.connect(self.__selected_bg_hdf5_key)
        self.param_widgets["use_thresholds"].io_edited.connect(
            self.__toggle_use_threshold
        )
        self.param_widgets["use_detector_mask"].io_edited.connect(
            self.__toggle_use_det_mask
        )
        # disconnect the generic param update connections and re-route to
        # composite update method
        self.param_widgets["composite_nx"].io_edited.disconnect()
        self.param_widgets["composite_nx"].io_edited.connect(
            partial(self.__update_composite_dim, "x")
        )
        self.param_widgets["composite_ny"].io_edited.disconnect()
        self.param_widgets["composite_ny"].io_edited.connect(
            partial(self.__update_composite_dim, "y")
        )
        self._app.updated_composite.connect(self.__received_composite_update)
        _app = QtWidgets.QApplication.instance()
        if hasattr(_app, "sig_exit_pydidas"):
            _app.sig_exit_pydidas.connect(self.deleteLater)

        self.setup_initial_state()

    @QtCore.Slot()
    def __received_composite_update(self):
        """
        Slot to be called on an update signal from the Composite.
        """
        if (
            time.time() - self._config["last_update"] >= 2
            and self._config["frame_active"]
        ):
            self.__show_composite()
            self._config["last_update"] = time.time()

    def __show_composite(self):
        """
        Show the composite image in the Viewer.
        """
        self.show_image_in_plot(self._app.composite)

    def setup_initial_state(self):
        """
        Set up the initial state for the widgets.
        """
        self.__toggle_roi_selection(False)
        self.__toggle_bg_file_selection(False)
        self.__toggle_use_threshold(False)
        self.__toggle_use_det_mask(False)

    def restore_state(self, state: dict):
        """
        Restore the frame's state from stored information.

        The BaseFrameWithApp implementation will update the associated App
        and then call the BaseFrame's method.

        Parameters
        ----------
        state : dict
            A dictionary with 'params', 'app' and 'visibility' keys and the
            respective information for all.
        """
        BaseFrameWithApp.restore_state(self, state)
        self._config["bg_configured"] = state["config"]["bg_configured"]
        self._config["input_configured"] = state["config"]["input_configured"]
        BaseFrameWithApp.frame_activated(self, self.frame_index)
        if self.get_param_value("first_file") != Path():
            self._filelist.update()
            self._image_metadata.filename = self.get_param_value("first_file")
            self._image_metadata.update()
            self.__update_n_image()
        self.__update_widgets_after_selecting_first_file()
        self.__toggle_use_threshold(self.get_param_value("use_thresholds"))
        self.__toggle_use_det_mask(self.get_param_value("use_detector_mask"))
        self.__toggle_roi_selection(self.get_param_value("use_roi"))
        self.__toggle_bg_file_selection(self.get_param_value("use_bg_file"))

    def export_state(self) -> tuple[int, dict]:
        """
        Export the state of the Frame for saving.

        This method adds an export for the frame's app.

        Returns
        -------
        frame_index : int
            The frame index which can be used as key for referencing the state.
        information : dict
            A dictionary with all the information required to export the
            frame's state.
        """
        _index, _state = BaseFrameWithApp.export_state(self)
        _state["config"] = {
            "bg_configured": self._config["bg_configured"],
            "input_configured": self._config["input_configured"],
        }
        return _index, _state

    def frame_activated(self, index: int):
        """
        Overload the generic frame_activated method.

        Parameters
        ----------
        index : int
            The frame index.
        """
        BaseFrameWithApp.frame_activated(self, index)
        self._config["frame_active"] = index == self.frame_index

    def _run_app_serial(self):
        """
        Serial implementation of the execution method.
        """
        self._prepare_app_run()
        self._prepare_plot_params()
        self._app.run()
        self._widgets["but_show"].setEnabled(True)
        self._widgets["but_save"].setEnabled(True)
        self.set_status("Finished composite image creation.")

    def _prepare_app_run(self):
        """
        Do preparations for running the CompositeCreatorApp.

        This method sets the required attributes both for serial and
        parallel running of the app.
        """
        self._config["plot_scale"] = None
        self._config["plot_origin"] = None
        self._config["plot_aspect"] = None
        self._image_metadata.update_final_image()
        self.set_status("Started composite image creation.")

    def _prepare_plot_params(self):
        _shape = self._app.composite.shape
        _border = self.q_settings_get("user/mosaic_border_width", int)
        _nx = self.get_param_value("composite_nx")
        _ny = self.get_param_value("composite_ny")
        _rel_border_width_x = 0.5 * _border / (_shape[1] + _border)
        _rel_border_width_y = 0.5 * _border / (_shape[0] + _border)
        _range_x = (0.5 + _rel_border_width_x, _nx + 0.5 - _rel_border_width_x)
        _range_y = (0.5 + _rel_border_width_y, _ny + 0.5 - _rel_border_width_y)
        self.setup_plot_params(_shape, _range_x, _range_y)

    def _run_app(self):
        """
        Parallel implementation of the execution method.
        """
        self._prepare_app_run()
        self._app.multiprocessing_pre_run()
        if self._app._det_mask is not None:
            _shape = tuple(
                [
                    _s // self.get_param_value("binning")
                    for _s in self.get_param_value("raw_image_shape")
                ]
            )
            if _shape != self._app._det_mask.shape:
                raise UserConfigError(
                    "The use of the global detector mask has been selected but the "
                    "detector mask size does not match the image data size."
                )
        self._prepare_plot_params()
        self._config["last_update"] = time.time()
        self._widgets["but_exec"].setEnabled(False)
        self._widgets["but_abort"].setVisible(True)
        self._widgets["progress"].setVisible(True)
        self._widgets["progress"].setValue(0)
        self._runner = AppRunner(self._app)
        self._runner.sig_final_app_state.connect(self._set_app)
        self._runner.sig_progress.connect(self._apprunner_update_progress)
        self._runner.finished.connect(self._apprunner_finished)
        logger.debug("Starting AppRunner")
        self._runner.start()

    @QtCore.Slot()
    def _apprunner_finished(self):
        """
        Clean up after AppRunner is done.
        """
        logger.debug("finishing AppRunner")
        if self._runner is not None:
            self._runner.exit()
        self._widgets["but_exec"].setEnabled(True)
        self._widgets["but_show"].setEnabled(True)
        self._widgets["but_save"].setEnabled(True)
        self._widgets["but_abort"].setVisible(False)
        self._widgets["progress"].setVisible(False)
        self.set_status("Finished composite image creation.")
        time.sleep(0.05)
        self._runner = None
        logger.debug("removed AppRunner")
        self.__show_composite()

    def __save_composite(self):
        """
        Save the composite image.
        """
        fname = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Name of file",
            None,
            IoManager.get_string_of_formats("export"),
        )[0]
        if fname not in [None, ""]:
            _cmap = self._widgets["plot_window"].getActiveImage().getColormap()
            _data_range = _cmap.getVRange()
            self._app.export_image(fname, data_range=_data_range, overwrite=True)

    @QtCore.Slot(str)
    def __selected_first_file(self, fname: Union[Path, str]):
        """
        Perform required actions after selecting the first image file.

        This method checks whether a hdf5 file has been selected and shows/
        hides the required fields for selecting the dataset or the last file
        in case of a file series.
        If a hdf5 image file has been selected, this method also opens a
        pop-up for dataset selection.

        Parameters
        ----------
        fname : Union[Path, str]
            The filename of the first image file.
        """
        self.__clear_entries(
            [
                "last_file",
                "hdf5_key",
                "hdf5_slicing_axis",
                "hdf5_first_image_num",
                "hdf5_last_image_num",
                "hdf5_stepping",
                "file_stepping",
                "n_total",
                "composite_nx",
                "composite_ny",
            ]
        )
        if not self.__check_file(fname):
            return
        self.__update_widgets_after_selecting_first_file()
        self.__update_file_selection()
        self._image_metadata.filename = self.get_param_value("first_file")
        self.param_widgets["last_file"].update_io_directory(
            self.get_param_value("first_file")
        )
        if self.__check_if_hdf5_file():
            self._config["input_configured"] = False
            self.__popup_select_hdf5_key(fname)
        else:
            self._image_metadata.update()
            _shape = (
                self._image_metadata.raw_size_y,
                self._image_metadata.raw_size_x,
            )
            self.set_param_value_and_widget("raw_image_shape", _shape)
            self.set_param_value_and_widget("images_per_file", 1)
            self._config["input_configured"] = True
        _finalize_flag = self._config["input_configured"]
        self.__update_n_total()
        self.__finalize_selection(_finalize_flag)
        self.__check_exec_enable()

    def __check_file(self, fname: Union[Path, str]) -> bool:
        """
        Check whether the filename is valid for processing.

        Parameters
        ----------
        fname : Union[Path, str]
            The filename

        Returns
        -------
        bool
            The flag whether the file is valid.
        """
        if self.get_param_value("live_processing") or os.path.isfile(fname):
            return True
        if fname not in ["", "."]:
            dialogues.critical_warning(
                "File does not exist",
                f'The selected file\n\n"{fname}"\n\ndoes not exist.',
            )
            self.__clear_entries(["first_file"], hide=False)
        return False

    def __update_widgets_after_selecting_first_file(self):
        """
        Update widget visibility after selecting the first file based on the
        file format (hdf5 or not).
        """
        hdf5_flag = self.__check_if_hdf5_file()
        for _key in [
            "hdf5_key",
            "hdf5_slicing_axis",
            "hdf5_first_image_num",
            "hdf5_last_image_num",
            "hdf5_stepping",
            "hdf5_dataset_shape",
        ]:
            self.toggle_param_widget_visibility(_key, hdf5_flag)
        self.toggle_param_widget_visibility("last_file", True)
        self.toggle_param_widget_visibility("raw_image_shape", not hdf5_flag)

    def __check_if_hdf5_file(self) -> bool:
        """
        Check if the first file is a hdf5 file.

        Returns
        -------
        bool
            Flag whether a hdf5 file has been selected.
        """
        _ext = get_extension(self.get_param_value("first_file"))
        return _ext in HDF5_EXTENSIONS

    def __popup_select_hdf5_key(self, fname: Union[Path, str]):
        """
        Create a popup window which asks the user to select a dataset.

        Parameters
        ----------
        fname : Union[Path, str]
            The filename to the hdf5 data file.
        """
        dset = dialogues.Hdf5DatasetSelectionPopup(self, fname).get_dset()
        if dset is not None:
            self.set_param_value_and_widget("hdf5_key", dset)
            self.__selected_hdf5_key()
        else:
            self._config["input_configured"] = False
            self.__finalize_selection(False)
            self.set_param_value_and_widget("hdf5_key", "")
            self.__clear_entries(
                [
                    "images_per_file",
                    "n_total",
                    "hdf5_dataset_shape",
                    "hdf5_key",
                    "hdf5_slicing_axis",
                    "hdf5_first_image_num",
                    "hdf5_last_image_num",
                    "hdf5_stepping",
                ],
                False,
            )

    def __selected_bg_file(self, fname: Union[Path, str]):
        """
        Perform required actions after selecting background image file.

        This method resets the fields for hdf5 image key and image number
        and opens a pop-up for dataset selection if a hdf5 file has been
        selected.

        Parameters
        ----------
        fname : Union[Path, str]
            The filename of the background image file.
        """
        self.__clear_entries(["bg_hdf5_key", "bg_hdf5_frame"])
        hdf5_flag = get_extension(fname) in HDF5_EXTENSIONS
        self._config["bg_hdf5_images"] = hdf5_flag
        self._config["bg_configured"] = not hdf5_flag
        if hdf5_flag:
            dset = dialogues.Hdf5DatasetSelectionPopup(self, fname).get_dset()
            if dset is not None:
                self.set_param_value_and_widget("bg_hdf5_key", dset)
                self._config["bg_configured"] = True
        self.toggle_param_widget_visibility("bg_hdf5_key", hdf5_flag)
        self.toggle_param_widget_visibility("bg_hdf5_frame", hdf5_flag)
        self.__check_exec_enable()

    def __selected_hdf5_key(self):
        """
        Perform required actions after a hdf5 key has been selected.
        """
        try:
            self._image_metadata.update()
            self.set_param_value_and_widget(
                "hdf5_dataset_shape", self._image_metadata.hdf5_dset_shape
            )
            self.set_param_value_and_widget(
                "images_per_file", self._image_metadata.images_per_file
            )
            self._config["input_configured"] = True
        except UserConfigError:
            self.__clear_entries(
                ["hdf5_key", "hdf5_dataset_shape", "images_per_file"], False
            )
            self._config["input_configured"] = False
            raise
        self.__update_n_image()

    def __selected_bg_hdf5_key(self):
        """
        Check that the background image hdf5 file actually has the required
        key.
        """
        _fname = self.get_param_value("bg_file")
        _dset = self.get_param_value("bg_hdf5_key")
        if _dset in get_hdf5_populated_dataset_keys(_fname):
            _flag = True
        else:
            self.__clear_entries(["bg_hdf5_key"], hide=False)
            dialogues.critical_warning(
                "Dataset key error",
                (
                    f'The selected file\n\n"{_fname}"\n\ndoes not have the '
                    f'selected dataset\n\n"{_dset}"'
                ),
            )
            _flag = False
        self._config["bg_configured"] = _flag
        self.__check_exec_enable()

    def __reset_params(self, keys: Union[Literal["all"], Iterable[str], None] = None):
        """
        Reset parameters to their default values.

        Parameters
        ----------
        keys : Union[Literal["all"], Iterable[str], None], optional
            An iterable of keys which reference the Parameters. If 'all',
            all Parameters in the ParameterCollection will be reset to their
            default values. The default is 'all'.
        """
        keys = keys if keys is not None else []
        for _but in ["but_exec", "but_save", "but_show"]:
            self._widgets[_but].setEnabled(False)
        self._widgets["progress"].setVisible(False)
        self._widgets["plot_window"].setVisible(False)
        for _key in keys:
            self.set_param_value_and_widget(_key, self.params[_key].default)
        if "first_file" in keys:
            self._config["input_configured"] = False

    def __check_exec_enable(self):
        """
        Check whether the exec button should be enabled and enable/disable it.
        """
        _enable = False
        try:
            assert self._image_metadata.final_shape is not None
            if self.get_param_value("use_bg_file"):
                assert os.path.isfile(self.get_param_value("bg_file"))
                assert self._config["bg_configured"]
            _enable = True
        except (KeyError, AssertionError):
            pass
        finally:
            _flag = _enable and self._config["input_configured"]
            self._widgets["but_exec"].setEnabled(_flag)

    def __toggle_bg_file_selection(self, flag: bool):
        """
        Show or hide the detail for background image files.

        Parameters
        ----------
        flag : bool
            The show / hide boolean flag.
        """
        if isinstance(flag, str):
            flag = flag == "True"
        self.set_param_value("use_bg_file", flag)
        self.toggle_param_widget_visibility("bg_file", flag)
        _bg_ext = get_extension(self.get_param_value("bg_file"))
        if _bg_ext not in HDF5_EXTENSIONS:
            flag = False
        self.toggle_param_widget_visibility("bg_hdf5_key", flag)
        self.toggle_param_widget_visibility("bg_hdf5_frame", flag)
        self.__check_exec_enable()

    def __abort_comp_creation(self):
        """
        Abort the creation of the composite image.
        """
        self._runner.stop()
        self._runner._wait_for_processes_to_finish(2)
        self._apprunner_finished()

    def __toggle_roi_selection(self, flag: bool):
        """
        Show or hide the ROI selection.

        Parameters
        ----------
        flag : bool
            The flag with visibility information for the ROI selection.
        """
        if isinstance(flag, str):
            flag = flag == "True"
        self.set_param_value("use_roi", flag)
        for _key in ["roi_xlow", "roi_xhigh", "roi_ylow", "roi_yhigh"]:
            self.toggle_param_widget_visibility(_key, flag)

    def __toggle_use_threshold(self, flag: bool):
        """
        Show or hide the threshold selection based on the flag selection.

        Parameters
        ----------
        flag : bool
            The flag with visibility information for the threshold selection.
        """
        if isinstance(flag, str):
            flag = flag == "True"
        self.set_param_value("use_thresholds", flag)
        for _key in ["threshold_low", "threshold_high"]:
            self.toggle_param_widget_visibility(_key, flag)

    def __toggle_use_det_mask(self, flag: bool):
        """
        Show or hide the detector mask Parameters based on the flag selection.

        Parameters
        ----------
        flag : bool
            The flag with visibility information for the threshold selection.
        """
        if isinstance(flag, str):
            flag = flag == "True"
        self.set_param_value("use_detector_mask", flag)
        for _key in ["detector_mask_file", "detector_mask_val"]:
            self.toggle_param_widget_visibility(_key, flag)

    def __clear_entries(
        self, keys: Union[Literal["all"], Iterable[str]] = "all", hide: bool = True
    ):
        """
        Clear the Parameter entries and reset to default for selected keys.

        Parameters
        ----------
        keys : Union[Literal["all"], Iterable[str]], optional
            The keys for the Parameters to be reset. The default is 'all'.
        hide : bool, optional
            Flag for hiding the reset keys. The default is True.
        """
        keys = keys if keys != "all" else list(self.params.keys())
        self.__reset_params(keys)
        for _key in [
            "hdf5_key",
            "hdf5_slicing_axis",
            "hdf5_first_image_num",
            "hdf5_last_image_num",
            "last_file",
            "bg_hdf5_key",
            "bg_hdf5_frame",
            "bg_file",
        ]:
            if _key in keys:
                self.toggle_param_widget_visibility(_key, not hide)
        self.__check_exec_enable()

    def __update_n_image(self):
        """
        Update the number of images in the composite based on the input parameters.
        """
        if not self._config["input_configured"]:
            return
        self._image_metadata.update_input_data()
        _n_per_file = self._image_metadata.images_per_file
        self.set_param_value_and_widget("images_per_file", _n_per_file)
        self.__update_n_total()

    def __update_composite_dim(self, dim: Literal["x", "y"]):
        """
        Update the composite dimension counters upon a change in one of them.

        Parameters
        ----------
        dim : Union['x', 'y']
            The dimension which has changed.
        """
        _n_total = self.get_param_value("n_total")
        num1 = self.param_widgets[f"composite_n{dim}"].get_value()
        num2 = int(np.ceil(_n_total / abs(num1)))
        dim2 = "y" if dim == "x" else "x"
        self.set_param_value_and_widget(f"composite_n{dim2}", num2)
        self.set_param_value_and_widget(f"composite_n{dim}", abs(num1))
        if (num1 - 1) * num2 >= _n_total or num1 * (num2 - 1) >= _n_total:
            self.__update_composite_dim(dim2)

    def __update_file_selection(self):
        """
        Update the filelist based on the current selection.
        """
        try:
            self._filelist.update()
        except UserConfigError as _error:
            self.__clear_entries(["last_file"], hide=False)
            dialogues.critical_warning("Could not create filelist.", str(_error))
            return
        if not self._filelist.n_files > 0:
            dialogues.critical_warning(
                "Filelist is empty.",
                "The list of files is empty. Please verify the selection.",
            )
            return
        self.set_param_value_and_widget("n_files", self._filelist.n_files)
        self.__update_n_total()

    def __update_n_total(self):
        """
        Update the total number of selected images.
        """
        if not self._config["input_configured"]:
            return
        _n_total = self._image_metadata.images_per_file * self._filelist.n_files
        self.set_param_value_and_widget("n_total", _n_total)
        self.__update_composite_dim(self.get_param_value("composite_dir"))
        self.__check_exec_enable()

    def __finalize_selection(self, flag: bool):
        """
        Finalize input file selection.

        Parameters
        ----------
        flag : bool
            Flag whether to finalize or lock finalization.
        """
        for _key in ["file_stepping", "composite_nx", "composite_ny"]:
            self.toggle_param_widget_visibility(_key, flag)
        self._widgets["but_exec"].setEnabled(flag)
