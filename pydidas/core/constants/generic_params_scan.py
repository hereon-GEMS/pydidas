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
The generic_params_scan module holds all the required data to create generic
Parameters for the scan context.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["GENERIC_PARAMS_SCAN"]


GENERIC_PARAMS_SCAN = (
    {
        "scan_dim": {
            "type": int,
            "default": 1,
            "name": "Scan dimensionsionality",
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
                "The pattern used for naming scan (files). Use hashes '#' for "
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
            "tooltip": f"The number of scan points in scan direction {_index}.",
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
        for _index in range(1, 5)
    }
)
