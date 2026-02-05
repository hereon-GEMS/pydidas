# This file is part of pydidas
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Hdf5DatasetSelector"]


from pathlib import Path
from typing import Any

from qtpy import QtCore

from pydidas.core import Parameter
from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH, HDF5_EXTENSIONS
from pydidas.core.utils import (
    ShowBusyMouse,
    get_extension,
    update_child_qobject,
)
from pydidas.core.utils.hdf5 import get_hdf5_populated_dataset_keys
from pydidas.widgets.utilities import (
    get_max_pixel_width_of_entries,
    get_pyqt_icon_from_str,
)
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


DEFAULT_FILTERS = {
    "/entry/instrument/detector/detectorSpecific/": (
        "Dectris (e.g. Eiger)\n `detectorSpecific` keys"
    ),
    "/entry/instrument/detector/": ("X-Spectrum (e.g. Lambda)\n `specific` keys"),
}
FILTER_EXCEPTIONS = {
    "/entry/instrument/detector/": ["/entry/instrument/detector/data"],
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
_CHECK_BOX_CREATE_KWARGS = {
    "font_metric_height_factor": 2,
    "font_metric_width_factor": 40,
    "parent_widget": "filter_container",
    "checked": True,
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
    **kwargs : Any
        Any additional keyword arguments. See below for supported arguments.

        dataset_filter_keys : dict, optional
            A dictionary with dataset keys to be filtered from the list
            of displayed datasets. Entries must be in the format
            {<Key to filter>: <Descriptive text for checkbox>}.
            The default is the built-in dict with detector-specific filter
            keys.
        dataset_filter_exceptions : dict, optional
            A dictionary with lists of dataset keys which are exceptions
            to the filter keys. Entries must be in the format
            {<Filter key>: [<Exception key 1>, <Exception key 2>, ...]}.
            The default is the built-in dict with detector-specific
            exceptions.
    """

    sig_new_dataset_selected = QtCore.Signal(str)
    sig_request_hdf5_browser = QtCore.Signal()

    def __init__(self, **kwargs: Any) -> None:
        _filter_keys = kwargs.pop("dataset_filter_keys", DEFAULT_FILTERS)
        _filter_exceptions = kwargs.pop("dataset_filter_exceptions", FILTER_EXCEPTIONS)
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.add_params(DATA_DIMENSION_PARAM.copy(), DATASET_PARAM.copy())

        self._config = {
            "current_dataset": "",
            "current_filename": "",
            "min_datadim": 1,
            "display_details": False,
            "dset_filters": _filter_keys,
            "dset_filter_exceptions": _filter_exceptions,
        }
        self.__create_widgets()
        self.__connect_slots()
        self.setVisible(kwargs.get("visible", False))

    def __create_widgets(self) -> None:
        """Create all required widgets."""
        self.__icon_vis = get_pyqt_icon_from_str("qt-std::SP_TitleBarShadeButton")
        self.__icon_invis = get_pyqt_icon_from_str("qt-std::SP_TitleBarUnshadeButton")
        update_child_qobject(self, "layout", horizontalSpacing=2)
        self.create_button(
            "button_inspect",
            "Inspect HDF5 tree structure",
            gridPos=(0, 2, 1, 1),
            icon="qt-std::SP_MessageBoxInformation",
        )
        self.create_empty_widget(
            "filter_container", gridPos=(1, 0, 1, 3), visible=False
        )
        self.create_param_widget(
            self.get_param("dataset"),
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            gridPos=(2, 0, 1, 2),
            width_text=0.275,
            width_io=0.725,
        )
        self.create_spacer("spacer_right", fixedWidth=15, gridPos=(2, 1, 1, 1))
        self.layout().setColumnStretch(1, 10)
        self.create_button(
            "button_toggle_details",
            "Show detailed dataset selection options",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            icon="qt-std::SP_TitleBarUnshadeButton",
            gridPos=(2, 2, 1, 1),
        )
        _index = 0
        self.create_check_box(
            "check_nxsignal",
            " Show only NXdata\n 'signal' datasets",
            gridPos=(0, 0, 1, 1),
            **_CHECK_BOX_CREATE_KWARGS,
        )
        for _index, (_key, _text) in enumerate(self._config["dset_filters"].items()):
            self.create_check_box(
                f"check_filter_{_key}",
                f" Hide {_text}",
                gridPos=((_index + 1) // 3, (_index + 1) % 3, 1, 1),
                **_CHECK_BOX_CREATE_KWARGS,
            )
        self.create_param_widget(
            self.get_param("min_datadim"),
            gridPos=(-1, 0, 1, 1),
            parent_widget="filter_container",
        )
        self.create_spacer("spacer_bottom", fixedHeight=15, gridPos=(-1, 0, 1, 1))

    def __connect_slots(self) -> None:
        """Connect all required slots."""
        self.param_composite_widgets["min_datadim"].sig_new_value.connect(
            self.__process_new_min_datadim
        )
        for _key in self._config["dset_filters"]:
            self._widgets[f"check_filter_{_key}"].sig_check_state_changed.connect(
                self.__populate_dataset_list
            )
        self._widgets["check_nxsignal"].sig_check_state_changed.connect(
            self.__populate_dataset_list
        )
        self.param_composite_widgets["dataset"].sig_value_changed.connect(
            self.display_dataset
        )
        self._widgets["button_inspect"].clicked.connect(self.sig_request_hdf5_browser)
        self._widgets["button_toggle_details"].clicked.connect(self._toggle_details)

    @property
    def active_filters(self) -> list[str]:
        """Get the list of currently active dataset filters."""
        return [
            _key
            for _key in self._config["dset_filters"]
            if self._widgets[f"check_filter_{_key}"].isChecked()
        ]

    @property
    def dset_filter_exceptions(self) -> list[str]:
        """Get the list of dataset keys which are exceptions to the active filters."""
        _filter_exceptions = []
        for _key in self.active_filters:
            for _exception in self._config["dset_filter_exceptions"].get(_key, []):
                if _exception not in _filter_exceptions:
                    _filter_exceptions.append(_exception)
        return _filter_exceptions

    @QtCore.Slot(str)
    def __process_new_min_datadim(self, value: str) -> None:
        """
        Update the available datasets according to the new minimum dataset dimension.

        Parameters
        ----------
        value : str
            The new value of the minimum dataset dimension parameter.
        """
        self._config["min_datadim"] = 0 if value == "any" else int(value.split("=")[1])
        self.__populate_dataset_list()

    @QtCore.Slot()
    def __populate_dataset_list(self) -> None:
        """
        Populate the dataset selection drop-down menu.

        This method reads the structure of the hdf5 file and filters the
        list of datasets according to the selected criteria. The filtered list
        is used to populate the selection drop-down menu.
        """
        with ShowBusyMouse():
            _datasets = get_hdf5_populated_dataset_keys(
                self._config["current_filename"],
                min_dim=self._config["min_datadim"],
                ignore_keys=self.active_filters,
                nxdata_signal_only=self._widgets["check_nxsignal"].isChecked(),
                ignore_key_exceptions=self.dset_filter_exceptions,
            )
            if "/entry/data/data" in _datasets:
                _datasets.remove("/entry/data/data")
                _datasets.insert(0, "/entry/data/data")
            if len(_datasets) == 0:
                _datasets = [""]
            _curr_choice = self.get_param_value("dataset")
            _new_choice = _curr_choice if _curr_choice in _datasets else _datasets[0]
            self.set_param_and_widget_value_and_choices(
                "dataset", _new_choice, _datasets
            )
            self.param_composite_widgets["dataset"].io_widget.view().setMinimumWidth(
                get_max_pixel_width_of_entries(_datasets) + 50
            )  # type: ignore[attr-defined]

    @property
    def dataset(self) -> str:
        """Get the currently selected dataset."""
        return self.get_param_value("dataset")

    @QtCore.Slot()
    def display_dataset(self) -> None:
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
        self.sig_new_dataset_selected.emit(_dset)  # type: ignore[attr-defined]

    @QtCore.Slot(str)
    def new_filename(self, filename: str) -> None:
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
        if not _is_hdf5:
            return
        _is_current = _filename == self._config["current_filename"]
        self._config["current_filename"] = filename
        if _filename.is_file() and not _is_current:
            self._config["current_dataset"] = ""
            self.__populate_dataset_list()
        self.display_dataset()

    def clear(self) -> None:
        """Clear all entries for the widget."""
        self.setVisible(False)
        self._config["current_dataset"] = ""
        self._config["current_filename"] = ""

    def _toggle_details(self) -> None:
        """Toggle the visibility of the detailed dataset selection options."""
        _is_visible = not self._config["display_details"]
        self._widgets["filter_container"].setVisible(_is_visible)
        self._config["display_details"] = _is_visible
        self._widgets["button_toggle_details"].setText(
            ("Hide" if _is_visible else "Show") + " detailed dataset selection options"
        )
        self._widgets["button_toggle_details"].setIcon(
            self.__icon_vis if _is_visible else self.__icon_invis
        )
