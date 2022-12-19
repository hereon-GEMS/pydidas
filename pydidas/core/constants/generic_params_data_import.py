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
The generic_params_data_import module holds all the required data to create generic
Parameters for data import.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["GENERIC_PARAMS_DATA_IMPORT"]


GENERIC_PARAMS_DATA_IMPORT = {
    "filename": {
        "type": "Path",
        "default": "",
        "name": "Filename",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The file name of the input file.",
    },
    "filename_pattern": {
        "type": "Path",
        "default": "",
        "name": "The filename pattern",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The pattern of the filename. Use hashes '#' for wildcards which will "
            "be filled in with numbers. This Parameter must be set if scan_for_all "
            "is False."
        ),
    },
    "first_file": {
        "type": "Path",
        "default": "",
        "name": "First file name",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The name of the first file for a file series or of the hdf5 file in "
            "case of hdf5 file input."
        ),
    },
    "last_file": {
        "type": "Path",
        "default": "",
        "name": "Last file name",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Used only for file series: The name of the last file to be used for "
            "this app or tool."
        ),
    },
    "file_stepping": {
        "type": int,
        "default": 1,
        "name": "File stepping",
        "choices": None,
        "allow_None": False,
        "tooltip": (
            "The step width (in files), A value n > 1 will only process every n-th "
            "file."
        ),
    },
    "hdf5_key": {
        "type": "Hdf5key",
        "default": "/entry/data/data",
        "name": "Hdf5 dataset key",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "Used only for hdf5 files: The dataset key.",
    },
    "hdf5_frame": {
        "type": int,
        "default": 0,
        "name": "Frame number",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "For hdf5 image files: The frame number in the dataset",
    },
    "hdf5_first_image_num": {
        "type": int,
        "default": 0,
        "name": "First image number",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The first image in the hdf5-dataset to be used.",
    },
    "hdf5_last_image_num": {
        "type": int,
        "default": -1,
        "name": "Last image number",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The last image in the hdf5-dataset to be used. The value -1 will "
            "default to the last image."
        ),
    },
    "hdf5_stepping": {
        "type": int,
        "default": 1,
        "name": "Hdf5 dataset stepping",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The step width (in frames). A value n > 1 will only "
            "process every n-th frame."
        ),
    },
    "bg_file": {
        "type": "Path",
        "default": "",
        "name": "Background image file",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The name of the file used for background correction.",
    },
    "bg_hdf5_key": {
        "type": "Hdf5key",
        "default": "/entry/data/data",
        "name": "Background image Hdf5 dataset key",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "For hdf5 background image files: The dataset key.",
    },
    "bg_hdf5_frame": {
        "type": int,
        "default": 0,
        "name": "Background image number",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "For hdf5 background image files: The image number in the dataset"
        ),
    },
    "images_per_file": {
        "type": int,
        "default": -1,
        "name": "Images per file",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The number of images in the file. For hdf5 files, this corresponds to "
            "the number of frames in the hdf5 dataset. A value -1 auto-discovers "
            "the number of images per file."
        ),
    },
    "directory_path": {
        "type": "Path",
        "default": "",
        "name": "Directory path",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The absolute path of the directory to be used.",
    },
    "eiger_filename_suffix": {
        "type": str,
        "default": "_data_000001.h5",
        "name": "Eiger filename suffix",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The suffix to be appended to the filename pattern to get"
            " the full filename for the data file."
        ),
    },
    "eiger_dir": {
        "type": str,
        "default": "eiger9m",
        "name": "Eiger directory key",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The name of the sub-directory for each scan in which the"
            " Eiger detector writes its data files."
        ),
    },
}
