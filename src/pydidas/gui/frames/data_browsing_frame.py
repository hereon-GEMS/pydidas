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
Module with the DataBrowsingFrame which is used to browse through the filesystem in a
dedicated filesystem tree and show file data in a view window.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DataBrowsingFrame"]


from pathlib import Path
from typing import Any

import h5py
from qtpy import QtCore
from silx.gui.hdf5 import H5Node
from silx.gui.hdf5.Hdf5Item import Hdf5Item
from silx.gui.hdf5.Hdf5Node import Hdf5Node

from pydidas.core import Dataset, Parameter, ParameterCollection
from pydidas.core.constants import (
    ALIGN_TOP_RIGHT,
)
from pydidas.core.exceptions import FileReadError
from pydidas.core.utils import (
    CatchFileErrors,
    formatted_str_repr_of_dict,
    get_extension,
    get_hdf5_metadata,
)
from pydidas.core.utils.associated_file_mixin import AssociatedFileMixin
from pydidas.data_io import IoManager, import_data, read_metadata
from pydidas.gui.frames.builders.data_browsing_frame_builder import (
    DATA_BROWSING_FRAME_BUILD_CONFIG,
    create_splitter,
)
from pydidas.widgets.framework import BaseFrame, PydidasWindow
from pydidas.widgets.misc import ReadOnlyTextWidget
from pydidas.widgets.windows import Hdf5BrowserWindow
from pydidas_qtcore import PydidasQApplication


