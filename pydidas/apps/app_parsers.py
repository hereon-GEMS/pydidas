# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with parsers to parse command line arguments for apps."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['parse_composite_creator_cmdline_arguments']

import argparse

from pydidas.core import get_generic_parameter as generic_param


def parse_composite_creator_cmdline_arguments(caller=None):
    """
    Use argparse to get command line arguments.

    Parameters
    ----------
    caller : object, optional
        If this function is called by a class as method, it requires a single
        argument which corresponds to the instance.

    Returns
    -------
    dict
        A dictionary with the parsed arugments which holds all the entries
        and entered values or  - if missing - the default values.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-first_file', '-f',
                        help=generic_param('first_file').tooltip)
    parser.add_argument('-last_file', '-l',
                        help=generic_param('last_file').tooltip)
    parser.add_argument('-file_stepping', type=int,
                        help=generic_param('file_stepping').tooltip)
    parser.add_argument('-hdf5_key',
                        help=generic_param('hdf5_key').tooltip)
    parser.add_argument('-hdf5_first_image_num', type=int,
                        help=generic_param('hdf5_first_image_num').tooltip)
    parser.add_argument('-hdf5_last_image_num', type=int,
                        help=generic_param('hdf5_last_image_num').tooltip)
    parser.add_argument('-hdf5_stepping', type=int,
                        help=generic_param('hdf5_stepping').tooltip)
    parser.add_argument('--use_bg_file', action='store_true',
                        help=generic_param('use_bg_file').tooltip)
    parser.add_argument('-bg_file',
                        help=generic_param('bg_file').tooltip)
    parser.add_argument('-bg_hdf5_key',
                        help=generic_param('bg_hdf5_key').tooltip)
    parser.add_argument('-bg_hdf5_frame', type=int,
                        help=generic_param('bg_hdf5_frame').tooltip)
    parser.add_argument('-composite_nx', type=int,
                        help=generic_param('composite_nx').tooltip)
    parser.add_argument('-composite_ny', type=int,
                        help=generic_param('composite_ny').tooltip)
    parser.add_argument('--use_roi', action='store_true',
                        help=generic_param('use_roi').tooltip)
    parser.add_argument('-roi_xlow', type=int,
                        help=generic_param('roi_xlow').tooltip)
    parser.add_argument('-roi_xhigh', type=int,
                        help=generic_param('roi_xhigh').tooltip)
    parser.add_argument('-roi_ylow', type=int,
                        help=generic_param('roi_ylow').tooltip)
    parser.add_argument('-roi_yhigh', type=int,
                        help=generic_param('roi_yhigh').tooltip)
    parser.add_argument('--use_thresholds', action='store_true',
                        help=generic_param('use_thresholds').tooltip)
    parser.add_argument('-threshold_low', type=int,
                        help=generic_param('threshold_low').tooltip)
    parser.add_argument('-threshold_high', type=int,
                        help=generic_param('threshold_high').tooltip)
    parser.add_argument('-binning', type=int,
                        help=generic_param('binning').tooltip)
    parser.add_argument('-output_fname',
                        help=('The name used for saving the composite image '
                              '(in numpy file format). An empty Path will '
                              'default to no automatic image saving. The '
                              'default is Path().'))
    _args = dict(vars(parser.parse_args()))
    # store None for keyword arguments which were not selected:
    for _key in ['use_roi', 'use_thresholds', 'use_bg_file']:
        _args[_key] = _args[_key] if _args[_key] else None
    return _args


def parse_execute_workflow_cmdline_arguments(caller):
    """
    Use argparse to get command line arguments.

    Parameters
    ----------
    caller : object, optional
        If this function is called by a class as method, it requires a single
        argument which corresponds to the instance.

    Returns
    -------
    dict
        A dictionary with the parsed arugments which holds all the entries
        and entered values or  - if missing - the default values.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--autosave', action='store_true',
                        help=generic_param('autosave_results').tooltip)
    parser.add_argument('-autosave_dir', '-d',
                        help=generic_param('autosave_dir').tooltip)
    parser.add_argument('-autosave_format', '-f',
                        help=generic_param('autosave_format').tooltip)
    _args = dict(vars(parser.parse_args()))
    # store False for keyword arguments which were not selected:
    for _key in ['autosave']:
        _args[_key] = bool(_args[_key])
    return _args
