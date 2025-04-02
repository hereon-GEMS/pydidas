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
The generic_params_data_import module holds all the required data to create generic
Parameters for data import.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
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
    "current_filename": {
        "type": str,
        "default": "",
        "name": "Current input filename",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The filename of the currently active file.",
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
    "hdf5_slicing_axis": {
        "type": int,
        "default": 0,
        "name": "Hdf5 frame slicing axes",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The slicing axes to identify the frame by its number in the full "
            "dataset. For example, if the frame has the axes (frame index, x, y), "
            "the slicing axes would be 0. To use the full dataset, set the slicing "
            "axis to `None`. A `None` setting will also ignore the hdf5 frame number "
            "Parameter."
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
        "tooltip": "For hdf5 background image files: The image number in the dataset",
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
    "profiles_per_file": {
        "type": int,
        "default": -1,
        "name": "Profiles per file",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The number of 1d profiles in the file. For hdf5 files, this corresponds "
            "to the number of frames in the hdf5 dataset. A value -1 auto-discovers "
            "the number of profiles per file."
        ),
    },
    "_counted_images_per_file": {
        "type": int,
        "default": 1,
        "name": "Processed images per file",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The number of images per file pydidas counted from the first file.",
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
    "raw_datatype": {
        "type": str,
        "default": "float 64 bit",
        "name": "Datatype",
        "choices": (
            ["boolean (1 bit integer)"]
            + [f"float {_i} bit" for _i in [16, 32, 64, 128]]
            + [f"int {_i} bit" for _i in [8, 16, 32, 64]]
            + [f" unsigned int {_i} bit" for _i in [8, 16, 32, 64]]
        ),
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The data type to be used for decoding. Note that numpy data types are "
            "used for decoding with native byteorder."
        ),
    },
    "raw_shape_x": {
        "type": int,
        "default": 0,
        "name": "Raw shape x",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": (
            "The x shape of the raw data file. Following the python convention,"
            "the first axis is y and the second axis is x."
        ),
    },
    "raw_shape_y": {
        "type": int,
        "default": 0,
        "name": "Raw shape y",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": (
            "The y shape of the raw data file. Following the python convention,"
            "the first axis is y and the second axis is x."
        ),
    },
    "raw_header": {
        "type": int,
        "default": 0,
        "name": "Raw file header length",
        "choices": None,
        "unit": "bytes",
        "allow_None": False,
        "tooltip": (
            "The length of the file header in bytes. The header will not be "
            "decoded as image data."
        ),
    },
    "num_frames_to_use": {
        "type": int,
        "default": 2,
        "name": "Number of frame to use",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The number of frames to be loaded and included in the stack. "
            "Frames are loaded starting with the first frame index and thus "
            "allow a rolling average over the frames."
        ),
    },
    "files_per_directory": {
        "type": int,
        "default": -1,
        "name": "Images per directory",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The number of files in the directory.",
    },
    "_counted_files_per_directory": {
        "type": int,
        "default": 1,
        "name": "Processed images per directory",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The counted number of images per directory.",
    },
    "fio_suffix": {
        "type": str,
        "default": "_mca_s#.fio",
        "name": "FIO file suffix",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The file suffix for teh individual MCA files.",
    },
    "use_custom_xscale": {
        "type": bool,
        "default": False,
        "name": "Use custom scale for x-axis",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Use a custom scale for the x-axis. If False, the scale will be "
            "created in channel numbers."
        ),
    },
    "x0_offset": {
        "type": float,
        "default": 0.0,
        "name": "x0 offset",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The offset for the zeroth channel.",
    },
    "x_delta": {
        "type": float,
        "default": 1.0,
        "name": "Channel Delta x",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The width of each channel.",
    },
    "x_unit": {
        "type": str,
        "default": "a.u.",
        "name": "x-axis unit",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The unit of the x-axis.",
    },
    "x_label": {
        "type": str,
        "default": "x",
        "name": "x-axis label",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The label for the x-axis.",
    },
    "data_dimensionality": {
        "type": int,
        "default": 2,
        "name": "Data dimensionality",
        "choices": [1, 2, 3],
        "unit": "",
        "allow_None": False,
        "tooltip": "The dimensionality of the data to be loaded.",
    },
    "detector_axis_label": {
        "type": str,
        "default": "detector",
        "name": "Detector axis label",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The label for the detector axis.",
    },
}
