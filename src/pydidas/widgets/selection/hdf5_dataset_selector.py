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
Module with the Hdf5DatasetSelector widget which allows to select a dataset
from a Hdf5 file and to browse through its data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Hdf5DatasetSelector"]


from functools import partial
from pathlib import Path

from qtpy import QtCore

from pydidas.core import Parameter
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import (
    get_extension,
    get_hdf5_populated_dataset_keys,
    update_child_qobject,
)
from pydidas.widgets.utilities import (
    get_max_pixel_width_of_entries,
    get_pyqt_icon_from_str,
)
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


DEFAULT_FILTERS = {
    "/entry/instrument/detector/detectorSpecific/": (
        '"detectorSpecific"\nkeys (Eiger detector)'
    ),
}
DATA_DIMENSION_PARAM = Parameter(
    "min_datadim",
    str,
    ">= 1",
    choices=["any", ">= 1", ">= 2", ">= 3", ">= 4"],
    name="Filter for dataset dimensions",
    tooltip="Minimum number of dimensions for a dataset to be displayed.",
)
DATASET_PARAM = Parameter(
    "dataset",
    str,
    "",
    choices=[""],
    name="Selected dataset",
    tooltip="The selected dataset to be displayed.",
)
EMPTY_WIDGET_COLS = {
    0: [],
    1: [1, 2],
    2: [2],
}


