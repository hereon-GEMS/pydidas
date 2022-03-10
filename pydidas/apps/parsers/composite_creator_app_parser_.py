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
Module with parsers to parse command line arguments for the
CompositeCreatorApp.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['composite_creator_app_parser']

import argparse

from ...core.constants import GENERIC_PARAM_DESCRIPTION as PARAMS


def composite_creator_app_parser(caller=None):
    """
    Parse the command line arguments for the CompositeCreatorApp.

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
                        help=PARAMS['first_file']['tooltip'])
    parser.add_argument('-last_file', '-l',
                        help=PARAMS['last_file']['tooltip'])
    parser.add_argument('-file_stepping', type=int,
                        help=PARAMS['file_stepping']['tooltip'])
    parser.add_argument('-hdf5_key',
                        help=PARAMS['hdf5_key']['tooltip'])
    parser.add_argument('-hdf5_first_image_num', type=int,
                        help=PARAMS['hdf5_first_image_num']['tooltip'])
    parser.add_argument('-hdf5_last_image_num', type=int,
                        help=PARAMS['hdf5_last_image_num']['tooltip'])
    parser.add_argument('-hdf5_stepping', type=int,
                        help=PARAMS['hdf5_stepping']['tooltip'])
    parser.add_argument('--use_bg_file', action='store_true',
                        help=PARAMS['use_bg_file']['tooltip'])
    parser.add_argument('-bg_file',
                        help=PARAMS['bg_file']['tooltip'])
    parser.add_argument('-bg_hdf5_key',
                        help=PARAMS['bg_hdf5_key']['tooltip'])
    parser.add_argument('-bg_hdf5_frame', type=int,
                        help=PARAMS['bg_hdf5_frame']['tooltip'])
    parser.add_argument('-composite_nx', type=int,
                        help=PARAMS['composite_nx']['tooltip'])
    parser.add_argument('-composite_ny', type=int,
                        help=PARAMS['composite_ny']['tooltip'])
    parser.add_argument('--do_not_use_detmask', action='store_true',
                        help='Do not use the global detector mask.')
    parser.add_argument('--use_roi', action='store_true',
                        help=PARAMS['use_roi']['tooltip'])
    parser.add_argument('-roi_xlow', type=int,
                        help=PARAMS['roi_xlow']['tooltip'])
    parser.add_argument('-roi_xhigh', type=int,
                        help=PARAMS['roi_xhigh']['tooltip'])
    parser.add_argument('-roi_ylow', type=int,
                        help=PARAMS['roi_ylow']['tooltip'])
    parser.add_argument('-roi_yhigh', type=int,
                        help=PARAMS['roi_yhigh']['tooltip'])
    parser.add_argument('--use_thresholds', action='store_true',
                        help=PARAMS['use_thresholds']['tooltip'])
    parser.add_argument('-threshold_low', type=int,
                        help=PARAMS['threshold_low']['tooltip'])
    parser.add_argument('-threshold_high', type=int,
                        help=PARAMS['threshold_high']['tooltip'])
    parser.add_argument('-binning', type=int,
                        help=PARAMS['binning']['tooltip'])
    parser.add_argument('-output_fname',
                        help=('The name used for saving the composite image '
                              '(in numpy file format). An empty Path will '
                              'default to no automatic image saving. The '
                              'default is Path().'))
    _args = dict(vars(parser.parse_args()))
    # store None for keyword arguments which were not selected:
    for _key in ['use_roi', 'use_thresholds', 'use_bg_file']:
        _val = _args[_key]
        _args[_key] = True if _val else None
    _args['use_global_det_mask'] = (False if _args.pop('do_not_use_detmask')
                                    else None)
    return _args
