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
__all__ = ["EigerScanSeriesLoader"]

import os

from pydidas.core import UserConfigError, get_generic_param_collection
from pydidas.core.constants import INPUT_PLUGIN
from pydidas.core.utils import copy_docstring, get_hdf5_metadata
from pydidas.experiment import SetupScan
from pydidas.plugins import InputPlugin
from pydidas.data_io import import_data


SCAN = SetupScan()


class EigerScanSeriesLoader(InputPlugin):
    """
    Load data frames from an Eiger scan series with files in different
    directories.

    This class is designed to load data from a series of directories with a
    single hdf5 file in each, as created by a series of scans with the Eiger
    detector.
    The key to the hdf5 dataset needs to be provided as well as the number
    of images per file. A value of -1 will have the class check for the number
    of images per file on its own.
    Filesystem checks can be enabled using the live_processing keyword but
    are disabled by default.

    A region of interest and image binning can be supplied to apply directly
    to the raw image.

    Parameters
    ----------
    eiger_dir : str, optional
        The directory name created by the Eiger detector to store its data.
        The default is "eiger9m".
    filename_suffix : str, optional
        The suffix to be appended to the filename pattern (including extension)
        to make up the full filename. The default is "_data_00001.h5"
    hdf5_key : str
        The key to access the hdf5 dataset in the file.
    images_per_file : int, optional
        The number of images per file. If -1, pydidas will auto-discover the number
        of images per file based on the first file. The default is -1.
    live_processing : bool, optional
        Flag to toggle file system checks. In live_processing mode, checks
        for the size and existance of files are disabled. The default is False.
    """

    plugin_name = "Eiger scan series loader"
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    default_params = get_generic_param_collection(
        "eiger_dir",
        "filename_suffix",
        "hdf5_key",
        "images_per_file",
    )
    input_data_dim = None
    output_data_dim = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, use_filename_pattern=True, **kwargs)
        self.filename_string = ""

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

    def update_filename_string(self):
        """
        Set up the generator that can create the full file names to load images.
        """
        _basepath = SCAN.get_param_value("scan_base_directory", dtype=str)
        _pattern = SCAN.get_param_value("scan_name_pattern", dtype=str)
        _eigerkey = self.get_param_value("eiger_dir")
        _suffix = self.get_param_value("filename_suffix", dtype=str)
        if _pattern.endswith(_suffix):
            _pattern = _pattern[: -len(_suffix)]
        _len_pattern = _pattern.count("#")
        if _len_pattern < 1:
            raise UserConfigError("No filename pattern detected in the Input plugin!")
        _name = os.path.join(_basepath, _pattern, _eigerkey, _pattern + _suffix)
        self.filename_string = _name.replace(
            "#" * _len_pattern, "{index:0" + str(_len_pattern) + "d}"
        )

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
                "pre_execute has not been called for EigerScanSeriesLoader and no "
                "filename generator has been created."
            )
        _images_per_file = self.get_param_value("images_per_file")
        _i_file = frame_index // _images_per_file + SCAN.get_param_value(
            "scan_start_index"
        )
        return self.filename_string.format(index=_i_file)