class Hdf5DatasetSelector(WidgetWithParameterCollection):
    """
    A compound widget to select datasets in Hdf5 files.

    The Hdf5DatasetSelector is a compound widget which allows to select
    a hdf5 dataset key and the frame number. By convention, the first
    dimension of an n-dimensional (n >= 3) dataset is the frame number. Any
    2-dimensional datasets will be interpreted as single frames.

    Parameters
    ----------
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

    sig_new_dataset_selected = QtCore.Signal(str)
    sig_request_hdf5_browser = QtCore.Signal()

    def __init__(self, dataset_key_filters=None, **kwargs):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.add_params(DATA_DIMENSION_PARAM.copy(), DATASET_PARAM.copy())

        self._config = {
            "activeDsetFilters": [],
            "current_dataset": "",
            "current_filename": "",
            "min_datadim": 1,
            "display_details": True,
            "dsetFilters": (
                dataset_key_filters
                if dataset_key_filters is not None
                else DEFAULT_FILTERS
            ),
        }
        self.__create_widgets()
        self.__connect_slots()
        self._toggle_details()

    def __create_widgets(self):
        """
        Create all required widgets.
        """
        update_child_qobject(self, "layout", horizontalSpacing=2)
        self.create_button(
            "button_inspect",
            "Inspect hdf5 tree structure",
            gridPos=(0, 2, 1, 1),
            icon="qt-std::SP_MessageBoxInformation",
        )
        for _index, (_key, _text) in enumerate(self._config["dsetFilters"].items()):
            self.create_check_box(
                f"check_filter_{_key}",
                f"Hide {_text}",
                checked=False,
                font_metric_height_factor=2,
                gridPos=(1 + _index // 3, _index % 3, 1, 1),
            )
            self._widgets[f"check_filter_{_key}"].stateChanged.connect(
                partial(self._toggle_filter_key, _key)
            )
        for _col in range(3):
            update_child_qobject(self, "layout", columnStretch=(_col, 10))
            if _col in EMPTY_WIDGET_COLS[len(self._config["dsetFilters"]) % 3]:
                self.create_empty_widget(
                    f"empty_{_index}",
                    gridPos=(1 + _index // 3, _col, 1, 1),
                    fixedHeight=5,
                )

        _row_offset = len(self._config["dsetFilters"]) // 2 + 2

        self.create_param_widget(
            self.get_param("min_datadim"), gridPos=(_row_offset, 0, 1, 1)
        )
        self.create_param_widget(
            self.get_param("dataset"),
            gridPos=(_row_offset + 1, 0, 1, 2),
            width_text=0.275,
            width_io=0.725,
        )
        self.create_button(
            "button_toggle_details",
            "Show detailed dataset selection options",
            clicked=self._toggle_details,
            icon="qt-std::SP_TitleBarUnshadeButton",
            gridPos=(_row_offset + 1, 2, 1, 1),
        )
        self.setVisible(False)

    def __connect_slots(self):
        """
        Connect all required widget slots.

        Filter keys are set up dynamically along with their checkbox widgets.
        """
        self.param_widgets["min_datadim"].io_edited.connect(self.__process_min_datadim)
        self.param_widgets["dataset"].io_edited.connect(self.__select_dataset)
        self._widgets["button_inspect"].clicked.connect(self.sig_request_hdf5_browser)

    @QtCore.Slot(str)
    def __process_min_datadim(self, value: str):
        """
        Process the minimum dataset dimension parameter.

        Parameters
        ----------
        value : str
            The new value of the minimum dataset dimension parameter.
        """
        self._config["min_datadim"] = 0 if value == "any" else int(value.split("=")[1])
        self.__populate_dataset_list()

    def __populate_dataset_list(self):
        """
        Populate the dateset selection with a filtered list of datasets.

        This method reads the structure of the hdf5 file and filters the
        list of datasets according to the selected criteria. The filtered list
        is used to populate the selection drop-down menu.
        """
        _datasets = get_hdf5_populated_dataset_keys(
            self._config["current_filename"],
            min_dim=self._config["min_datadim"],
            ignore_keys=self._config["activeDsetFilters"],
        )
        if "/entry/data/data" in _datasets:
            _datasets.remove("/entry/data/data")
            _datasets.insert(0, "/entry/data/data")
        if len(_datasets) == 0:
            _datasets = [""]
        _param_widget = self.param_widgets["dataset"]
        self.params["dataset"].update_value_and_choices(_datasets[0], _datasets)
        _param_widget.update_choices(_datasets)
        _param_widget.view().setMinimumWidth(
            get_max_pixel_width_of_entries(_datasets) + 50
        )
        self.__select_dataset()

    def __select_dataset(self):
        """
        Select a dataset from the drop-down list.

        This internal method is called by the Qt event system if the QComBoBox
        text has changed to notify the main program that the user has selected
        a different dataset to be visualized. This method also updates the
        accepted frame range for the sliders.
        """
        _dset = self.get_param_value("dataset")
        if _dset == self._config["current_dataset"]:
            return
        self._config["current_dataset"] = _dset
        self.sig_new_dataset_selected.emit(_dset)

    def _toggle_filter_key(self, key: str):
        """
        Add or remove the filter key from the active dataset key filters.

        This method will add or remove the <key> which is associated with the
        checkbox widget <widget> from the active dataset filters.
        Note: This method should never be called by the user, but it is
        connected to the checkboxes which activate or deactivate the respective
        filters.

        Parameters
        ----------
        key : str
            The dataset filter string.
        """
        _widget = self._widgets[f"check_filter_{key}"]
        if _widget.isChecked() and key not in self._config["activeDsetFilters"]:
            self._config["activeDsetFilters"].append(key)
        if not _widget.isChecked() and key in self._config["activeDsetFilters"]:
            self._config["activeDsetFilters"].remove(key)
        self.__populate_dataset_list()

    @QtCore.Slot(str)
    def new_filename(self, filename: str):
        """
        Process the new filename.

        If the new filename has a suffix associated with hdf5 files,
        show the widget.

        Parameters
        ----------
        filename : str
            The full file system path to the new file.
        """
        _filename = Path(filename)
        _is_hdf5 = get_extension(_filename, lowercase=True) in HDF5_EXTENSIONS
        self.setVisible(_is_hdf5)
        if (not _filename.is_file()) or filename == self._config["current_filename"]:
            return
        self._config["current_filename"] = filename if _is_hdf5 else ""
        self._config["current_dataset"] = ""
        if _is_hdf5:
            self.__populate_dataset_list()

    def clear(self):
        """
        Clear all entries for the widget.
        """
        self.setVisible(False)
        self._config["current_dataset"] = ""
        self._config["current_filename"] = ""

    def _toggle_details(self):
        """
        Toggle the visibility of the detailed dataset selection options.
        """
        _show = not self._config["display_details"]
        for _key in self._widgets:
            if _key.startswith("check_filter_") or _key.startswith("empty_"):
                self._widgets[_key].setVisible(_show)
        self.param_composite_widgets["min_datadim"].setVisible(_show)
        self._config["display_details"] = _show
        self._widgets["button_toggle_details"].setText(
            "Hide detailed dataset selection options"
            if _show
            else "Show detailed dataset selection options"
        )
        self._widgets["button_toggle_details"].setIcon(
            get_pyqt_icon_from_str("qt-std::SP_TitleBarShadeButton")
            if _show
            else get_pyqt_icon_from_str("qt-std::SP_TitleBarUnshadeButton")
        )
