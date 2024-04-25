# This file is part of pydidas
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
Module with the Hdf5DatasetSelector widget which allows to select a dataset
from a Hdf5 file and to browse through its data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Hdf5DatasetSelector"]


from functools import partial
from pathlib import Path

import h5py
from qtpy import QtCore, QtWidgets
from silx.gui.widgets.FrameBrowser import HorizontalSliderWithBrowser

from ...core import PydidasGuiError
from ...core.constants import ALIGN_TOP_RIGHT, HDF5_EXTENSIONS, QT_COMBO_BOX_SIZE_POLICY
from ...core.utils import (
    apply_qt_properties,
    get_extension,
    get_hdf5_populated_dataset_keys,
)
from ..factory import CreateWidgetsMixIn
from ..utilities import get_max_pixel_width_of_entries
from .common_selection import register_plot_widget_method


DEFAULT_FILTERS = {
    "/entry/instrument/detector/detectorSpecific/": '"detectorSpecific"\nkeys (Eiger detector)'
}


class Hdf5DatasetSelector(QtWidgets.QWidget, CreateWidgetsMixIn):
    """
    A compound widget to select datasets in Hdf5 files.

    The Hdf5DatasetSelector is a compound widget which allows to select
    a hdf5 dataset key and the frame number. By convention, the first
    dimension of an n-dimensional (n >= 3) dataset is the frame number. Any
    2-dimensional datasets will be interpreted as single frames.

    Parameters
    ----------
    plot_widget : Union[QWidget, None], optional
        A widget for a full view. It can also be registered later using
        the  *register_plot_widget* method. The default is None.
    dataset_key_filters : Union[dict, None], optional
        A dictionary with dataset keys to be filtered from the list
        of displayed datasets. Entries must be in the format
        {<Key to filter>: <Descriptive text for checkbox>}.
        The default is None.
    **kwargs : dict
        Any additional keyword arguments. See below for supported arguments.
    **QtAttribute : depends on the attribute
        Any Qt attributes which are supported by the generic QWidget. Use the
        Qt attribute name with a lowercase first character. Examples are
        ``fixedWidth``, ``fixedHeight``.
    """

    new_frame_signal = QtCore.Signal(object)
    register_plot_widget = register_plot_widget_method

    def __init__(self, plot_widget=None, dataset_key_filters=None, **kwargs):
        QtWidgets.QWidget.__init__(self, kwargs.pop("parent", None))
        CreateWidgetsMixIn.__init__(self)
        apply_qt_properties(self, **kwargs)

        self._config = {
            "activeDsetFilters": [],
            "currentDset": None,
            "current_filename": None,
            "currentIndex": None,
            "dsetFilters": (
                dataset_key_filters
                if dataset_key_filters is not None
                else DEFAULT_FILTERS
            ),
        }
        self.flags = {"slotActive": False, "autoUpdate": True}
        self.show_image_method = None
        if plot_widget is not None:
            self.register_plot_widget(plot_widget)
        self._frame = None
        self.__create_widgets_and_layout()
        self.__connect_slots()

    def __create_widgets_and_layout(self):
        """
        Create all required widgets and the layout.

        This private method will create all the required and widgets and
        the layout.
        """
        _layout = QtWidgets.QGridLayout()
        _layout.setHorizontalSpacing(15)
        self.setLayout(_layout)

        # create checkboxes and links for all filter keys:
        _w_filter_keys = []
        for key, text in self._config["dsetFilters"].items():
            _widget = QtWidgets.QCheckBox(f"Ignore {text}")
            _widget.setChecked(False)
            _widget.stateChanged.connect(partial(self._toggle_filter_key, _widget, key))
            _w_filter_keys.append(_widget)
        for i, widget in enumerate(_w_filter_keys):
            _layout.addWidget(widget, i // 2, i % 2, 1, 2)

        # Determine the layout row offset for the other widgets based on
        # the number of filter key checkboxes:
        _row_offset = len(_w_filter_keys) // 2 + len(_w_filter_keys) % 2

        self.create_label(None, "Min. dataset\nsize: ", gridPos=(_row_offset, 0, 1, 1))
        self.create_label(
            None, "Min. dataset\ndimensions: ", gridPos=(_row_offset, 3, 1, 1)
        )
        self.create_label(
            None, "Filtered datasets: ", gridPos=(1 + _row_offset, 0, 1, 1)
        )
        self.create_spin_box(
            "min_datasize",
            gridPos=(_row_offset, 1, 1, 1),
            range=(0, int(1e9)),
            value=50,
        )
        self.create_spin_box(
            "min_datadim",
            gridPos=(_row_offset, 4, 1, 1),
            range=(0, 3),
            value=2,
        )
        self.create_combo_box(
            "select_dataset",
            gridPos=(1 + _row_offset, 1, 1, 4),
            minimumContentsLength=25,
            sizeAdjustPolicy=QT_COMBO_BOX_SIZE_POLICY,
        )
        self.add_any_widget(
            "frame_browser",
            HorizontalSliderWithBrowser(),
            gridPos=(2 + _row_offset, 0, 1, 5),
        )
        self.create_button(
            "but_view",
            "Show full frame",
            alignment=ALIGN_TOP_RIGHT,
            gridPos=(3 + _row_offset, 3, 1, 2),
            font_metric_width_factor=30,
        )
        self.create_check_box(
            "auto_update",
            "Auto update",
            checked=True,
            gridPos=(3 + _row_offset, 0, 1, 2),
            font_metric_width_factor=30,
        )
        self.setVisible(False)

    def __connect_slots(self):
        """
        Connect all required widget slots.

        Filter keys are set up dynamically along with their checkbox widgets.
        """
        self._widgets["min_datasize"].valueChanged.connect(self.__populate_dataset_list)
        self._widgets["min_datadim"].valueChanged.connect(self.__populate_dataset_list)
        self._widgets["select_dataset"].currentTextChanged.connect(
            self.__select_dataset
        )
        self._widgets["frame_browser"].valueChanged.connect(self._index_changed)
        self._widgets["but_view"].clicked.connect(self.click_view_button)
        self._widgets["auto_update"].clicked.connect(self._toggle_auto_update)

    def __populate_dataset_list(self):
        """
        Populate the dateset selection with a filtered list of datasets.

        This method reads the structure of the hdf5 file and filters the
        list of datasets according to the selected criteria. The filtered list
        is used to populate the selection drop-down menu.
        """
        _dset_filter_min_size = self._widgets["min_datasize"].value()
        _dset_filter_min_dim = self._widgets["min_datadim"].value()
        _datasets = get_hdf5_populated_dataset_keys(
            self._config["current_filename"],
            min_size=_dset_filter_min_size,
            min_dim=_dset_filter_min_dim,
            ignore_keys=self._config["activeDsetFilters"],
        )
        _combo = self._widgets["select_dataset"]
        with QtCore.QSignalBlocker(self._widgets["select_dataset"]):
            self._widgets["select_dataset"].clear()
            self._widgets["select_dataset"].addItems(_datasets)
        if len(_datasets) > 0:
            _items = [_combo.itemText(i) for i in range(_combo.count())]
            _combo.view().setMinimumWidth(get_max_pixel_width_of_entries(_items) + 50)
            self.__select_dataset()
        else:
            self._widgets["but_view"].setEnabled(False)

    def __select_dataset(self):
        """
        Select a dataset from the drop-down list.

        This internal method is called by the Qt event system if the QComBoBox
        text has changed to notify the main program that the user has selected
        a different dataset to be visualized. This method also updates the
        accepted frame range for the sliders.
        """
        _dset = self._widgets["select_dataset"].currentText()
        with h5py.File(self._config["current_filename"], "r") as _file:
            _shape = _file[_dset].shape
        n_frames = _shape[0] if len(_shape) >= 3 else 1
        self._widgets["frame_browser"].setRange(0, n_frames - 1)
        self._config["currentIndex"] = 0
        self._widgets["but_view"].setEnabled(True)
        self.__update()

    def __update(self, new_frame: bool = False):
        """
        Propagate an update to any consumers.

        This method will read a new frame from the file if any consumers
        demand it (consumers must activate the signal slot or the automatic
        update). The new frame will be passed to any active view/preview
        widgets and a signal emitted if the slot is active.

        Parameters
        ----------
        new_frame : bool
            A flag to tell this method to process a new frame, e.g. after changing
            the dataset.
        """
        if self.flags["autoUpdate"] or self.flags["slotActive"] or new_frame:
            self.__get_frame()
            if self._frame is None:
                return
        if self.flags["slotActive"]:
            self.new_frame_signal.emit(self._frame)
        if self.flags["autoUpdate"] and self._widgets["plot"] is not None:
            self.show_image_method(self._frame, legend="pydidas image")

    def __get_frame(self):
        """
        Get and store a frame.

        This internal method reads an image frame from the hdf5 dataset and
        stores it internally for further processing (passing to other widgets
        / signals)
        """
        _dset = self._widgets["select_dataset"].currentText()
        if _dset == "":
            self._frame = None
        with h5py.File(self._config["current_filename"], "r") as _file:
            _dset = _file[_dset]
            _ndim = len(_dset.shape)
            if _ndim >= 3:
                self._frame = _dset[self._config["currentIndex"]]
            elif _ndim == 2:
                self._frame = _dset[...]

    def _toggle_filter_key(self, widget: QtWidgets.QWidget, key: str):
        """
        Add or remove the filter key from the active dataset key filters.

        This method will add or remove the <key> which is associated with the
        checkbox widget <widget> from the active dataset filters.
        Note: This method should never be called by the user, but it is
        connected to the checkboxes which activate or deactivate the respective
        filters.

        Parameters
        ----------
        widget : QWidget
            The checkbox widget which is associated with enabling/disabling
            the filter key.
        key : str
            The dataset filter string.
        """
        if widget.isChecked() and key not in self._config["activeDsetFilters"]:
            self._config["activeDsetFilters"].append(key)
        if not widget.isChecked() and key in self._config["activeDsetFilters"]:
            self._config["activeDsetFilters"].remove(key)
        self.__populate_dataset_list()

    def _toggle_auto_update(self):
        """
        Toggle automatic updates based on the state of the checkbox widget.
        """
        self.flags["autoUpdate"] = self._widgets["auto_update"].isChecked()

    def enable_signal_slot(self, enable: bool):
        """
        Toggle the signal slot to emit the selected frame as signal for other
        widgets.

        Parameters
        ----------
        enable : bool
            Flag to enable the signal slot. If True, a signal is emitted every
            time a new frame is selected. If False, the signal slot is not
            used.
        """
        self.flags["slotActive"] = enable

    @QtCore.Slot(str)
    def new_filename(self, name: str):
        """
        Process the new filename.

        If the new filename has a suffix associated with hdf5 files,
        show the widget.

        Parameters
        ----------
        name : str
            The full file system path to the new file.
        """
        _filename = Path(name)
        if not _filename.is_file():
            return
        _is_hdf5 = get_extension(_filename) in HDF5_EXTENSIONS
        self.setVisible(_is_hdf5)
        if _is_hdf5:
            self._config["current_filename"] = name
            self.__populate_dataset_list()
            self.__update(True)

    def _index_changed(self, index: int):
        """
        Store the new index from the frame selector.

        This method is connected to the frame selector (slider/field) and
        calls for an update of the frame if the index has changed.

        Parameters
        ----------
        index : int
            The index in the image dataset.
        """
        self._config["currentIndex"] = index
        self.__update(True)

    def click_view_button(self):
        """
        Process clicking the view button.

        This method is connected to the clicked event of the View button.
        """
        if self._frame is None or not self.flags["autoUpdate"]:
            self.__get_frame()
        if not isinstance(self._widgets["plot"], QtWidgets.QWidget):
            raise PydidasGuiError("The reference is not a widget")
        self.show_image_method(self._frame, legend="pydidas_image")
