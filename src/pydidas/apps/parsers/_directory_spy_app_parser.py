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
Module with the parser to parse command line arguments for the
DirectorySpyApp.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["directory_spy_app_parser"]


import argparse
from typing import Union

from pydidas.core.generic_params import GENERIC_PARAMS_METADATA as PARAMS


def directory_spy_app_parser(caller: Union[object, None] = None) -> dict:
    """
    Parse the command line arguments for the DirectorySpyApp.

    Parameters
    ----------
    caller : object, optional
        If this function is called by a class as method, it requires a single
        argument which corresponds to the instance.

    Returns
    -------
    dict
        A dictionary with the parsed arugments which holds all the entries
        and entered values or - if missing - the default values.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scan_for_all", action="store_true", help=PARAMS["scan_for_all"]["tooltip"]
    )
    parser.add_argument(
        "-filename_pattern", "-f", help=PARAMS["filename_pattern"]["tooltip"]
    )
    parser.add_argument(
        "-directory_path", "-d", help=PARAMS["directory_path"]["tooltip"]
    )
    parser.add_argument("-hdf5_key", help=PARAMS["hdf5_key"]["tooltip"])
    parser.add_argument(
        "--do_not_use_detmask",
        action="store_true",
        help="Do not use the global detector mask.",
    )
    parser.add_argument(
        "--use_bg_file", action="store_true", help=PARAMS["use_bg_file"]["tooltip"]
    )
    parser.add_argument("-bg_file", help=PARAMS["bg_file"]["tooltip"])
    parser.add_argument("-bg_hdf5_key", help=PARAMS["bg_hdf5_key"]["tooltip"])
    parser.add_argument("-bg_hdf5_frame", help=PARAMS["bg_hdf5_frame"]["tooltip"])

    _options, _unknown = parser.parse_known_args()
    _args = dict(vars(_options))
    # store False for keyword arguments which were not selected:
    for _key in ["scan_for_all", "use_bg_file"]:
        _val = _args[_key]
        _args[_key] = True if _val else None
    _args["use_global_det_mask"] = False if _args.pop("do_not_use_detmask") else None
    return _args
