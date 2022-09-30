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
The generic_param_description module holds all the required data to create generic
Parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["GENERIC_PARAM_DESCRIPTION"]

import numpy as np


GENERIC_PARAM_DESCRIPTION = (
    {
        #################################
        # Generic processing paramters
        ##################################
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
        ###################################
        # Parameters for CompositeCreation
        ###################################
        "filename": {
            "type": "Path",
            "default": "",
            "name": "Filename",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": "The file name of the input file.",
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
        "use_bg_file": {
            "type": int,
            "default": 0,
            "name": "Subtract background image",
            "choices": [True, False],
            "allow_None": False,
            "tooltip": "Keyword to toggle usage of background subtraction.",
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
            "tooltip": "The toal number of selected files.",
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
        "use_roi": {
            "type": int,
            "default": 0,
            "name": "Use ROI",
            "choices": [True, False],
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "Keyword to toggle use of the ROI for cropping the original images "
                "before processing them."
            ),
        },
        "roi_xlow": {
            "type": int,
            "default": 0,
            "name": "ROI lower x limit",
            "choices": None,
            "unit": "px",
            "allow_None": False,
            "tooltip": (
                "The lower boundary (in pixel) for cropping images in x, if use_roi is "
                "enabled. Negative values will be modulated with the image width."
            ),
        },
        "roi_xhigh": {
            "type": int,
            "default": None,
            "name": "ROI upper x limit",
            "choices": None,
            "unit": "px",
            "allow_None": True,
            "tooltip": (
                "The upper boundary (in pixel) for cropping images in x, if use_roi is "
                "enabled. Negative values will be modulated with the image width, i.e. "
                "-1 is equivalent with the full image size minus 1. To take the full "
                "image, use 'None' as value for the upper ROI limit."
            ),
        },
        "roi_ylow": {
            "type": int,
            "default": 0,
            "name": "ROI lower y limit",
            "choices": None,
            "unit": "px",
            "allow_None": False,
            "tooltip": (
                "The lower boundary (in pixel) for cropping images in y, if use_roi is "
                "enabled. Negative values will be modulated with the image width."
            ),
        },
        "roi_yhigh": {
            "type": int,
            "default": None,
            "name": "ROI upper y limit",
            "choices": None,
            "unit": "px",
            "allow_None": True,
            "tooltip": (
                "The upper boundary (in pixel) for cropping images in y, if use_roi is "
                "enabled. Negative values will be modulated with the image width, i.e. "
                "-1 is equivalent with the full image size minus 1. To take the full "
                "image, use 'None' as value for the upper ROI limit."
            ),
        },
        "use_thresholds": {
            "type": int,
            "default": 0,
            "name": "Use thresholds",
            "choices": [True, False],
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "Keyword to toggle use of the thresholds for clipping the data range "
                "in the original images before combining them."
            ),
        },
        "threshold_low": {
            "type": float,
            "default": None,
            "name": "Lower threshold",
            "choices": None,
            "unit": "",
            "allow_None": True,
            "tooltip": (
                "The lower threshold of the image. If any finite value (i.e. not "
                "np.nan or None) is used, the value of any pixels with a value below "
                "the threshold will be replaced by the threshold value. A value of "
                "np.nan or None will ignore the threshold."
            ),
        },
        "threshold_high": {
            "type": float,
            "default": None,
            "name": "Upper threshold",
            "choices": None,
            "unit": "",
            "allow_None": True,
            "tooltip": (
                "The upper threshold of the image. If any finite value (i.e. not "
                "np.nan or None) is used, the value of any pixels with a value below "
                "the threshold will be replaced by the threshold value. A value of "
                "np.nan or None will ignore the threshold."
            ),
        },
        "binning": {
            "type": int,
            "default": 1,
            "name": "Binning factor",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The re-binning factor for the images in the composite. "
                "The binning will be applied to the cropped images."
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
        "image_shape": {
            "type": tuple,
            "default": (0, 0),
            "name": "Image shape",
            "choices": None,
            "unit": "px",
            "allow_None": False,
            "tooltip": "The shape of an image.",
        },
        "raw_image_shape": {
            "type": tuple,
            "default": (0, 0),
            "name": "Raw image shape",
            "choices": None,
            "unit": "px",
            "allow_None": False,
            "tooltip": (
                "The image shape of the original image as loaded from the file."
            ),
        },
        "datatype": {
            "type": None,
            "default": np.float32,
            "name": "Datatype",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": "The datatype.",
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
            "tooltip": ("The last index to be used for the file series."),
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
        "filename_suffix": {
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
        #################################
        # Parameters for global geometry
        #################################
        "xray_wavelength": {
            "type": float,
            "default": 1,
            "name": "X-ray wavelength",
            "choices": None,
            "unit": "A",
            "allow_None": False,
            "tooltip": (
                "The X-ray wavelength. Any changes to the wavelength will"
                " also update the X-ray energy setting."
            ),
        },
        "xray_energy": {
            "type": float,
            "default": 12.398,
            "name": "X-ray energy",
            "choices": None,
            "unit": "keV",
            "allow_None": False,
            "tooltip": (
                "The X-ray energy. Changing this parameter will also "
                "update the X-ray wavelength setting."
            ),
        },
        "detector_name": {
            "type": str,
            "default": "detector",
            "name": "Detector name",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": "The detector name in pyFAI nomenclature.",
        },
        "detector_npixx": {
            "type": int,
            "default": 0,
            "name": "Detector size X",
            "choices": None,
            "unit": "px",
            "allow_None": False,
            "tooltip": "The number of detector pixels in x direction (horizontal).",
        },
        "detector_npixy": {
            "type": int,
            "default": 0,
            "name": "Detector size Y",
            "choices": None,
            "unit": "px",
            "allow_None": False,
            "tooltip": "The number of detector pixels in x direction (vertical).",
        },
        "detector_pxsizex": {
            "type": float,
            "default": -1,
            "name": "Detector pixel size X",
            "choices": None,
            "unit": "um",
            "allow_None": False,
            "tooltip": "The detector pixel size in X-direction.",
        },
        "detector_pxsizey": {
            "type": float,
            "default": -1,
            "name": "Detector pixel size Y",
            "choices": None,
            "unit": "um",
            "allow_None": False,
            "tooltip": "The detector pixel size in Y-direction.",
        },
        "detector_dist": {
            "type": float,
            "default": 1,
            "name": "Sample-detector distance",
            "choices": None,
            "unit": "m",
            "allow_None": False,
            "tooltip": "The sample-detector distance.",
        },
        "detector_poni1": {
            "type": float,
            "default": 0,
            "name": "Detector PONI1",
            "choices": None,
            "unit": "m",
            "allow_None": False,
            "tooltip": (
                "The detector PONI1 (point of normal incidence; in y direction). This "
                "is measured in meters from the detector origin."
            ),
        },
        "detector_poni2": {
            "type": float,
            "default": 0,
            "name": "Detector PONI2",
            "choices": None,
            "unit": "m",
            "allow_None": False,
            "tooltip": (
                "The detector PONI2 (point of normal incidence; in x direction). This "
                "is measured in meters from the detector origin."
            ),
        },
        "detector_rot1": {
            "type": float,
            "default": 0,
            "name": "Detector Rot1",
            "choices": None,
            "unit": "rad",
            "allow_None": False,
            "tooltip": 'The detector rotation 1 (lefthanded around the "up"-axis)',
        },
        "detector_rot2": {
            "type": float,
            "default": 0,
            "name": "Detector Rot2",
            "choices": None,
            "unit": "rad",
            "allow_None": False,
            "tooltip": (
                "The detector rotation 2 (pitching the detector; positive direction is "
                "tilting the detector top upstream while keeping the bottom of the "
                "detector stationary."
            ),
        },
        "detector_rot3": {
            "type": float,
            "default": 0,
            "name": "Detector Rot3",
            "choices": None,
            "unit": "rad",
            "allow_None": False,
            "tooltip": (
                "The detector rotation 3 (around the beam axis; right-handed when "
                "looking downstream with the beam.)"
            ),
        },
    }
    | {
        ############################
        # Parameters for scan setup
        ############################
        "scan_dim": {
            "type": int,
            "default": 1,
            "name": "Scan dimension",
            "choices": [1, 2, 3, 4],
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The scan dimensionality. This defines the number of processed "
                "dimensions."
            ),
        },
        "scan_title": {
            "type": str,
            "default": "",
            "name": "Scan name/title",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The scan name or title. This is used exclusively for "
                "reference in result exporters."
            ),
        },
        "scan_base_directory": {
            "type": "Path",
            "default": "",
            "name": "Scan base directory path",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The absolute path of the base directory in which to find this scan. "
                "Note that indivual plugins may automatically discover and use "
                "subdirectories. Please refer to the specific InputPlugin in use for "
                "more information."
            ),
        },
        "scan_name_pattern": {
            "type": "Path",
            "default": "",
            "name": "The scan naming pattern",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The pattern used for naming scan (files9. Use hashes '#' for "
                "wildcards which will be filled in with numbers for the various files. "
                "Note that individual plugins may use this Parameter for either "
                "directory or file names. Please refer to the specific InputPlugin in "
                "use for more information."
            ),
        },
        "scan_start_index": {
            "type": int,
            "default": 0,
            "name": "Starting index",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The starting index offset for the index used to identify data "
                "points in the scan."
            ),
        },
        "scan_index_stepping": {
            "type": int,
            "default": 1,
            "name": "Index stepping",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The stepping of the index. A value of n corresponds to only using "
                "every n-th index. For example, an index stepping of 3 with an offset "
                "of 5 would process the frames 5, 8, 11, 14 etc."
            ),
        },
        "scan_multi_image_handling": {
            "type": str,
            "default": "Average",
            "name": "Multi-image handling",
            "choices": ["Average", "Sum"],
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "Define the handling of images if multiple images were acquired per "
                "scan point. If all individual images should be kept, please set the "
                "scan multiplicity to 1 and add an additional dimension with the "
                "multiplicity to the scan."
            ),
        },
        "scan_multiplicity": {
            "type": int,
            "default": 1,
            "name": "Image multiplicity",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The number of images acquired at each scan point. The default of '1' "
                "corresponds to one image per scan point."
            ),
        },
    }
    | {
        f"scan_label_{_index}": {
            "type": str,
            "default": "",
            "name": f"Name of scan direction {_index}",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                f"The axis name for scan direction {_index}. This information will "
                "only be used for labelling."
            ),
        }
        for _index in range(1, 5)
    }
    | {
        f"n_points_{_index}": {
            "type": int,
            "default": 0,
            "name": f"Number of scan points (dir. {_index})",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": f"The number of scan points in scan direction {_index}.",
        }
        for _index in range(1, 5)
    }
    | {
        f"delta_{_index}": {
            "type": float,
            "default": 1,
            "name": f"Step width in direction {_index}",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": f"The step width between scan points in direction {_index}.",
        }
        for _index in range(1, 5)
    }
    | {
        f"offset_{_index}": {
            "type": float,
            "default": 0,
            "name": f"Offset of direction {_index}",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The coordinate offset of the movement in scan direction "
                f"{_index} (i.e. the counter / motor position for scan step #0)."
            ),
        }
        for _index in range(1, 5)
    }
    | {
        f"unit_{_index}": {
            "type": str,
            "default": "",
            "name": f"Unit of direction {_index}",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": f"The unit of the positions in scan direction {_index}.",
        }
        for _index in range(1, 5)
    }
    | {
        ############################
        # selected scan indices
        ############################
        f"scan_index{_index}": {
            "type": int,
            "default": 0,
            "name": f"Scan dim. {_index} index",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": f"The position index for the scan dimension {_index}.",
        }
        for _index in range(1, 5)
    }
    | {
        "image_num": {
            "type": int,
            "default": 0,
            "name": "Image number",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": "The image number to be processed.",
        },
        ############################
        # global app settings
        ############################
        "mp_n_workers": {
            "type": int,
            "default": 4,
            "name": "Number of MP workers",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The number of multiprocessing workers. Note that this number should "
                "not be set too high for two reasons:\n1. File reading processes "
                "interfere with each other if too many are active at once.\n2. pyFAI "
                "already inherently uses parallelization and you can only gain limited "
                "performance increases for multiple parallel processes."
            ),
        },
        "shared_buffer_size": {
            "type": float,
            "default": 100,
            "name": "Shared buffer size limit",
            "choices": None,
            "unit": "MB",
            "allow_None": False,
            "tooltip": (
                "A shared buffer is used to efficiently transport data between the "
                "main App and multiprocessing Processes. This buffer must be large "
                "enough to store at least one instance of all result data."
            ),
        },
        "shared_buffer_max_n": {
            "type": int,
            "default": 20,
            "name": "Buffer dataframe limit",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The maximum number of datasets in the buffer. A dataset consists of "
                "all results for one frame. For performance reasons, the buffer should "
                "not be too large."
            ),
        },
        "use_global_det_mask": {
            "type": bool,
            "default": True,
            "name": "Use global detector mask",
            "choices": [True, False],
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "Flag to use the global detector mask file and value. If False, no "
                "detector mask will be used."
            ),
        },
        "det_mask": {
            "type": "Path",
            "default": "",
            "name": "Detector mask file",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": "The path to the detector mask file.",
        },
        "det_mask_val": {
            "type": float,
            "default": 0,
            "name": "Detector mask value",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The value to be used for the pixels masked on the detector. Note that "
                "this value will only be used for displaying the images. For pyFAI "
                "integration, the pixels will be fully masked and not be included."
            ),
        },
        "mosaic_border_width": {
            "type": int,
            "default": 0,
            "name": "Mosaic tiling border width",
            "choices": None,
            "unit": "px",
            "allow_None": False,
            "tooltip": (
                "The width of the border inserted between adjacent frames"
                " in the mosaic creation."
            ),
        },
        "mosaic_border_value": {
            "type": float,
            "default": 0,
            "name": "Mosaic border value",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": "The value to be put in the border pixels in mosaics.",
        },
        "mosaic_max_size": {
            "type": float,
            "default": 100,
            "name": "Mosaic maximum size",
            "choices": None,
            "unit": "Mpx",
            "allow_None": False,
            "tooltip": "The maximum size (in megapixels) of mosaic images.",
        },
        "run_type": {
            "type": str,
            "default": "Process in GUI",
            "name": "Run type",
            "choices": ["Process in GUI", "Command line"],
            "unit": "",
            "allow_None": False,
            "tooltip": ("Specify how the processing shall be performed."),
        },
        "plugin_path": {
            "type": str,
            "default": "",
            "name": "Plugin paths",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The paths to all plugin locations. Individual entries are"
                ' separated by a double semicolon ";;".'
            ),
        },
        "plot_update_time": {
            "type": float,
            "default": 1.0,
            "name": "Plot update time",
            "choices": None,
            "allow_None": False,
            "unit": "s",
            "tooltip": (
                "The delay before any plot updates will be processed. This"
                " will prevent multiple frequent update of plots."
            ),
        },
        "histogram_outlier_fraction": {
            "type": float,
            "default": 0.07,
            "name": "Histogram outlier fraction",
            "choices": None,
            "allow_None": False,
            "unit": "",
            "tooltip": (
                "The fraction of pixels which will be ignored when cropping the "
                "histogram for 2d plots. A value of 0.07 will mask all sensor gaps in "
                "the Eiger."
            ),
        },
        "plugin_fit_std_threshold": {
            "type": float,
            "default": 0.25,
            "name": "Fit sigma rejection threshold",
            "choices": None,
            "allow_None": False,
            "unit": "",
            "tooltip": (
                "The threshold to select which fitting points to reject, based on the "
                "normalized standard deviation. Any fit which has a normalized std "
                "which is worse than the threshold will be rejected as failed."
            ),
        },
        ############################
        # global choice settings
        ############################
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
        # pyFAI settings parameters
        ############################
        "rad_npoint": {
            "type": int,
            "default": 1000,
            "name": "Num points radial integration",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The number of bins in radial direction for the pyFAI integration."
            ),
        },
        "rad_unit": {
            "type": str,
            "default": "2theta / deg",
            "name": "Radial unit",
            "choices": ["Q / nm^-1", "Q / A^-1", "2theta / deg", "2theta / rad"],
            "unit": "",
            "allow_None": False,
            "tooltip": "The unit and type of the azimuthal profile.",
        },
        "rad_use_range": {
            "type": int,
            "default": 0,
            "name": "Use radial range",
            "choices": [True, False],
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "Toggle to limit the radial integration range or use the full data "
                "range. If True, boundaries need to be defined in the lower and upper "
                "radial range Parameters."
            ),
        },
        "rad_range_lower": {
            "type": float,
            "default": 0,
            "name": "Radial lower range",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The lower boundary of the radial integration range. This setting is "
                "only used if 'Use radial range' is  True. This value needs to be "
                "given in the unit selected as radial unit."
            ),
        },
        "rad_range_upper": {
            "type": float,
            "default": 0,
            "name": "Radial upper range",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The upper boundary of the radial integration range. This setting is "
                "only used if 'Use radial range' is  True.  This value needs to be "
                "given in the unit selected as radial unit."
            ),
        },
        "azi_npoint": {
            "type": int,
            "default": 1000,
            "name": "Num points azimuthal integration",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The number of bins in azimuthal direction for the pyFAI integration."
            ),
        },
        "azi_unit": {
            "type": str,
            "default": "chi / deg",
            "name": "Azimuthal unit",
            "choices": ["chi / deg", "chi / rad"],
            "unit": "",
            "allow_None": False,
            "tooltip": "The unit and type of the azimuthal profile.",
        },
        "azi_use_range": {
            "type": int,
            "default": 0,
            "name": "Use azimuthal range",
            "choices": [True, False],
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "Toggle to limit the azimuthal integration range or use the full data "
                "range. If True, boundaries need to be defined in the lower and upper "
                "azimuthal range Parameters."
            ),
        },
        "azi_range_lower": {
            "type": float,
            "default": 0,
            "name": "Azimuthal lower range",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The lower boundary of the azimuthal integration range. This setting "
                "is only used if 'Use azimuthal range' is True. This value needs to be "
                "given in the unit selected as azimuthal unit."
            ),
        },
        "azi_range_upper": {
            "type": float,
            "default": 0,
            "name": "Azimuthal upper range",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The upper boundary of the azimuthal integration range. This setting "
                "is only used if 'Use azimuthal range' is True. This value needs to be "
                "given in the unit selected as azimuthal unit."
            ),
        },
        "int_method": {
            "type": str,
            "default": "CSR",
            "name": "PyFAI integration method",
            "choices": [
                "CSR",
                "CSR OpenCL",
                "CSR full",
                "CSR full OpenCL",
                "LUT",
                "LUT OpenCL",
                "LUT full",
                "LUT full OpenCL",
            ],
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The integration method. For a full reference, please"
                " visit the pyfai documentation available at: "
                "https://pyfai.readthedocs.io/"
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
        "directory_path": {
            "type": "Path",
            "default": "",
            "name": "Directory path",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": "The absolute path of the directory to be used.",
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
        ############################
        # Fitting Parameters
        ############################
        "fit_func": {
            "type": str,
            "default": "Gaussian",
            "name": "Fit function",
            "choices": ["Gaussian", "Lorentzian", "Voigt"],
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
            "tooltip": (
                "The order of the background. None corresponds to no background."
            ),
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
        ############################
        # Plugin Parameters
        ############################
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
        ############################
        # Result visualization Parameters
        ############################
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
        ############################
        # Plugin data selection
        ############################
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
)