class DataBrowsingFrame(BaseFrame, AssociatedFileMixin):
    """
    A class to browse the filesystem tree and display data.

    The DataBrowsingFrame is frame with a directory explorer
    and a main data visualization window. Its main purpose is to browse
    through datasets.
    """

    menu_icon = "pydidas::frame_icon_data_browsing"
    menu_title = "Data browsing"
    menu_entry = "Data browsing"
    default_params = ParameterCollection(
        Parameter(
            "xcol",
            int,
            None,
            name="[ASCII] Use data column as x values:",
            allow_None=True,
            choices=[None],
        )
    )
    params_not_to_restore = ["xcol"]

    def __init__(self, **kwargs: Any):
        BaseFrame.__init__(self, **kwargs)
        AssociatedFileMixin.__init__(self, **kwargs)
        self.__qtapp = PydidasQApplication.instance()
        self.__supported_extensions = set(IoManager.registry_import.keys())
        self.__open_file = None
        self.__hdf5node = Hdf5Node()
        self.__browser_window = None
        self.__metadata_window = None
        self.set_default_params()

    def connect_signals(self):
        """
        Connect all required signals and slots between widgets and class
        methods.
        """
        self._widgets["explorer"].sig_new_file_selected.connect(self.__file_selected)
        self.param_widgets["xcol"].sig_new_value.connect(self.__display_ascii_data)
        self._widgets["hdf5_dataset_selector"].sig_new_dataset_selected.connect(
            self.__display_hdf5_dataset
        )
        self._widgets["configure_binary_decoding"].sig_new_binary_config.connect(
            self.__display_binary_data
        )
        self._widgets["hdf5_dataset_selector"].sig_request_hdf5_browser.connect(
            self.__inspect_hdf5_tree
        )
        self._widgets["button_ascii_metadata"].clicked.connect(self.__display_metadata)

    def build_frame(self):
        """
        Build the frame and populate it with widgets.
        """
        for _method, _args, _kwargs in DATA_BROWSING_FRAME_BUILD_CONFIG:
            _widget_creation_method = getattr(self, _method)
            _widget_creation_method(*_args, **_kwargs)
        self.add_any_widget(
            "splitter",
            create_splitter(
                self._widgets["browser"],
                self._widgets["viewer_and_filename"],
                self.width(),
            ),
        )
        _viewer_layout = self._widgets["viewer_and_filename"].layout()
        _viewer_layout.setRowStretch(_viewer_layout.rowCount() - 1, 1)

    @QtCore.Slot(int)
    def frame_activated(self, index: int):
        """
        Received signal that frame has been activated.

        This method is called when this frame becomes activated by the
        central widget. By default, this method will perform no actions.
        If specific frames require any actions, they will need to overwrite
        this method.

        Parameters
        ----------
        index : int
            The index of the activated frame.
        """
        BaseFrame.frame_activated(self, index)
        if index != self.frame_index:
            for _window in (self.__browser_window, self.__metadata_window):
                if _window is not None and _window.isVisible():
                    _window.hide()

    @QtCore.Slot(str)
    def __file_selected(self, filename: str):
        """
        Open a file after sit has been selected in the DirectoryExplorer.

        Parameters
        ----------
        filename : str
            The full file name (including directory) of the selected file.
        """
        if self.current_filename == filename:
            return
        if get_extension(filename) not in self.__supported_extensions:
            return
        if self.__browser_window is not None:
            self.__browser_window.hide()
        if self.__metadata_window is not None:
            self.__metadata_window.hide()
        self.current_filename = filename
        self._widgets["viewer"].set_data(None)
        self._widgets["filename"].setText(self.current_filename)
        self._widgets["ascii_widgets"].setVisible(self.ascii_file)
        self._widgets["hdf5_dataset_selector"].setVisible(self.hdf5_file)
        self._widgets["configure_binary_decoding"].set_new_filename(filename)
        if self.ascii_file:
            self.__open_ascii_file()
        elif self.hdf5_file:
            self.__open_hdf5_file()
        elif self.generic_file:
            _data = import_data(filename)
            self.__display_dataset(_data)

    def __open_hdf5_file(self):
        """Process the input file and check whether it is a hdf5 file."""
        if self.__open_file is not None:
            self.__open_file.close()
            self.__open_file = None
        with (
            CatchFileErrors(
                self.current_filename, KeyError, raise_file_read_error=False
            ) as catcher,
            QtCore.QSignalBlocker(self._widgets["hdf5_dataset_selector"]),
        ):
            self.__open_file = h5py.File(self.current_filename, mode="r")
            self._widgets["hdf5_dataset_selector"].new_filename(self.current_filename)
            self.__display_hdf5_dataset(self._widgets["hdf5_dataset_selector"].dataset)
        if catcher.raised_exception:
            try:
                self.__open_file.close()
            except (OSError, AttributeError):
                pass
            self.__open_file = None
            self._widgets["hdf5_dataset_selector"].clear()
            self._widgets["filename"].setText("")
            self.current_filename = ""
            raise FileReadError(catcher.exception_message)

    def __display_dataset(
        self, data: Dataset | H5Node, h5node: H5Node = None, title: str | None = None
    ):
        """
        Display the data in the viewer widget.

        Parameters
        ----------
        data : Dataset | H5Node
            The data to display.
        h5node : H5Node | None
            The H5Node if the data is from a hdf5 file.
        title : str | None
            The title to display in the viewer window.
        """
        title = Path(self.current_filename).name if title is None else title
        self._widgets["viewer"].set_data(data, title=title, h5node=h5node)

    @QtCore.Slot(str)
    def __display_hdf5_dataset(self, dataset: str):
        """
        Display the selected dataset in the viewer widget.

        Parameters
        ----------
        dataset : str
            The key of the dataset to display.
        """
        if dataset == "":
            self._widgets["viewer"].set_data(None)
            return
        _max_direct_import_size = 1_048_576 * self.q_settings_get(
            "global/data_buffer_hdf5_max_size", dtype=int
        )
        _nbytes = get_hdf5_metadata(self.current_filename, "nbytes", dset=dataset)
        _fpath = self.current_filepath.name
        try:
            _item = Hdf5Item(
                text=dataset,
                obj=self.__open_file[dataset],
                parent=self.__hdf5node,
                openedPath=self.current_filename,
            )
            _h5node = H5Node(_item)
        except KeyError:
            self._widgets["viewer"].set_data(None)
            raise FileReadError(
                f"Dataset `{dataset}` could not be read from the file `{_fpath}`."
            )
        if _nbytes <= _max_direct_import_size:
            _data = import_data(self.current_filename, dataset=dataset)
        else:
            _data = _h5node
        self.__display_dataset(_data, h5node=_h5node, title=_fpath + "::" + dataset)

    @QtCore.Slot(dict)
    def __display_binary_data(self, kwargs: dict[str, Any]):
        """
        Display the raw binary data in the viewer widget.

        Parameters
        ----------
        kwargs : dict
            The kwargs required for decoding the raw data.
        """
        _data = import_data(self.current_filename, **kwargs)
        self.__display_dataset(_data)

    @QtCore.Slot()
    def __inspect_hdf5_tree(self):
        """
        Inspect the hdf5 tree structure of the current file.

        This method will open a new window with the hdf5 tree structure to display.
        """
        if self.__browser_window is None:
            self.__browser_window = Hdf5BrowserWindow()
        self.__browser_window.open_file(self.current_filename)

    def __open_ascii_file(self):
        """Import ASCII raw data."""
        if not self.current_filename_is_valid:
            return
        _ascii_data = import_data(self.current_filename, x_column=False)
        _new_choices = [None]
        _curr_choice = None
        if _ascii_data.ndim > 1:
            _curr_choice = self.get_param_value("xcol")
            _new_choices = _new_choices + list(range(_ascii_data.shape[1]))
            if _curr_choice not in _new_choices:
                _curr_choice = None
            if _ascii_data.shape[1] == 2:
                _curr_choice = 0
        self.set_param_value_and_choices("xcol", _curr_choice, _new_choices)
        self.param_composite_widgets["xcol"].setVisible(_ascii_data.ndim > 1)
        self.param_widgets["xcol"].update_choices(
            _new_choices, selection=_curr_choice, emit_signal=False
        )
        self.__display_ascii_data(_curr_choice)

    def __display_ascii_data(self, use_x_col: str):
        """
        Display the ASCII data with the new x-column setting.

        Parameters
        ----------
        use_x_col : str
            The new value for the xcol parameter. This can be "None" or an integer.
        """
        use_x_col = None if use_x_col in [None, "None"] else int(use_x_col)
        _data = import_data(
            self.current_filename,
            x_column=use_x_col is not None,
            x_column_index=use_x_col,
        )
        self.__display_dataset(_data)

    def __display_metadata(self):
        """
        Display the metadata of the current file in a message box.
        """
        if (
            not self.current_filename_is_valid
            or not self._widgets["viewer"].data_is_set
        ):
            return
        _metadata = read_metadata(self.current_filename)
        _str_repr = formatted_str_repr_of_dict(_metadata)
        if self.__metadata_window is None:
            self.__create_metadata_window()
        self.__metadata_window._widgets["text_box"].setText(
            _str_repr, title=self.current_filename
        )
        self.__metadata_window.show()

    def __create_metadata_window(self):
        """
        Create the metadata window if it does not yet exist.
        """
        self.__metadata_window = PydidasWindow()
        self.__metadata_window.create_any_widget(
            "text_box",
            ReadOnlyTextWidget,
            font_metric_width_factor=120,
            line_wrap_width=120,
            gridPos=(0, 0, 1, 2),
            minimumHeight=600,
        )
        self.__metadata_window.create_button(
            "button_close",
            "Close window",
            alignment=ALIGN_TOP_RIGHT,
            gridPos=(-1, 1, 1, 2),
            font_metric_width_factor=20,
        )
        self.__metadata_window._widgets["button_close"].clicked.connect(
            self.__metadata_window.hide
        )
        self.__metadata_window.setWindowTitle("Metadata")
