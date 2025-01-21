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
ExecuteWorkflowAppp.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["execute_workflow_app_parser"]


import argparse
from typing import Union

from pydidas.core.generic_params import GENERIC_PARAMS_METADATA as PARAMS


def execute_workflow_app_parser(caller: Union[object, None] = None) -> dict:
    """
    Parse the command line arguments for the ExecuteWorkflowApp.

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
        "--autosave", action="store_true", help=PARAMS["autosave_results"]["tooltip"]
    )
    parser.add_argument(
        "-autosave_directory", "-d", help=PARAMS["autosave_directory"]["tooltip"]
    )
    parser.add_argument(
        "-autosave_format", "-f", help=PARAMS["autosave_format"]["tooltip"]
    )
    _options, _unknown = parser.parse_known_args()
    _args = dict(vars(_options))
    # store the autosave entry for the autosave_results Parameter
    _args["autosave_results"] = True if _args.pop("autosave") else None
    return _args
