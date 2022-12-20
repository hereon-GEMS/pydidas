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
The generic_params_other module holds all the required data to create generic
Parameters which are are not included in other specialized modules.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["GENERIC_PARAMS_OTHER"]


from .unicode_greek_letters import GREEK_ASCII_TO_UNI

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
        "tooltip": "The toal number of images in the composite images.",
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
    "image_num": {
        "type": int,
        "default": 0,
        "name": "Image number",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The image number to be processed.",
    },
    #####################
    # fitting settings
    #####################
    "fit_sigma_threshold": {
        "type": float,
        "default": 0.25,
        "name": f"Fit {GREEK_ASCII_TO_UNI['sigma']} rejection threshold",
        "choices": None,
        "allow_None": False,
        "unit": "",
        "tooltip": (
            "The threshold to select which fitting points to reject, based on the "
            "normalized standard deviation. Any fit which has a normalized std "
            "which is worse than the threshold will be rejected as failed."
        ),
    },
    "fit_min_peak_height": {
        "type": float,
        "default": None,
        "name": "Minimum peak height to fit",
        "choices": None,
        "allow_None": True,
        "unit": "",
        "tooltip": (
            "The minimum height a peak must have to attempt a fit. A value of "
            "'None' will not impose any limits on the peak height."
        ),
    },
    "fit_func": {
        "type": str,
        "default": "Gaussian",
        "name": "Fit function",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Select the type of fit function to be used in the single peak fit."
        ),
    },
    "fit_bg_order": {
        "type": int,
        "default": 0,
        "name": "Fit background order",
        "choices": [None, 0, 1],
        "unit": "",
        "allow_None": True,
        "tooltip": "The order of the background. None corresponds to no background.",
    },
    "fit_upper_limit": {
        "type": float,
        "default": 0,
        "name": "Peak fit upper limit",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The upper limit (in the x-axis´ unit) to the fit region.",
    },
    "fit_lower_limit": {
        "type": float,
        "default": 0,
        "name": "Peak fit lower limit",
        "choices": None,
        "unit": "",
        "allow_None": False,
        "tooltip": "The lower limit (in the x-axis´ unit) to the fit region.",
    },
    ########################
    # global choice settings
    ########################
    "use_global_mask": {
        "type": int,
        "default": 1,
        "name": "Use global mask",
        "choices": [True, False],
        "unit": "",
        "allow_None": False,
        "tooltip": (
            "Select 'True' to use the global settings for the detector mask and "
            "mask value. A 'False' settings uses the local mask settings. Note: "
            "The mask value will not be used for integrating but only for "
            "presentation or by using the MaskImage plugin."
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
            "results for each plugin will be saved in a separete file (or files if "
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
            "been excuted. All data will be saved in a single folder for each run "
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
        "name": "The ative node",
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
            "The axis which is to be used as the first axis in the "
            "plot of the results."
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
    # '': {
    #     'type': int,
    #     'default': ,
    #     'name': '',
    #     'choices': None,
    #     'unit': '',
    #     'allow_None': False,
    #     'tooltip': },
}
