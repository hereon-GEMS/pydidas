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

"""
Module with the Hdf5singleFileLoader Plugin which can be used to load
images from single Hdf5 files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["Hdf5fileSeriesLoader"]

from pydidas.core import get_generic_param_collection, UserConfigError
from pydidas.core.constants import INPUT_PLUGIN
from pydidas.core.utils import copy_docstring, get_hdf5_metadata
from pydidas.plugins import InputPlugin
from pydidas.experiment import SetupScan
from pydidas.data_io import import_data


SCAN = SetupScan()


class Hdf5fileSeriesLoader(InputPlugin):
    """
    Load data frames from Hdf5 data files.

    This class is designed to load data from a series of hdf5 file. The file
    series is defined through the SCAN's base directory, filename pattern and
    start index.


    The final filename is
    <SCAN base directory>/<SCAN name pattern with index subsituted for hashes>.

    The dataset in the Hdf5 file is defined by the hdf5_key Parameter.

    A region of interest and image binning can be supplied to apply directly
    to the raw image.

    Parameters
    ----------
    hdf5_key : str, optional
        The key to access the hdf5 dataset in the file. The default is entry/data/data.
    images_per_file : int, optional
        The number of images per file. If -1, pydidas will auto-discover the number
        of images per file based on the first file. The default is -1.
    file_stepping : int, optional
        The stepping width through all files in the file list, determined
        by fist and last file. The default is 1.
    """

    plugin_name = "HDF5 file series loader"
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    default_params = get_generic_param_collection(
        "hdf5_key", "images_per_file", "file_stepping"
    )
    input_data_dim = None
    output_data_dim = 2

    def pre_execute(self):
        """
        Prepare loading images from a file series.
        """
        InputPlugin.pre_execute(self)
        if self.get_param_value("images_per_file") == -1:
            _n_per_file = get_hdf5_metadata(
                self.get_filename(0), "shape", dset=self.get_param_value("hdf5_key")
            )[0]
            self.set_param_value("images_per_file", _n_per_file)

    def get_frame(self, frame_index, **kwargs):
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
        data : pydidas.core.Dataset
            The image data.
        """
        _fname = self.get_filename(frame_index)
        _hdf_index = frame_index % self.get_param_value("images_per_file")
        kwargs["dataset"] = self.get_param_value("hdf5_key")
        kwargs["frame"] = _hdf_index
        kwargs["binning"] = self.get_param_value("binning")
        _data = import_data(_fname, **kwargs)
        _data.axis_units = ["pixel", "pixel"]
        _data.axis_labels = ["detector y", "detector x"]
        return _data, kwargs

    @copy_docstring(InputPlugin)
    def get_filename(self, frame_index):
        """
        For the full docstring, please refer to the
        :py:class:`pydidas.plugins.base_input_plugin.InputPlugin
        <InputPlugin>` class.
        """
        if self.filename_string == "":
            raise UserConfigError(
                "pre_execute has not been called for Hdf5FileSeriesLoader and no "
                "filename generator has been created."
            )
        _images_per_file = self.get_param_value("images_per_file")
        _i_file = (frame_index // _images_per_file) * self.get_param_value(
            "file_stepping"
        ) + SCAN.get_param_value("scan_start_index")
        return self.filename_string.format(index=_i_file)
