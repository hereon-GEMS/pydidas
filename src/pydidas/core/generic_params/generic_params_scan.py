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
The generic_params_scan module holds all the required data to create generic
Parameters for the scan context.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_SCAN"]


GENERIC_PARAMS_SCAN = (
    {
        "scan_dim": {
            "type": int,
            "default": 1,
            "name": "Scan dimensionality",
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
            "name": "Scan base directory",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The absolute path of the base directory in which to find this scan. "
                "Note that individual plugins may automatically discover and use "
                "subdirectories. Please refer to the specific InputPlugin in use for "
                "more information."
            ),
        },
        "scan_name_pattern": {
            "type": "Path",
            "default": "",
            "name": "The scan/file naming pattern",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The pattern used for naming scan (files). Use hashes '#' for "
                "wildcards which will be filled in with numbers for the various files. "
                "Note that individual plugins may use this Parameter for either "
                "directory or file names. Please refer to the specific InputPlugin in "
                "use for more information."
            ),
        },
        "pattern_number_offset": {
            "type": int,
            "default": 0,
            "name": "First pattern number",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The first number in the pattern to be used in processing. This number "
                "will be applied as offset in the scan naming pattern to identify the "
                "respective filename for scan points. For example, if the first file "
                "is named `scan_0001.h5`, the offset should be set to 1."
            ),
        },
        "pattern_number_delta": {
            "type": int,
            "default": 1,
            "name": "Index stepping of pattern",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The difference in the index between two consecutive pattern points. "
                "A value of 1 would mean that each index is processed in the pattern "
                "whereas a value of n would mean that only every n-th index (e.g. "
                "filename) is processed.For example, a value of 3 would process the "
                "files with the names `scan_0000.h5`, `scan_0003.h5`, `scan_0006.h5` "
                "etc."
            ),
        },
        "frame_indices_per_scan_point": {
            "type": int,
            "default": 1,
            "name": "Frame index stepping per scan point",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The number of frame indices (in frames) between two scan points. "
                "A value of 1 would increment the image index by 1 for each scan "
                "point whereas a value of n corresponds to only using every n-th "
                "index. For example, a value of 3 frame indices per scan point "
                "process the frame 0 for scan point 0, frame 3 for scan point 1 etc."
                "Please note that the index stepping refers to the frames, not the "
                "filenames. In the case of container files (e.g. hdf5), the index "
                "stepping will skip process every n-th frame, not every n-th file."
            ),
        },
        "scan_multi_frame_handling": {
            "type": str,
            "default": "Average",
            "name": "Multi-frame handling",
            "choices": ["Average", "Sum", "Maximum", "Stack"],
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "Define the handling of images if multiple images were acquired per "
                "scan point. If all individual images should be kept, please set the "
                "scan multiplicity to 1 and add an additional dimension with the "
                "multiplicity to the scan."
            ),
        },
        "scan_frames_per_point": {
            "type": int,
            "default": 1,
            "name": "Frames to process per scan point",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "The number of frames to process at *each* scan point. The default of "
                "`1` corresponds to one image per scan point. Please note that the "
                "value for the  "
                "points. If this setting is used for `averaging` images, please reduce "
                "the number of scan points correspondingly."
            ),
        },
    }
    | {
        f"scan_dim{_index}_label": {
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
        for _index in range(4)
    }
    | {
        f"scan_dim{_index}_n_points": {
            "type": int,
            "default": 0,
            "name": f"Number of scan points (dir. {_index})",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                f"The total number of scan points in scan direction {_index}. The "
                "number of points is one higher than the number of intervals."
            ),
        }
        for _index in range(4)
    }
    | {
        f"scan_dim{_index}_delta": {
            "type": float,
            "default": 1,
            "name": f"Step width in direction {_index}",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": f"The step width between scan points in direction {_index}.",
        }
        for _index in range(4)
    }
    | {
        f"scan_dim{_index}_offset": {
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
        for _index in range(4)
    }
    | {
        f"scan_dim{_index}_unit": {
            "type": str,
            "default": "",
            "name": f"Unit of direction {_index}",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": f"The unit of the positions in scan direction {_index}.",
        }
        for _index in range(4)
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
        for _index in range(0, 4)
    }
)
