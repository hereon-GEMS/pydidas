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
Module with the Hdf5singleFileLoader Plugin which can be used to load
images from single Hdf5 files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Hdf5fileSeriesLoader"]


from pydidas.core import Dataset, get_generic_param_collection
from pydidas.core.utils import get_hdf5_metadata
from pydidas.data_io import import_data
from pydidas.plugins import InputPlugin


class Hdf5fileSeriesLoader(InputPlugin):
    """
    Load 2d data frames from Hdf5 data files.

    This class is designed to load image data from a series of hdf5 file. The file
    series is defined through the SCAN's base directory, filename pattern and
    start index.

    The final filename is
    <SCAN base directory>/<SCAN name pattern with index substituted for hashes>.

    The dataset in the Hdf5 file is defined by the hdf5_key Parameter.

    A region of interest and image binning can be supplied to apply directly
    to the raw image.

    Parameters
    ----------
    hdf5_key : str, optional
        The key to access the hdf5 dataset in the file. The default is entry/data/data.
    hdf5_slicing_axis : int, optional
        The axis along which the images are sliced in the hdf5 file. If None, the
        images are assumed to be stored in a single 2d array. If an integer is
        provided, it is assumed that the images are stored in a 3d array and the
        images are sliced along the given axis. The default is None.
    images_per_file : int, optional
        The number of images (or spectra in the case of 1d data)  per file.
        If -1, pydidas will auto-discover the number of images per file based on
        the first file. The default is -1.
    """

    plugin_name = "HDF5 file series loader"
    default_params = get_generic_param_collection(
        "hdf5_key",
        "hdf5_slicing_axis",
        "images_per_file",
    )
    advanced_parameters = InputPlugin.advanced_parameters.copy() + [
        "hdf5_slicing_axis",
        "images_per_file",
    ]

    def pre_execute(self):
        """
        Prepare loading images from a file series.
        """
        InputPlugin.pre_execute(self)
        _i_per_file = self.get_param_value("images_per_file")
        _slice_ax = self.get_param_value("hdf5_slicing_axis")
        if _slice_ax is None:
            _i_per_file = 1
        elif _i_per_file == -1:
            _i_per_file = get_hdf5_metadata(
                self.get_filename(0), "shape", dset=self.get_param_value("hdf5_key")
            )[_slice_ax]
        self.set_param_value("_counted_images_per_file", _i_per_file)
        self._standard_kwargs = {
            "dataset": self.get_param_value("hdf5_key"),
            "binning": self.get_param_value("binning"),
            "forced_dimension": 2,
            "import_metadata": False,
        }
        self._index_func = lambda i: (
            None if _slice_ax is None else ((None,) * _slice_ax + (i,))
        )

    def get_frame(self, frame_index: int, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Load a frame and pass it on.

        Parameters
        ----------
        frame_index : int
            The frame index.
        **kwargs : dict
            Any calling keyword arguments. Can be used to apply a ROI or
            binning to the raw image.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            The updated kwargs for importing the frame.
        """
        _fname = self.get_filename(frame_index)
        _hdf_index = frame_index % self.get_param_value("_counted_images_per_file")
        kwargs = kwargs | self._standard_kwargs
        kwargs["indices"] = self._index_func(_hdf_index)

        _data = import_data(_fname, roi=self._get_own_roi(), **kwargs)
        if _data.ndim == 2:
            _data.axis_units = ["pixel", "pixel"]
            _data.axis_labels = ["detector y", "detector x"]
        return _data, kwargs
