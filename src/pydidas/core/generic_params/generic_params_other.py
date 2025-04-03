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
The generic_params_other module holds all the required data to create generic
Parameters which are are not included in other specialized modules.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_OTHER"]


from pydidas.core.constants.colors import PYDIDAS_COLORS


GENERIC_PARAMS_OTHER = {
    ###############################
    # Generic processing parameters
    ###############################
    "live_processing": {
        "type": int,
        "default": 0,
        "name": "Live processing",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Set live processing to True if the files do not yet exist at process "
            "startup. This will skip checks on file existence and size."
        ),
    },
    "label": {
        "type": str,
        "default": "",
        "name": "Node label",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "A label for identifying the Plugin node in the results. Internally, "
            "all Plugins are identified by their node IDs, this additional label "
            "is merely a handle for easier human identification."
        ),
    },
    "keep_results": {
        "type": bool,
        "default": False,
        "name": "Always store results",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Flag to force pydidas to keep the results of this plugin available "
            "even if it is intermediary data and would normally not be stored."
        ),
    },
    ##################################
    # Parameters for CompositeCreation
    ##################################
    "hdf5_dataset_shape": {
        "type": tuple,
        "default": (0, 0, 0),
        "name": "Hdf5 dataset shape",
        "choices": None,
        "allow_None": False,
        "tooltip": (
            "The shape of the hdf5 dataset. This corresponds to "
            "(number of images, image size y, image size x)."
        ),
    },
    "use_bg_file": {
        "type": int,
        "default": 0,
        "name": "Subtract background image",
        "choices": [True, False],
        "allow_None": False,
        "tooltip": "Keyword to toggle usage of background subtraction.",
    },
    "n_image": {
        "type": int,
        "default": 0,
        "name": "Total number of images",
        "choices": None,
        "unit": "",
        "tooltip": "The total number of images in the composite images.",
    },
    "n_files": {
        "type": int,
        "default": 0,
        "name": "Total number of files",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The total number of selected files.",
    },
    "composite_nx": {
        "type": int,
        "default": 1,
        "name": "Number of images in x",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The number of original images combined in the composite image in x "
            "direction. A value of -1 will determine the number of images in x "
            "direction automatically based on the number of images in y direction."
        ),
    },
    "composite_ny": {
        "type": int,
        "default": -1,
        "name": "Number of images in y",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The number of original images combined in the composite image in y "
            "direction. A value of -1 will determine the number of images in y "
            "direction automatically based on the number of images in x direction."
        ),
    },
    "composite_dir": {
        "type": str,
        "default": "x",
        "name": "Preferred composite direction",
        "choices": ["x", "y"],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The 'fast' direction of the composite image. This dimension will be "
            "filled first before going to the next row/column."
        ),
    },
    "composite_image_op": {
        "type": str,
        "default": None,
        "name": "Raw image operation",
        "choices": [
            None,
            "Flip left/right",
            "Flip up/down",
            "Rot 180deg",
            "Rot 90deg clockwise",
            "Rot 90deg counter-clockwise",
        ],
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The image operation applied to each raw image prior to merging it in "
            "the composite image. This allows to adjust the image orientation with "
            "respect to the scan."
        ),
    },
    "composite_xdir_orientation": {
        "type": str,
        "default": "left-to-right",
        "name": "X orientation direction",
        "choices": ["left-to-right", "right-to-left"],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The direction of how images are inserted into the composite in x "
            "direction. Left-to-right starts with low indices (python standard) "
            "whereas right-to-left will insert image at the max index position "
            "first."
        ),
    },
    "composite_ydir_orientation": {
        "type": str,
        "default": "top-to-bottom",
        "name": "Y orientation direction",
        "choices": ["top-to-bottom", "bottom-to-top"],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The direction of how images are inserted into the composite in y "
            "direction. Top-to-bottom starts with low indices (python standard) "
            "whereas bottom-to-top will insert image at the max index position "
            "first. Note that the display may be flipped with the origin at the "
            "bottom."
        ),
    },
    "first_index": {
        "type": int,
        "default": 0,
        "name": "First index",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The first index to be used for the file series.",
    },
    "last_index": {
        "type": int,
        "default": 0,
        "name": "Last index",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The last index to be used for the file series.",
    },
    "frame_index": {
        "type": int,
        "default": 0,
        "name": "Global frame index",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The global index of the frame to be processed. Note: The first frame "
            "number is always 0, irrespective of any offsets in the filenames."
        ),
    },
    "detector_image_index": {
        "type": int,
        "default": 0,
        "name": "Detector image number",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": ("The detector image number, as files are written to disk."),
    },
    ################
    # Generic limits
    ################
    "upper_limit": {
        "type": float,
        "default": None,
        "name": "Upper limit",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The upper limit of data selection. This point is included in the data. "
            "Note that the selection is either in indices or data range, depending on "
            "the value of 'type_selection'. A limit of 'None' will set no upper limit."
        ),
    },
    "lower_limit": {
        "type": float,
        "default": None,
        "name": "Lower limit",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The lower limit of data selection. This point is included in the data. "
            "Note that the selection is either in indices or data range, depending on "
            "the value of 'type_selection'. A limit of 'None' will set no lower limit."
        ),
    },
    "upper_limit_ax0": {
        "type": float,
        "default": None,
        "name": "Upper limit axis 0 (y)",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The upper limit of data selection. This point is included in the data. "
            "Note that the selection is either in indices or data range, depending on "
            "the value of 'type_selection'. A limit of 'None' will set no upper limit."
        ),
    },
    "lower_limit_ax0": {
        "type": float,
        "default": None,
        "name": "Lower limit axis 0 (y)",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The lower limit of data selection. This point is included in the data. "
            "Note that the selection is either in indices or data range, depending on "
            "the value of 'type_selection'. A limit of 'None' will set no lower limit."
        ),
    },
    "upper_limit_ax1": {
        "type": float,
        "default": None,
        "name": "Upper limit axis 1 (x)",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The upper limit of data selection. This point is included in the data. "
            "Note that the selection is either in indices or data range, depending on "
            "the value of 'type_selection'. A limit of 'None' will set no upper limit."
        ),
    },
    "lower_limit_ax1": {
        "type": float,
        "default": None,
        "name": "Lower limit axis 1 (x)",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The lower limit of data selection. This point is included in the data. "
            "Note that the selection is either in indices or data range, depending on "
            "the value of 'type_selection'. A limit of 'None' will set no lower limit."
        ),
    },
    ############################
    # Autosave results settings
    ############################
    "autosave_results": {
        "type": int,
        "default": 0,
        "name": "Autosave results",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Save the results automatically after finishing processing. The "
            "results for each plugin will be saved in a separate file (or files if "
            "multiple formats have been selected)."
        ),
    },
    "autosave_directory": {
        "type": "Path",
        "default": "",
        "name": "Autosave directory",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The directory for autosave files.",
    },
    "autosave_format": {
        "type": str,
        "default": "HDF5",
        "name": "Autosave formats",
        "choices": [None, "HDF5"],
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The file format(s) for the data to be saved after the workflow has "
            "been executed. All data will be saved in a single folder for each run "
            "with one file for each plugin."
        ),
    },
    "output_fname": {
        "type": "Path",
        "default": "",
        "name": "Output filename",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The output filename for the data export.",
    },
    "output_fname_digits": {
        "type": int,
        "default": 6,
        "name": "Number of digits in filenames",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The number of digits to be used for the index of the output filename. "
        ),
    },
    "output_index_offset": {
        "type": bool,
        "default": False,
        "name": "Count output file numbers from 1 instead of 0",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "If True, the output files will be numbered starting from 1. If False, "
            "the numbering will start from 0 as is the python default."
        ),
    },
    ############################
    # Result selection settings
    ############################
    "selected_results": {
        "type": str,
        "default": "No selection",
        "name": "Select node result to display",
        "choices": ["No selection"],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The selected node of the WorkflowTree to display the corresponding "
            "results."
        ),
    },
    "saving_format": {
        "type": str,
        "default": "HDF5",
        "name": "Save to format",
        "choices": [None, "HDF5"],
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The file format(s) for saving the data. All data will "
            "be saved in a single folder for each run."
        ),
    },
    "enable_overwrite": {
        "type": int,
        "default": False,
        "name": "Enable overwriting",
        "choices": [False, True],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Allow overwriting of existing files and writing in existing folders. "
            "If this Parameter is True, no further confirmation will be asked and "
            "no further warning will be displayed."
        ),
    },
    "use_scan_timeline": {
        "type": int,
        "default": False,
        "name": "Use scan timeline",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Keyword to toggle using a scan timeline with only one "
            "dimension instead of all scan dimensions."
        ),
    },
    "use_data_range": {
        "type": int,
        "default": True,
        "name": "Use data range",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Keyword to toggle using a the data range instead of "
            "the indices for selecting data."
        ),
    },
    "scan_for_all": {
        "type": int,
        "default": False,
        "name": "Scan for all new files",
        "choices": [False, True],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Scan for all new files and not only files matching the input pattern."
        ),
    },
    "result_n_dim": {
        "type": int,
        "default": -1,
        "name": "Result dimensionality",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The total number of dimensions in the result dataset.",
    },
    "active_node": {
        "type": int,
        "default": 0,
        "name": "The active node",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The node ID of the currently selected node.",
    },
    "type_selection": {
        "type": str,
        "default": "Data values",
        "name": "Data selection",
        "choices": ["Data values", "Indices"],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Select between using the axis values (in the respective."
            "unit) and the axis indices."
        ),
    },
    #################################
    # Result visualization Parameters
    #################################
    "plot_ax1": {
        "type": int,
        "default": 0,
        "name": "Data axis no. 1 for plot",
        "choices": [0],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The axis which is to be used as the first axis in the plot of the results."
        ),
    },
    "plot_ax2": {
        "type": int,
        "default": 1,
        "name": "Data axis no. 2 for plot",
        "choices": [0, 1],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The axis which is to be used as the second axis in the "
            "plot of the results."
        ),
    },
    "overlay_color": {
        "type": str,
        "default": "orange",
        "name": "Plot overlay color",
        "choices": list(PYDIDAS_COLORS.keys()),
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Set the display color for the overlay items (markers and shapes) in the "
            "plot."
        ),
    },
    ############################
    # Dynamic mask configuration
    ############################
    "mask_threshold_low": {
        "type": float,
        "default": None,
        "name": "Lower mask threshold",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The lower threshold for the mask. If any finite value (i.e. not np.nan or "
            "None) is used, the value of any pixels with a value below the threshold "
            "will be masked. A value of np.nan or None will ignore the threshold."
        ),
    },
    "mask_threshold_high": {
        "type": float,
        "default": None,
        "name": "Upper mask threshold",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "tooltip": (
            "The upper threshold for the mask. If any finite value (i.e. not np.nan or "
            "None) is used, the value of any pixels with a value above the threshold "
            "will be masked. A value of np.nan or None will ignore the threshold."
        ),
    },
    "mask_grow": {
        "type": int,
        "default": 0,
        "name": "Grow/shrink masked regions",
        "choices": None,
        "unit": "px",
        "allow_None": False,
        "tooltip": (
            "The masked region can be grown (morphological dilation) or shrunk "
            "(morphological erosion), based on the input value. A value >0 will grow "
            "the masked region by the specified amounts in pixels, a value less than "
            "zero will erode the masked regions by the specified amount."
        ),
    },
    "kernel_iterations": {
        "type": int,
        "default": 1,
        "name": "Grow/shrink iterations",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "The number of iterations to apply the erosion/dilation operation on the "
            "masked region."
        ),
    },
    #######################
    # Plugin data selection
    #######################
    "process_data_dim": {
        "type": int,
        "default": -1,
        "name": "Process data dimension",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "This parameter determines which data dimension should be processed if "
            "the input data dimensionality is larger than the processing "
            "dimensionality. The default of -1 will always use the last data "
            "dimension."
        ),
    },
    "_process_data_dim": {
        "type": int,
        "default": -1,
        "name": "Process data dimension",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "This internal parameter can store the modulated data dimension "
            "to be processed."
        ),
    },
    "process_data_dims": {
        "type": tuple,
        "default": (0, 1),
        "name": "Process data dimensions",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "subtype": int,
        "tooltip": (
            "This parameter determines which data dimensions should be processed if "
            "the input data dimensionality is larger than the processing "
            "dimensionality. The default of None will default to the full data "
            "dimensions and raise an error if the input data has more dimensions "
            "than expected for processing."
        ),
    },
    "_process_data_dims": {
        "type": tuple,
        "default": None,
        "name": "Process data dimensions",
        "choices": None,
        "unit": "",
        "allow_None": True,
        "subtype": int,
        "tooltip": (
            "This internal Parameter can store the modulated data dimensions "
            "to be processed."
        ),
    },
    ####################
    # User Configuration
    ####################
    "auto_check_for_updates": {
        "type": int,
        "default": True,
        "name": "Check for updates",
        "choices": [False, True],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "This parameter allows the user to activate/deactivate the automatic "
            "checking for updates at startup."
        ),
    },
}
